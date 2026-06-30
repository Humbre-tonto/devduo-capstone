# DevDuo
### Two coding agents negotiate a backend/frontend contract and ship a working app from one sentence

**Track: Agents for Business**
*Kaggle AI Agents Capstone — 5-Day AI Agents Intensive with Google*

> ⚠️ Remaining placeholder before submitting: `[VIDEO_URL]` (YouTube link, ≤5 min). Cover image and video must also be attached in the Kaggle Writeup's Media Gallery — see the checklist at the bottom.

---

## 1. The problem

Every full-stack feature hits the same expensive bottleneck: a backend
developer and a frontend developer have to agree on an API contract —
endpoint names, request/response shapes, error formats — before either side
can finish their half. In practice this is Slack threads, stale wiki pages,
"wait, did you change the field name?" bugs, and rework when the two sides
silently drift apart. It's pure coordination overhead: no business value is
created while it happens, and it's a real, recurring cost on every team that
ships software with separate BE/FE ownership.

This is a business problem, not just a workflow annoyance: coordination
overhead is time billed against a sprint that produces nothing the customer
sees, and contract drift is one of the most common sources of integration
bugs that surface late, in QA or production, when they're most expensive to
fix.

## 2. The solution

**DevDuo** replaces that human coordination loop with two independent AI
agents — a Backend Developer agent and a Frontend Developer agent — that
negotiate the contract themselves, the same way two human developers would,
but over a secure, auditable, machine-readable channel instead of Slack.

- The **BE Agent** receives the feature request, picks a backend stack,
  designs and writes the API, and publishes the contract (endpoints, schema,
  base URL) as a structured message.
- The **FE Agent** reads that contract — and only that contract, it never
  sees the BE agent's reasoning or code directly — picks a compatible UI
  stack, and writes a frontend that calls exactly those endpoints.
- Neither agent can communicate with the other except through this channel,
  which mirrors (and enforces) the real-world handoff discipline a contract
  is supposed to provide.

The channel itself, **crosstalk-mcp**, is a small MCP server I deployed and
operate on Cloud Run, secured with a bearer token stored in GCP Secret
Manager. It is the single source of truth for the negotiation — every
message either agent posts is durable, timestamped, and visible to both
sides and to a human auditor.

For a business, the value is direct: less calendar time spent on handoff
meetings, a durable contract artifact instead of tribal knowledge, and a
pattern that generalizes past TODO apps to any feature where two
specifications need to agree before code ships.

## 3. What I built

| Component | What it does | Where |
|---|---|---|
| **crosstalk-mcp relay** | Token-authenticated MCP server on Cloud Run. The *only* channel the two agents can talk through. | `deploy/` |
| **BE Agent** | ADK `LlmAgent` (Gemini 2.5 Flash). Designs and writes a FastAPI backend, posts the API contract to the `be-to-fe` MCP channel. | `be_agent/agent.py` |
| **FE Agent** | ADK `LlmAgent` (Gemini 2.5 Flash). Reads the contract off MCP, writes a matching React UI, posts a confirmation to `fe-to-be`. | `fe_agent/agent.py` |
| **Orchestrator** | Runs BE then FE against the same feature request, end to end. | `orchestrate.py` |
| **Demo UI** | Live, auto-refreshing monitor of both MCP channels — watch the negotiation happen in real time. | `demo_ui/` |

### A real run, end to end

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

I then ran both generated apps locally and used them through a real
browser — added, listed, and deleted a TODO item through the generated UI,
hitting the generated API. It worked, after I found and fixed a real bug
the FE agent's app hit (see §6).

## 4. Architecture

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

## 5. Course concepts demonstrated

The brief requires at least 3 of the listed concepts; this submission
covers 4, three of them directly in code:

| Concept | Where | How |
|---|---|---|
| **Multi-agent system (ADK)** | Code | Two independent `LlmAgent`s, distinct roles/instructions, no shared memory — `be_agent/agent.py`, `fe_agent/agent.py` |
| **MCP Server** | Code | crosstalk-mcp, deployed and operated by me, is the *only* path between the agents — streamable HTTP MCP at `/mcp`, tools `post_message`/`get_messages`/`list_channels` |
| **Security features** | Code | Bearer-token auth enforced on every relay request; token generated and stored in GCP Secret Manager, never committed or logged; CORS-locked demo proxy keeps the token server-side |
| **Deployability** | Video | Live walkthrough of the Cloud Run deployment (`deploy/deploy_relay.sh`) and the running service in the GCP console |

## 6. Real engineering, not a happy-path demo

Things that broke while building this, worth calling out because they show
the system actually ran end to end, not just compiled:

- Cloud Run can't pull GHCR images directly → mirrored the relay image into
  Artifact Registry.
- The relay's default `RELAY_DB=/data/relay.db` doesn't exist on Cloud
  Run's filesystem → repointed it to `/tmp`.
- `PORT` is a reserved Cloud Run env var → removed it from the deploy
  script.
- The Cloud Run service account needed explicit `secretAccessor` IAM on the
  secret.
- The BE agent's generated FastAPI code had **no CORS middleware**, so the
  FE agent's generated React app couldn't actually call it from a browser —
  only caught by running both generated apps together, not by inspecting
  the code.
- The relay's bearer-auth middleware rejects unauthenticated CORS preflight
  `OPTIONS` requests, which browsers send without an Authorization header —
  built a small local proxy (`demo_ui/proxy.py`) so the demo UI's REST
  polling could work from a browser without exposing the token client-side.

## 7. How to run it yourself

```bash
git clone https://github.com/Humbre-tonto/devduo-capstone
cd devduo-capstone
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp deploy/.env.example .env   # fill in RELAY_URL / RELAY_TOKEN / GOOGLE_API_KEY
# RELAY_URL + RELAY_TOKEN come from running deploy/deploy_relay.sh against your own GCP project

python orchestrate.py "Build me a TODO app"

# watch the negotiation live:
python demo_ui/proxy.py &
cd demo_ui && python3 -m http.server 8090
# open http://localhost:8090
```

Full setup detail in [README.md](README.md).

## 8. Links

- **GitHub repo:** https://github.com/Humbre-tonto/devduo-capstone
- **Demo video:** [VIDEO_URL]
- **crosstalk-mcp:** the open-source relay this project deploys and builds on top of — credited as the integration layer

## 9. Submission checklist

- [x] Public GitHub repo with README covering problem/solution/architecture/setup
- [x] crosstalk-mcp credited and linked
- [ ] Cover image attached to Kaggle Writeup Media Gallery
- [ ] Video (≤5 min, published to YouTube) attached to Media Gallery
- [x] Kaggle Writeup text (this file) — title, subtitle, track selected, under 2,500 words
- [x] Architecture diagram (§4)
- [x] At least 3 course concepts clearly called out, with code/video evidence (§5)
- [x] No API keys or passwords in the repo (`.env` gitignored, verified)
