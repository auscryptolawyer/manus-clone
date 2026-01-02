"""WebSocket connection handler for real-time updates."""

import json
import asyncio
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from anthropic import AsyncAnthropic

from agent.browser.driver import BrowserDriver
from agent.core.planner import TaskPlanner
from agent.core.executor import AgentExecutor
from api.schemas import TaskPlan
from config import Settings


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connection: WebSocket | None = None
        self.agent_task: asyncio.Task | None = None
        self.browser: BrowserDriver | None = None
        self.executor: AgentExecutor | None = None
        self._cancel_requested = False
        # Plan confirmation state
        self._pending_task: str | None = None
        self._pending_plan: TaskPlan | None = None
        self._anthropic_client: AsyncAnthropic | None = None
        self._settings: Settings | None = None

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()

        # Only one connection at a time
        if self.active_connection:
            await self.active_connection.close()

        self.active_connection = websocket
        logger.info("WebSocket connected")

    def disconnect(self) -> None:
        """Handle WebSocket disconnection."""
        self.active_connection = None
        self._pending_task = None
        self._pending_plan = None
        logger.info("WebSocket disconnected")

    async def send_message(self, message: dict) -> None:
        """Send a message to the connected client."""
        if self.active_connection:
            try:
                await self.active_connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")

    async def handle_message(self, data: dict, settings: Settings) -> None:
        """Handle an incoming message from the client."""
        msg_type = data.get("type")

        if msg_type == "start_task":
            await self._create_plan(data.get("task", ""), settings)
        elif msg_type == "confirm_plan":
            await self._execute_confirmed_plan()
        elif msg_type == "reject_plan":
            await self._reject_plan()
        elif msg_type == "cancel":
            await self._cancel_task()
        elif msg_type == "user_message":
            await self._handle_user_message(data.get("content", ""))
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    async def _create_plan(self, task: str, settings: Settings) -> None:
        """Create a plan and wait for user confirmation."""
        if not task:
            await self.send_message({"type": "error", "message": "No task provided"})
            return

        if self.agent_task and not self.agent_task.done():
            await self.send_message({"type": "error", "message": "Task already running"})
            return

        logger.info(f"Creating plan for task: {task}")
        self._settings = settings

        try:
            await self.send_message({"type": "status", "status": "planning"})

            # Initialize Anthropic client
            self._anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

            # Create plan
            planner = TaskPlanner(self._anthropic_client)
            plan = await planner.create_plan(task)

            # Store pending task and plan
            self._pending_task = task
            self._pending_plan = plan

            # Send plan for confirmation
            step_descriptions = [s.description for s in plan.steps]
            await self.send_message({
                "type": "plan_pending",
                "task": task,
                "steps": step_descriptions,
                "message": "Please review the plan and confirm to proceed."
            })

            await self.send_message({"type": "status", "status": "awaiting_confirmation"})

        except Exception as e:
            logger.error(f"Planning error: {e}")
            await self.send_message({"type": "error", "message": str(e)})
            await self.send_message({"type": "status", "status": "idle"})

    async def _execute_confirmed_plan(self) -> None:
        """Execute the confirmed plan."""
        if not self._pending_task or not self._pending_plan:
            await self.send_message({"type": "error", "message": "No pending plan to execute"})
            return

        task = self._pending_task
        plan = self._pending_plan
        self._pending_task = None
        self._pending_plan = None
        self._cancel_requested = False

        # Run task in background
        self.agent_task = asyncio.create_task(self._run_task(task, plan))

    async def _reject_plan(self) -> None:
        """Reject the pending plan."""
        self._pending_task = None
        self._pending_plan = None
        await self.send_message({"type": "status", "status": "idle"})
        await self.send_message({"type": "plan_rejected", "message": "Plan rejected. You can try a different task."})

    async def _run_task(self, task: str, plan: TaskPlan) -> None:
        """Execute the automation task."""
        try:
            await self.send_message({"type": "status", "status": "starting"})

            # Send confirmed plan
            step_descriptions = [s.description for s in plan.steps]
            await self.send_message({"type": "plan", "steps": step_descriptions})

            # Launch browser
            self.browser = BrowserDriver(headless=self._settings.browser_headless)
            await self.browser.launch()
            await self.send_message({"type": "status", "status": "browser_ready"})

            # Execute
            await self.send_message({"type": "status", "status": "executing"})

            self.executor = AgentExecutor(
                anthropic_client=self._anthropic_client,
                browser=self.browser,
                max_steps=self._settings.max_steps_per_task,
                step_timeout=self._settings.step_timeout_seconds,
            )
            self.executor.set_event_callback(self._agent_event_callback)

            state = await self.executor.run(task, plan)

            if state.completed:
                await self.send_message({
                    "type": "complete",
                    "result": state.result or "Task completed"
                })
            elif state.failed:
                await self.send_message({
                    "type": "error",
                    "message": state.error or "Task failed"
                })

        except asyncio.CancelledError:
            logger.info("Task cancelled")
            await self.send_message({"type": "status", "status": "cancelled"})
        except Exception as e:
            logger.error(f"Task error: {e}")
            await self.send_message({"type": "error", "message": str(e)})
        finally:
            # Cleanup
            if self.browser:
                await self.browser.close()
                self.browser = None
            self.executor = None
            await self.send_message({"type": "status", "status": "idle"})

    async def _agent_event_callback(self, event_type: str, data: dict) -> None:
        """Callback for agent events."""
        await self.send_message({"type": event_type, **data})

    async def _cancel_task(self) -> None:
        """Cancel the running task."""
        # Also cancel pending plans
        if self._pending_task:
            self._pending_task = None
            self._pending_plan = None
            await self.send_message({"type": "status", "status": "idle"})
            return

        self._cancel_requested = True
        if self.agent_task and not self.agent_task.done():
            self.agent_task.cancel()
            logger.info("Task cancellation requested")
            await self.send_message({"type": "status", "status": "cancelling"})

    async def _handle_user_message(self, content: str) -> None:
        """Handle a user message during task execution."""
        if self.executor:
            await self.executor.handle_user_message(content)
        else:
            logger.warning("No executor to handle user message")


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, settings: Settings) -> None:
    """WebSocket endpoint handler."""
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(data, settings)
    except WebSocketDisconnect:
        manager.disconnect()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect()
