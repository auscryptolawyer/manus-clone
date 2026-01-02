# Manus Clone

Personal browser automation agent with a chat interface. Describe a web task and the agent autonomously browses to complete it.

## Quick Start with GitHub Codespaces

1. Click the green **Code** button → **Codespaces** → **Create codespace on master**
2. Wait for setup to complete (~2 minutes)
3. Add your Anthropic API key:
   - Create `.env` file: `cp .env.example .env`
   - Edit `.env` and add your `ANTHROPIC_API_KEY`
4. Start the backend (Terminal 1):
   ```bash
   python -m api.main
   ```
5. Start the frontend (Terminal 2):
   ```bash
   cd web && npm run dev
   ```
6. Open the frontend URL (port 5173) when prompted

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key

### Setup

```bash
# Clone
git clone https://github.com/auscryptolawyer/manus-clone.git
cd manus-clone

# Python setup
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate
pip install -r requirements.txt
playwright install chromium

# Frontend setup
cd web && npm install && cd ..

# Configure
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run

```bash
# Terminal 1 - Backend
python -m api.main

# Terminal 2 - Frontend
cd web && npm run dev
```

Open http://localhost:5173

## Architecture

```
Frontend (React) ←→ WebSocket ←→ Backend (FastAPI) ←→ Playwright Browser
                                        ↓
                                   Claude API
```

## Tech Stack
- **Backend**: Python, FastAPI, Playwright, Anthropic SDK
- **Frontend**: React, Vite, Tailwind CSS
- **AI**: Claude (via Anthropic API)

## License
MIT
