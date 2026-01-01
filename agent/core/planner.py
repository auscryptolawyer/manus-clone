"""Task planner - breaks user tasks into steps using Claude."""

from anthropic import AsyncAnthropic
from loguru import logger

from api.schemas import TaskPlan, TaskStep


PLANNER_SYSTEM_PROMPT = """You are a task planner for a browser automation agent. Given a user's task, break it down into clear, sequential steps that can be executed by a web browser.

Guidelines:
- Keep steps simple and atomic
- Each step should be a single action or small group of related actions
- Be specific about what needs to happen
- Consider common web patterns (search, login, navigation, forms)
- Account for page loads and dynamic content
- 3-7 steps is usually appropriate

Output format: Return ONLY a JSON array of step descriptions, nothing else.

Example:
Task: "Find the cheapest flight from Brisbane to Tokyo in March"
["Navigate to a flight search website", "Enter Brisbane as origin and Tokyo as destination", "Set travel dates to March", "Search for flights", "Sort or filter by price", "Extract the cheapest flight details"]
"""


class TaskPlanner:
    """Breaks high-level tasks into executable steps."""

    def __init__(self, client: AsyncAnthropic, model: str = "claude-sonnet-4-20250514"):
        self.client = client
        self.model = model

    async def create_plan(self, task: str) -> TaskPlan:
        """Create a plan for the given task."""
        logger.info(f"Creating plan for: {task}")

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=PLANNER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": task}]
        )

        # Parse the response
        content = response.content[0].text.strip()

        # Extract JSON array from response
        try:
            import json
            # Handle potential markdown code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            step_descriptions = json.loads(content)

            steps = [TaskStep(description=desc) for desc in step_descriptions]
            plan = TaskPlan(task=task, steps=steps)

            logger.info(f"Created plan with {len(steps)} steps")
            return plan

        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Failed to parse plan, using single step: {e}")
            # Fallback: single step with the original task
            return TaskPlan(
                task=task,
                steps=[TaskStep(description=f"Complete the task: {task}")]
            )
