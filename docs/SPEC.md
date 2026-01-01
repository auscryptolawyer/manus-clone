# Manus Clone - Technical Specification

## Overview

A personal browser automation agent with a chat interface. Users describe tasks in natural language, and the agent autonomously navigates the web to complete them.

## Goals

- **Autonomous browsing**: Agent can navigate, click, type, scroll, and extract data
- **Real-time visibility**: User sees what the agent is doing via screenshots and status updates
- **Mobile-friendly**: Responsive web UI works on phone and desktop
- **Self-hosted**: Runs locally or on a personal VPS
- **Interruptible**: User can pause, correct, or cancel at any time

## Non-Goals (v1)

- Multi-user support
- Authentication/login for the app itself
- Persistent task history (sessions are ephemeral)
- File uploads/downloads (future enhancement)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Chat UI    │  │ Browser View│  │ Status/Controls │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                      WebSocket
                           │
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  WebSocket  │  │  Agent      │  │  Browser        │  │
│  │  Handler    │──│  Controller │──│  Manager        │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              Claude API     Playwright
```

---

## Core Components

### 1. Browser Manager (`/agent/browser/`)

Handles all Playwright interactions.

**Files:**
- `driver.py` - Browser lifecycle (launch, close, new page)
- `actions.py` - Atomic actions (click, type, scroll, navigate)
- `observer.py` - Page state extraction (screenshot, DOM summary, visible text)

**DOM Extraction Strategy:**

Full DOM is too large for LLM context. Extract a simplified representation:

```python
# Target format for LLM
{
    "url": "https://example.com/search",
    "title": "Search Results",
    "interactive_elements": [
        {"id": 1, "type": "button", "text": "Next Page", "selector": "button.next"},
        {"id": 2, "type": "input", "placeholder": "Search...", "selector": "input#search"},
        {"id": 3, "type": "link", "text": "Product Details", "href": "/product/123"}
    ],
    "visible_text_summary": "Showing results 1-10 of 234...",
    "screenshot_base64": "..."
}
```

Assign numeric IDs to interactive elements so the LLM can reference them easily ("click element 3").

### 2. Agent Core (`/agent/core/`)

The reasoning and execution loop.

**Files:**
- `planner.py` - Breaks high-level task into steps
- `executor.py` - Runs the observe-think-act loop
- `tools.py` - Tool definitions for Claude

**Agent Loop:**

```python
async def run_task(task: str):
    plan = await planner.create_plan(task)
    
    for step in plan.steps:
        while not step.complete:
            # 1. Observe
            state = await browser.observe()
            
            # 2. Think (Claude decides action)
            action = await llm.decide(
                task=task,
                current_step=step,
                page_state=state,
                history=action_history
            )
            
            # 3. Act
            result = await browser.execute(action)
            
            # 4. Update
            action_history.append((action, result))
            await websocket.send_update(state, action, result)
            
            # 5. Check completion
            step.complete = await llm.check_step_complete(step, state)
```

**Tools for Claude:**

```python
tools = [
    {
        "name": "navigate",
        "description": "Go to a URL",
        "parameters": {"url": "string"}
    },
    {
        "name": "click",
        "description": "Click an interactive element by its ID",
        "parameters": {"element_id": "integer"}
    },
    {
        "name": "type",
        "description": "Type text into the focused element or a specified element",
        "parameters": {"text": "string", "element_id": "integer (optional)"}
    },
    {
        "name": "scroll",
        "description": "Scroll the page",
        "parameters": {"direction": "up|down", "amount": "string (e.g., 'half_page')"}
    },
    {
        "name": "wait",
        "description": "Wait for page to load or element to appear",
        "parameters": {"seconds": "integer", "for_element": "string (optional)"}
    },
    {
        "name": "extract",
        "description": "Extract specific data from the page",
        "parameters": {"what": "string description of data to extract"}
    },
    {
        "name": "complete",
        "description": "Mark task as complete and provide final answer",
        "parameters": {"result": "string"}
    },
    {
        "name": "fail",
        "description": "Mark task as failed with reason",
        "parameters": {"reason": "string"}
    }
]
```

### 3. API Layer (`/api/`)

**Files:**
- `main.py` - FastAPI app, CORS, static files
- `websocket.py` - Real-time connection handler
- `schemas.py` - Pydantic models

**WebSocket Protocol:**

```python
# Client -> Server
{"type": "start_task", "task": "Find the cheapest flight from Brisbane to Tokyo in March"}
{"type": "cancel"}
{"type": "user_message", "content": "Actually, make that April"}

# Server -> Client
{"type": "status", "status": "planning"}
{"type": "plan", "steps": ["Search flights", "Compare prices", "Report best option"]}
{"type": "step_start", "step": 1, "description": "Searching flights"}
{"type": "observation", "screenshot": "base64...", "elements": [...]}
{"type": "action", "tool": "click", "params": {"element_id": 5}}
{"type": "step_complete", "step": 1}
{"type": "complete", "result": "The cheapest flight is..."}
{"type": "error", "message": "..."}
```

### 4. Frontend (`/web/`)

React app with three main sections:

**Chat Panel:**
- Message input
- Conversation history
- Task status indicator

**Browser View:**
- Live screenshot (updates every action)
- Clickable overlay showing element IDs (optional, for debugging)
- Current URL display

**Controls:**
- Start/Cancel button
- Step progress indicator

**Mobile Layout:**
- Stack vertically: Controls → Browser View → Chat
- Browser view can be collapsed/minimized
- Chat is primary interface

---

## Data Flow

### Starting a Task

1. User types task in chat, clicks send
2. Frontend sends `start_task` over WebSocket
3. Backend creates new agent session
4. Planner generates step list, sends `plan` event
5. Executor begins loop, streaming updates

### During Execution

1. Observer captures page state
2. State sent to frontend as `observation`
3. Claude decides action via tool use
4. Action sent to frontend as `action`
5. Playwright executes action
6. Loop continues until complete/failed/cancelled

### User Intervention

1. User sends `user_message` with correction
2. Message injected into Claude context
3. Agent adjusts approach based on feedback

---

## Configuration

**Environment Variables:**

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
BROWSER_HEADLESS=true          # false for debugging
SCREENSHOT_QUALITY=50          # JPEG quality 1-100
MAX_STEPS_PER_TASK=50          # prevent runaway agents
STEP_TIMEOUT_SECONDS=60        # timeout per action
PORT=8000
```

---

## Error Handling

| Scenario | Handling |
|----------|----------|
| Page load timeout | Retry once, then report to user |
| Element not found | Re-observe page, ask Claude to reassess |
| Claude API error | Retry with backoff, fail after 3 attempts |
| Unexpected popup/modal | Observe new state, Claude handles dynamically |
| CAPTCHA detected | Pause and ask user for help |
| Task seems stuck | After 3 identical states, ask user for guidance |

---

## Security Considerations

- **Local/personal use only** - no auth implemented
- **Sandboxed browser** - Playwright runs in Docker
- **No credential storage** - user enters passwords live if needed
- **Rate limiting** - prevent accidental API cost blowout

---

## File Structure

```
/manus-clone
├── CLAUDE.md                 # AI assistant instructions
├── docker-compose.yml
├── .env.example
├── /docs
│   └── SPEC.md              # This file
├── /agent
│   ├── __init__.py
│   ├── /browser
│   │   ├── __init__.py
│   │   ├── driver.py
│   │   ├── actions.py
│   │   └── observer.py
│   └── /core
│       ├── __init__.py
│       ├── planner.py
│       ├── executor.py
│       └── tools.py
├── /api
│   ├── __init__.py
│   ├── main.py
│   ├── websocket.py
│   └── schemas.py
└── /web
    ├── package.json
    ├── /public
    │   └── index.html
    └── /src
        ├── App.jsx
        ├── App.css
        ├── /components
        │   ├── Chat.jsx
        │   ├── BrowserView.jsx
        │   └── Controls.jsx
        └── /hooks
            └── useWebSocket.js
```

---

## Development Phases

### Phase 1: Browser Foundation
- [ ] Playwright driver with basic actions
- [ ] DOM extractor producing clean element list
- [ ] Screenshot capture and encoding

### Phase 2: Agent Loop
- [ ] Claude integration with tool definitions
- [ ] Basic observe-think-act loop
- [ ] Action history tracking

### Phase 3: API & WebSocket
- [ ] FastAPI server
- [ ] WebSocket connection handling
- [ ] Real-time event streaming

### Phase 4: Frontend
- [ ] React app scaffold
- [ ] Chat component
- [ ] Browser view with live screenshots
- [ ] Mobile responsive layout

### Phase 5: Polish
- [ ] Error handling improvements
- [ ] User intervention flow
- [ ] Docker packaging
- [ ] Documentation

---

## Future Enhancements (v2+)

- File download/upload support
- Multiple browser tabs
- Session persistence and replay
- Saved task templates
- Local LLM option (Ollama)
- Browser extension mode
