"""Agent executor - the observe-think-act loop."""

from typing import Any, Callable, Awaitable
from dataclasses import dataclass, field
from anthropic import AsyncAnthropic
from loguru import logger

from agent.browser.driver import BrowserDriver
from agent.browser.actions import BrowserActions
from agent.browser.observer import PageObserver
from agent.core.tools import get_tool_definitions
from api.schemas import PageState, ActionResult, TaskPlan


@dataclass
class ActionRecord:
    """Record of an action taken."""
    tool: str
    params: dict
    result: ActionResult
    page_state_after: PageState | None = None


@dataclass
class AgentState:
    """Current state of the agent."""
    task: str
    plan: TaskPlan | None = None
    current_step: int = 0
    action_history: list[ActionRecord] = field(default_factory=list)
    completed: bool = False
    failed: bool = False
    result: str | None = None
    error: str | None = None
    waiting_for_user: bool = False
    user_question: str | None = None


# Type alias for event callback
EventCallback = Callable[[str, dict], Awaitable[None]]


EXECUTOR_SYSTEM_PROMPT = """You are a browser automation agent. You control a web browser to complete tasks for the user.

You will receive:
1. The current task and plan
2. A screenshot of the current page (in the next message)
3. A list of interactive elements on the page, each with a numeric ID
4. Visible text from the page
5. History of recent actions

Based on this information, decide what action to take next using one of the available tools.

Key principles:
- Always wait for pages to load before interacting
- Use element IDs to click or type into specific elements
- If an element isn't visible, try scrolling
- If stuck, re-assess the situation and try a different approach
- Ask the user if you encounter CAPTCHAs, login requirements, or ambiguous situations
- Complete the task and provide a clear result when done

Think step by step about what you see and what action will progress toward the goal."""


class AgentExecutor:
    """Executes browser automation tasks using Claude."""

    def __init__(
        self,
        anthropic_client: AsyncAnthropic,
        browser: BrowserDriver,
        model: str = "claude-sonnet-4-20250514",
        max_steps: int = 50,
        step_timeout: int = 60,
    ):
        self.client = anthropic_client
        self.browser = browser
        self.model = model
        self.max_steps = max_steps
        self.step_timeout = step_timeout
        self.state: AgentState | None = None
        self._event_callback: EventCallback | None = None

    def set_event_callback(self, callback: EventCallback) -> None:
        """Set callback for streaming events to the frontend."""
        self._event_callback = callback

    async def _emit(self, event_type: str, data: dict) -> None:
        """Emit an event to the frontend."""
        if self._event_callback:
            await self._event_callback(event_type, data)

    async def run(self, task: str, plan: TaskPlan) -> AgentState:
        """Run the agent to complete a task."""
        logger.info(f"Starting task execution: {task}")

        self.state = AgentState(task=task, plan=plan)
        observer = PageObserver(self.browser.page)
        actions = BrowserActions(self.browser.page, timeout=self.step_timeout * 1000)

        step_count = 0

        while not self.state.completed and not self.state.failed:
            if step_count >= self.max_steps:
                self.state.failed = True
                self.state.error = f"Exceeded maximum steps ({self.max_steps})"
                await self._emit("error", {"message": self.state.error})
                break

            step_count += 1
            logger.info(f"Step {step_count}/{self.max_steps}")

            # 1. Observe
            page_state = await observer.observe()
            await self._emit("observation", {
                "screenshot": page_state.screenshot_base64,
                "elements": [e.model_dump() for e in page_state.interactive_elements],
                "url": page_state.url,
                "title": page_state.title,
            })

            # 2. Think (ask Claude what to do)
            tool_call = await self._decide_action(page_state)

            if not tool_call:
                logger.warning("No tool call from Claude")
                continue

            tool_name = tool_call.get("name", "")
            tool_params = tool_call.get("params", {})

            await self._emit("action", {"tool": tool_name, "params": tool_params})

            # 3. Act
            result = await self._execute_tool(
                tool_name, tool_params, actions, observer, page_state
            )

            # 4. Record
            self.state.action_history.append(ActionRecord(
                tool=tool_name,
                params=tool_params,
                result=result,
            ))

            # Keep only recent history to manage context
            if len(self.state.action_history) > 20:
                self.state.action_history = self.state.action_history[-20:]

        logger.info(f"Task {'completed' if self.state.completed else 'failed'}")
        return self.state

    async def _decide_action(self, page_state: PageState) -> dict | None:
        """Ask Claude to decide the next action."""
        # Build context message
        elements_text = self._format_elements(page_state.interactive_elements)
        history_text = self._format_history()

        current_step_desc = ""
        if self.state and self.state.plan and self.state.plan.steps:
            if self.state.current_step < len(self.state.plan.steps):
                current_step_desc = self.state.plan.steps[self.state.current_step].description

        user_content = [
            {
                "type": "text",
                "text": f"""**Task:** {self.state.task if self.state else 'Unknown'}

**Current step:** {current_step_desc or 'Execute the task'}

**Current page:** {page_state.url}
**Page title:** {page_state.title}

**Interactive elements on page:**
{elements_text}

**Visible text excerpt:**
{page_state.visible_text[:1500] if page_state.visible_text else '(none)'}

**Recent actions:**
{history_text}

Analyze the page and decide what action to take next. Use a tool to perform an action."""
            }
        ]

        # Add screenshot if available
        if page_state.screenshot_base64:
            user_content.insert(0, {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": page_state.screenshot_base64,
                }
            })

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=EXECUTOR_SYSTEM_PROMPT,
                tools=get_tool_definitions(),
                messages=[{"role": "user", "content": user_content}]
            )

            # Extract tool use from response
            for block in response.content:
                if block.type == "tool_use":
                    return {"name": block.name, "params": block.input}

            # If no tool call, log the text response
            for block in response.content:
                if block.type == "text":
                    logger.debug(f"Claude response (no tool): {block.text[:200]}")

            return None

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None

    async def _execute_tool(
        self,
        tool_name: str,
        params: dict,
        actions: BrowserActions,
        observer: PageObserver,
        page_state: PageState,
    ) -> ActionResult:
        """Execute a tool and return the result."""
        elements_dict = observer.elements_to_dict(page_state.interactive_elements)

        try:
            if tool_name == "navigate":
                return await actions.navigate(params["url"])

            elif tool_name == "click":
                return await actions.click_element_id(params["element_id"], elements_dict)

            elif tool_name == "type":
                element_id = params.get("element_id")
                clear_first = params.get("clear_first", True)
                if element_id:
                    return await actions.type_element_id(
                        element_id, params["text"], elements_dict, clear_first
                    )
                else:
                    return await actions.type_text(params["text"], clear_first=clear_first)

            elif tool_name == "scroll":
                direction = params.get("direction", "down")
                amount = params.get("amount", "half_page")
                return await actions.scroll(direction, amount)

            elif tool_name == "wait":
                seconds = min(params.get("seconds", 1), 30)
                for_element = params.get("for_element")
                return await actions.wait(seconds, for_element)

            elif tool_name == "press_key":
                return await actions.press_key(params["key"])

            elif tool_name == "extract":
                # For extraction, we return the current visible text
                # Claude will interpret it based on the "what" parameter
                return ActionResult(success=True, data=page_state.visible_text)

            elif tool_name == "complete":
                if self.state:
                    self.state.completed = True
                    self.state.result = params["result"]
                await self._emit("complete", {"result": params["result"]})
                return ActionResult(success=True, data=params["result"])

            elif tool_name == "fail":
                if self.state:
                    self.state.failed = True
                    self.state.error = params["reason"]
                await self._emit("error", {"message": params["reason"]})
                return ActionResult(success=False, error=params["reason"])

            elif tool_name == "ask_user":
                if self.state:
                    self.state.waiting_for_user = True
                    self.state.user_question = params["question"]
                await self._emit("ask_user", {"question": params["question"]})
                return ActionResult(success=True, data="Waiting for user response")

            else:
                logger.warning(f"Unknown tool: {tool_name}")
                return ActionResult(success=False, error=f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return ActionResult(success=False, error=str(e))

    def _format_elements(self, elements: list) -> str:
        """Format elements for Claude context."""
        if not elements:
            return "(no interactive elements found)"

        lines = []
        for el in elements[:50]:  # Limit to 50 for context management
            el_info = f"[{el.id}] {el.type}"
            if el.text:
                el_info += f": \"{el.text[:60]}{'...' if len(el.text) > 60 else ''}\""
            if el.placeholder:
                el_info += f" (placeholder: {el.placeholder})"
            if el.href:
                el_info += f" -> {el.href[:50]}{'...' if len(el.href) > 50 else ''}"
            lines.append(el_info)

        return "\n".join(lines)

    def _format_history(self) -> str:
        """Format action history for Claude context."""
        if not self.state or not self.state.action_history:
            return "(no previous actions)"

        lines = []
        for record in self.state.action_history[-10:]:  # Last 10 actions
            status = "OK" if record.result.success else f"FAILED: {record.result.error}"
            lines.append(f"- {record.tool}({record.params}) -> {status}")

        return "\n".join(lines)

    async def handle_user_message(self, message: str) -> None:
        """Handle a user message during execution."""
        if self.state and self.state.waiting_for_user:
            self.state.waiting_for_user = False
            self.state.user_question = None
            # Add user response to history context
            self.state.action_history.append(ActionRecord(
                tool="user_response",
                params={"message": message},
                result=ActionResult(success=True, data=message),
            ))
