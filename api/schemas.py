"""Pydantic models for API data structures."""

from typing import Any
from pydantic import BaseModel, Field


# --- Page State Models ---

class Element(BaseModel):
    """An interactive element on the page."""
    id: int = Field(description="Numeric ID for referencing this element")
    type: str = Field(description="Element type: button, link, input, select, etc.")
    text: str = Field(default="", description="Visible text content")
    placeholder: str | None = Field(default=None, description="Placeholder text for inputs")
    href: str | None = Field(default=None, description="Link URL if applicable")
    selector: str = Field(description="CSS selector to locate this element")


class PageState(BaseModel):
    """Current state of the browser page."""
    url: str
    title: str
    interactive_elements: list[Element] = Field(default_factory=list)
    visible_text: str = Field(default="", description="Truncated visible text summary")
    screenshot_base64: str = Field(default="")
    error: str | None = None


# --- Action Models ---

class ActionResult(BaseModel):
    """Result of a browser action."""
    success: bool
    error: str | None = None
    data: Any = None


# --- WebSocket Message Models ---

class StartTaskMessage(BaseModel):
    """Client request to start a task."""
    type: str = "start_task"
    task: str


class CancelMessage(BaseModel):
    """Client request to cancel current task."""
    type: str = "cancel"


class UserMessage(BaseModel):
    """Client message during task execution."""
    type: str = "user_message"
    content: str


class StatusUpdate(BaseModel):
    """Server status update."""
    type: str = "status"
    status: str  # planning, executing, paused, complete, error


class PlanUpdate(BaseModel):
    """Server plan announcement."""
    type: str = "plan"
    steps: list[str]


class StepStartUpdate(BaseModel):
    """Server step start notification."""
    type: str = "step_start"
    step: int
    description: str


class ObservationUpdate(BaseModel):
    """Server observation with page state."""
    type: str = "observation"
    screenshot: str
    elements: list[Element]
    url: str
    title: str


class ActionUpdate(BaseModel):
    """Server action notification."""
    type: str = "action"
    tool: str
    params: dict[str, Any]


class StepCompleteUpdate(BaseModel):
    """Server step completion notification."""
    type: str = "step_complete"
    step: int


class CompleteUpdate(BaseModel):
    """Server task completion."""
    type: str = "complete"
    result: str


class ErrorUpdate(BaseModel):
    """Server error notification."""
    type: str = "error"
    message: str


# --- Task Models ---

class TaskStep(BaseModel):
    """A step in the task plan."""
    description: str
    complete: bool = False


class TaskPlan(BaseModel):
    """A plan for completing a task."""
    task: str
    steps: list[TaskStep]
