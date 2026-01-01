# CLAUDE.md - AI Assistant Instructions

## Project Overview

This is **Manus Clone**, a personal browser automation agent. Users chat with the agent, describe a web task, and the agent autonomously browses the web to complete it.

**Stack:** Python (FastAPI, Playwright) + React frontend + Claude API

**Status:** Early development

---

## Key Architecture Decisions

1. **Simplified DOM representation** - We extract only interactive elements with numeric IDs rather than passing full HTML to the LLM
2. **WebSocket for real-time updates** - Frontend maintains persistent connection for live screenshots and status
3. **Tool-based agent** - Claude uses structured tool calls (click, type, navigate, etc.) rather than generating code
4. **Single browser session per task** - No tab management in v1

---

## Code Conventions

### Python (Backend)

- Python 3.11+
- Use `async`/`await` throughout - Playwright is async
- Type hints on all function signatures
- Pydantic models for all data structures
- Keep files under 200 lines; split if larger
- Use `loguru` for logging, not print statements

```python
# Good
async def click_element(page: Page, selector: str) -> ActionResult:
    """Click an element and return the result."""
    try:
        await page.click(selector, timeout=5000)
        return ActionResult(success=True)
    except TimeoutError:
        return ActionResult(success=False, error="Element not found")

# Bad
def click(p, s):
    p.click(s)
```

### React (Frontend)

- Functional components with hooks
- Keep components small and focused
- CSS modules or Tailwind (not inline styles)
- Use `useReducer` for complex state, `useState` for simple

```jsx
// Good
function BrowserView({ screenshot, elements, loading }) {
  if (loading) return <Spinner />;
  return (
    <div className={styles.browserView}>
      <img src={`data:image/jpeg;base64,${screenshot}`} alt="Browser" />
    </div>
  );
}

// Bad
function BrowserView(props) {
  return <div style={{width: '100%'}}><img src={props.ss}/></div>
}
```

---

## File Purposes

| File | Purpose |
|------|---------|
| `agent/browser/driver.py` | Browser lifecycle (launch, close, new context) |
| `agent/browser/actions.py` | Atomic actions (click, type, scroll, navigate) |
| `agent/browser/observer.py` | Extract page state (screenshot, DOM summary) |
| `agent/core/planner.py` | Break user task into steps using Claude |
| `agent/core/executor.py` | Main agent loop (observe → think → act) |
| `agent/core/tools.py` | Tool definitions for Claude API |
| `api/main.py` | FastAPI app setup, routes, CORS |
| `api/websocket.py` | WebSocket connection and message handling |
| `api/schemas.py` | Pydantic models for API data |
| `web/src/App.jsx` | Main React component, layout |
| `web/src/components/Chat.jsx` | Chat input and message history |
| `web/src/components/BrowserView.jsx` | Screenshot display |
| `web/src/hooks/useWebSocket.js` | WebSocket connection hook |

---

## Common Tasks

### Adding a New Browser Action

1. Add the action function to `agent/browser/actions.py`
2. Add corresponding tool definition to `agent/core/tools.py`
3. Handle the tool call in `agent/core/executor.py`

### Modifying the Agent Prompt

The main agent prompt is in `agent/core/executor.py`. Key sections:
- System prompt with role and capabilities
- Tool descriptions (auto-generated from tools.py)
- Current page state injection
- Action history context

### Adding a Frontend Feature

1. Create component in `web/src/components/`
2. Add any WebSocket message handling to `useWebSocket.js`
3. Wire into `App.jsx`

---

## Important Patterns

### Page State Object

This is what gets sent to Claude for decision-making:

```python
@dataclass
class PageState:
    url: str
    title: str
    interactive_elements: list[Element]  # Numbered 1, 2, 3...
    visible_text: str                     # Truncated summary
    screenshot_base64: str
    error: str | None = None
```

### Action Result

Every browser action returns:

```python
@dataclass
class ActionResult:
    success: bool
    error: str | None = None
    data: Any = None  # For extract actions
```

### WebSocket Message Format

All messages are JSON with a `type` field:

```python
# Outbound (server → client)
{"type": "observation", "screenshot": "...", "elements": [...]}
{"type": "action", "tool": "click", "params": {...}}
{"type": "complete", "result": "..."}

# Inbound (client → server)
{"type": "start_task", "task": "..."}
{"type": "cancel"}
{"type": "user_message", "content": "..."}
```

---

## Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install fastapi uvicorn playwright anthropic loguru pydantic websockets

# Install Playwright browsers
playwright install chromium

# Frontend
cd web && npm install

# Run backend
uvicorn api.main:app --reload

# Run frontend (separate terminal)
cd web && npm run dev
```

---

## Testing Approach

- Unit tests for browser actions (mock Playwright)
- Integration tests for agent loop (use simple test pages)
- Manual testing for full flow (no e2e automation yet)

---

## Known Limitations / TODO

- [ ] No handling for CAPTCHAs (will ask user)
- [ ] No file upload/download support yet
- [ ] Single tab only
- [ ] No persistent sessions
- [ ] Mobile layout needs work

---

## Debugging Tips

1. **See browser visually**: Set `BROWSER_HEADLESS=false` in `.env`
2. **Log all Claude calls**: Check logs for full prompt/response
3. **WebSocket issues**: Browser console shows connection state
4. **DOM extraction issues**: Save raw HTML to file for inspection

---

## Don't Do

- Don't pass full HTML to Claude - always use the simplified element list
- Don't store any credentials or sensitive data
- Don't make the agent loop synchronous - everything is async
- Don't use global state - pass dependencies explicitly
- Don't commit `.env` or API keys
