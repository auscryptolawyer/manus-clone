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
from config import Settings


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connection: WebSocket | None = None
        self.agent_task: asyncio.Task | None = None
        self.browser: BrowserDriver | None = None
        self.executor: AgentExecutor | None = None
        self._cancel_requested = False

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
            await self._start_task(data.get("task", ""), settings)
        elif msg_type == "cancel":
            await self._cancel_task()
        elif msg_type == "user_message":
            await self._handle_user_message(data.get("content", ""))
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    async def _start_task(self, task: str, settings: Settings) -> None:
        """Start a new automation task."""
        if not task:
            await self.send_message({"type": "error", "message": "No task provided"})
            return

        if self.agent_task and not self.agent_task.done():
            await self.send_message({"type": "error", "message": "Task already running"})
            return

        logger.info(f"Starting task: {task}")
        self._cancel_requested = False

        # Run task in background
        self.agent_task = asyncio.create_task(self._run_task(task, settings))

    async def _run_task(self, task: str, settings: Settings) -> None:
        """Execute the automation task."""
        try:
            await self.send_message({"type": "status", "status": "starting"})

            # Initialize Anthropic client
            client = AsyncAnthropic(api_key=settings.anthropic_api_key)

            # Launch browser
            self.browser = BrowserDriver(headless=settings.browser_headless)
            await self.browser.launch()
            await self.send_message({"type": "status", "status": "browser_ready"})

            # Create plan
            await self.send_message({"type": "status", "status": "planning"})
            planner = TaskPlanner(client)
            plan = await planner.create_plan(task)

            step_descriptions = [s.description for s in plan.steps]
            await self.send_message({"type": "plan", "steps": step_descriptions})

            # Execute
            await self.send_message({"type": "status", "status": "executing"})

            self.executor = AgentExecutor(
                anthropic_client=client,
                browser=self.browser,
                max_steps=settings.max_steps_per_task,
                step_timeout=settings.step_timeout_seconds,
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
