"""Tool definitions for Claude API."""

TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate to a URL. Use this to go to a specific webpage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to navigate to (must include http:// or https://)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "click",
        "description": "Click an interactive element by its ID number from the element list.",
        "input_schema": {
            "type": "object",
            "properties": {
                "element_id": {
                    "type": "integer",
                    "description": "The numeric ID of the element to click"
                }
            },
            "required": ["element_id"]
        }
    },
    {
        "name": "type",
        "description": "Type text into an input field. Can target a specific element or type into the currently focused element.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to type"
                },
                "element_id": {
                    "type": "integer",
                    "description": "Optional: The numeric ID of the element to type into. If not provided, types into the focused element."
                },
                "clear_first": {
                    "type": "boolean",
                    "description": "Whether to clear existing text before typing. Default: true"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "scroll",
        "description": "Scroll the page up or down.",
        "input_schema": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["up", "down"],
                    "description": "Direction to scroll"
                },
                "amount": {
                    "type": "string",
                    "enum": ["small", "half_page", "full_page"],
                    "description": "How much to scroll. Default: half_page"
                }
            },
            "required": ["direction"]
        }
    },
    {
        "name": "wait",
        "description": "Wait for the page to load or for a specific element to appear.",
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "number",
                    "description": "Number of seconds to wait (1-30)"
                },
                "for_element": {
                    "type": "string",
                    "description": "Optional: CSS selector of element to wait for"
                }
            },
            "required": ["seconds"]
        }
    },
    {
        "name": "press_key",
        "description": "Press a keyboard key (Enter, Tab, Escape, etc.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key to press: Enter, Tab, Escape, ArrowUp, ArrowDown, Backspace, etc."
                }
            },
            "required": ["key"]
        }
    },
    {
        "name": "extract",
        "description": "Extract specific information from the current page. Describe what data you want to extract.",
        "input_schema": {
            "type": "object",
            "properties": {
                "what": {
                    "type": "string",
                    "description": "Description of what information to extract from the page"
                }
            },
            "required": ["what"]
        }
    },
    {
        "name": "complete",
        "description": "Mark the task as successfully completed and provide the final result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "The final result or answer to return to the user"
                }
            },
            "required": ["result"]
        }
    },
    {
        "name": "fail",
        "description": "Mark the task as failed when it cannot be completed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Explanation of why the task could not be completed"
                }
            },
            "required": ["reason"]
        }
    },
    {
        "name": "ask_user",
        "description": "Ask the user for clarification or input when needed (e.g., CAPTCHA, login credentials, ambiguous instructions).",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to ask the user"
                }
            },
            "required": ["question"]
        }
    }
]


def get_tool_definitions() -> list[dict]:
    """Get tool definitions for Claude API."""
    return TOOLS


def get_tool_names() -> list[str]:
    """Get list of available tool names."""
    return [tool["name"] for tool in TOOLS]
