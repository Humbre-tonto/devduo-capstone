# DevDuo — Two Coding Agents, One Codebase

**Kaggle AI Agents Capstone · Freestyle Track**
*Submission deadline: July 6, 2026*

> ⚠️ Fill in the remaining placeholder before submitting: `[VIDEO_URL]`.

---

## 1. Pitch

Two AI coding agents — one Backend, one Frontend — independently build their
half of a feature, negotiate the integration contract through a custom
**crosstalk-mcp** relay, and deliver a working full-stack TODO app without a
human writing a single line of application code.

This isn't a chatbot demo — it's two real Gemini-powered agents writing real,
running code and coordinating over a secure, authenticated MCP channel,
exactly the way a backend and frontend developer would hand off an API
contract.

---

## 2. What I built

| Component | What it does | Where |
|---|---|---|
| **crosstalk-mcp relay** | Secure, token-authenticated MCP server on Cloud Run. The *only* channel the two agents can talk through. | Deployed service, see `deploy/` |
| **BE Agent** | ADK `LlmAgent` (Gemini 2.5 Flash). Reads the feature request, designs a FastAPI backend, writes the code, posts the API contract to the `be-to-fe` MCP channel. | `be_agent/agent.py` |
| **FE Agent** | ADK `LlmAgent` (Gemini 2.5 Flash). Reads the contract off MCP, designs a matching React UI, writes the code, posts a confirmation to `fe-to-be`. | `fe_agent/agent.py` |
| **Orchestrator** | Runs BE then FE against the same feature request. | `orchestrate.py` |
| **Demo UI** | Live, auto-refreshing monitor of both MCP channels — watch the agents' handoff happen in real time. | `demo_ui/` |

### Live run, end to end

```
$ python orchestrate.py "Build me a TODO app"

BE Agent
  → wrote be_agent/output/main.py (FastAPI, in-memory store, full CRUD)
  → posted CONTRACT to be-to-fe: 5 endpoints, schema, base_url

FE Agent
  → read CONTRACT from be-to-fe
  → wrote fe_agent/output/src/App.jsx (React, fetch-based)
  → posted CONFIRM to fe-to-be: 4 endpoints consumed, notes
```

I then ran both apps locally and used them through a real browser — added,
listed, and deleted a TODO item through the generated UI, hitting the
generated API. It worked.

---

## 3. Architecture

```
User: "Build me a TODO app"
        │
        ▼
┌─────────────────────┐        be-to-fe channel         ┌─────────────────────┐
│     BE Agent         │ ───────────────────────────────▶│     FE Agent         │
│  Gemini 2.5 Flash     │   CONTRACT: endpoints, schema,   │  Gemini 2.5 Flash     │
│  Picks FastAPI        │   base_url (JSON)                │  Picks React          │
│  Writes main.py       │                                   │  Writes App.jsx       │
└──────────┬────────────┘                                   └──────────┬────────────┘
           │                                                            │
           │                        fe-to-be channel                   │
           │◀────────────────────────────────────────────────────────│
           │   CONFIRM: status, consumed_endpoints, notes              │
           ▼                                                            ▼
                    ┌───────────────────────────────┐
                    │   crosstalk-mcp (Cloud Run)     │
                    │   Bearer-token auth · SQLite     │
                    │   MCP tools: post_message,        │
                    │   get_messages, list_channels      │
                    └───────────────────────────────┘
```

---

## 4. Course concepts demonstrated

| # | Concept | Evidence |
|---|---|---|
| 1 | **Multi-agent system (ADK)** | Two independent `LlmAgent`s with distinct roles and instructions — `be_agent/agent.py`, `fe_agent/agent.py` |
| 2 | **MCP server** | crosstalk-mcp, deployed and operated by me, is the *only* communication path between the agents — streamable HTTP MCP at `/mcp` |
| 3 | **Security features** | Bearer-token auth on the relay (stored in GCP Secret Manager, never in plaintext env vars); agents physically cannot communicate outside the authenticated channel |
| 4 | **Agent skills / tools** | Each agent has a custom `write_file` tool plus the `MCPToolset` (post_message/get_messages/list_channels) bound over streamable HTTP |
| 5 | **Vibe coding** | The only human input is one sentence — `"Build me a TODO app"` — agents handle stack choice, contract design, and code generation end to end |

---

## 5. Google infrastructure used

| Service | Role |
|---|---|
| **Cloud Run** | Hosts the crosstalk-mcp relay (scale-to-zero, HTTPS by default) |
| **Artifact Registry** | Mirrors the relay's container image (Cloud Run can't pull from GHCR directly) |
| **Secret Manager** | Stores the relay's bearer token, injected at runtime via `--set-secrets` |
| **Gemini API** | LLM backbone for both agents (`gemini-2.5-flash`) |
| **Agent Development Kit (ADK)** | Agent orchestration, MCP tool integration, session running |

---

## 6. Real engineering, not a happy-path demo

Things that broke and that I had to debug while building this — worth
calling out because it shows the system actually ran, not just compiled:

- Cloud Run can't pull GHCR images directly → mirrored the relay image into
  Artifact Registry.
- The relay's default `RELAY_DB=/data/relay.db` doesn't exist on Cloud Run's
  filesystem → repointed it to `/tmp`.
- `PORT` is a reserved Cloud Run env var → removed it from the deploy script.
- The Cloud Run service account needed explicit `secretAccessor` IAM on the
  secret.
- The BE agent's generated FastAPI code had **no CORS middleware**, so the
  FE agent's React app couldn't actually call it from the browser — caught
  by testing the real running apps together, not just inspecting code.
- The relay's bearer-auth middleware rejects unauthenticated CORS preflight
  `OPTIONS` requests, which browsers send without an Authorization header —
  built a small local proxy (`demo_ui/proxy.py`) so the demo UI could poll
  the relay's REST mirror from a browser.

---

## 7. How to run it yourself

```bash
git clone https://github.com/Humbre-tonto/devduo-capstone
cd devduo-capstone
cp .env.example .env   # fill in RELAY_URL / RELAY_TOKEN / GOOGLE_API_KEY

source .venv/bin/activate   # python -m venv .venv && pip install -r requirements.txt
python orchestrate.py "Build me a TODO app"

# watch it live:
python demo_ui/proxy.py &
cd demo_ui && python3 -m http.server 8090
# open http://localhost:8090
```

---

## 8. Links

- **GitHub repo:** https://github.com/Humbre-tonto/devduo-capstone
- **Demo video (2–3 min):** [VIDEO_URL]
- **crosstalk-mcp:** credited as the relay this project deploys and builds on top of

---

## 9. Submission checklist

- [x] Public GitHub repo with clean README
- [x] crosstalk-mcp credited and linked
- [ ] Live demo or video walkthrough (2-3 min)
- [x] Kaggle writeup covering pitch + implementation (this file)
- [x] Architecture diagram (section 3)
- [x] At least 3 course concepts clearly called out (section 4 — 5 listed)
