# DevDuo — Two Coding Agents, One Codebase

Kaggle AI Agents Capstone · **Agents for Business** track. Full pitch and
course-concept mapping: [KAGGLE_WRITEUP.md](KAGGLE_WRITEUP.md). Build log and
milestones: [project-blueprint.md](project-blueprint.md).

## Problem

Shipping a full-stack feature means a backend and a frontend developer have
to agree on an API contract before either side can finish — endpoint names,
request/response shapes, error formats. In practice that agreement happens
in Slack threads and stale docs, drifts silently, and surfaces as
integration bugs late in the cycle. It's coordination overhead: real time
spent producing nothing the customer sees.

## Solution

Two independent Gemini-powered ADK agents do the negotiation themselves:

- **BE Agent** picks a backend stack, designs and writes the API, publishes
  the contract (endpoints, schema, base URL) to a shared channel.
- **FE Agent** reads *only* that contract (never the BE agent's code or
  reasoning directly), picks a UI stack, writes a frontend that calls
  exactly those endpoints, and confirms back on the channel.

The channel is **crosstalk-mcp**, a token-authenticated MCP relay deployed
on Cloud Run — the only path either agent has to communicate, and a durable,
auditable record of the negotiation.

## Architecture

```
User: "Build me a TODO app"
        │
        ▼
┌─────────────────────┐        be-to-fe channel         ┌─────────────────────┐
│     BE Agent          │ ──────────────────────────────▶│     FE Agent          │
│  Gemini 2.5 Flash      │   CONTRACT: endpoints, schema,  │  Gemini 2.5 Flash      │
│  Picks FastAPI         │   base_url (JSON)               │  Picks React           │
│  Writes main.py        │                                  │  Writes App.jsx        │
└──────────┬─────────────┘                                  └──────────┬─────────────┘
           │                                                            │
           │                       fe-to-be channel                    │
           │◀───────────────────────────────────────────────────────│
           │   CONFIRM: status, consumed_endpoints, notes              │
           ▼                                                            ▼
                    ┌────────────────────────────────┐
                    │   crosstalk-mcp (Cloud Run)      │
                    │   Bearer-token auth · SQLite      │
                    │   MCP tools: post_message,         │
                    │   get_messages, list_channels       │
                    └────────────────────────────────┘
```

## Layout

| Path | What it is |
|---|---|
| `deploy/` | Scripts to deploy crosstalk-mcp to Cloud Run (`deploy_relay.sh`) and validate it (`test_relay.sh`) |
| `be_agent/` | Backend Developer agent — designs and writes the API, posts the contract to MCP |
| `fe_agent/` | Frontend Developer agent — reads the contract, designs and writes the UI, posts confirmation |
| `orchestrate.py` | Runs BE → FE against a single feature request, end to end |
| `demo_ui/` | Live monitor of both MCP channels — watch the agents negotiate in real time |

## Setup

### 1. Deploy the relay (or reuse an existing one)

```bash
cd deploy
# edit PROJECT_ID in deploy_relay.sh to your own GCP project
chmod +x deploy_relay.sh && ./deploy_relay.sh
# copy the printed RELAY_URL and RELAY_TOKEN
```

Requires `gcloud` authenticated against a GCP project with billing enabled.
See `deploy/README.md` for what the script does and why.

### 2. Configure environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp deploy/.env.example .env
# fill in RELAY_URL, RELAY_TOKEN (from step 1) and GOOGLE_API_KEY
# (a Gemini API key from https://aistudio.google.com — never commit this file)
```

### 3. Run the agents

```bash
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
python orchestrate.py "Build me a TODO app"
```

Generated code lands in `be_agent/output/` and `fe_agent/output/`. The BE
output is a runnable FastAPI app (`uvicorn main:app`); the FE output is a
Vite/React app (`npm install && npm run dev`).

### 4. Watch the negotiation live

```bash
python demo_ui/proxy.py &
cd demo_ui && python3 -m http.server 8090
# open http://localhost:8090, click Connect
```

See `demo_ui/README.md` for why the local proxy exists (the relay's
auth middleware blocks unauthenticated browser CORS preflights).

## Security notes

- The relay token is generated server-side by `deploy_relay.sh` and stored
  in GCP Secret Manager — it is never written into source.
- `.gitignore` excludes `.env`; no API keys or tokens are committed to this
  repo (verify with `git log -p -- .env`, which returns nothing).
- The demo UI never holds the relay token client-side — `demo_ui/proxy.py`
  keeps it server-side and forwards only GET requests.
