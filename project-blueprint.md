# 🤝 DevDuo — Two Coding Agents, One Codebase
### Kaggle AI Agents Capstone · Agents for Business Track
**Author:** Solo submission | **Deadline:** July 6, 2026

---

## 1. One-Line Pitch

> Two AI coding agents — one Backend, one Frontend — independently build their half of a feature, negotiate the integration contract through **crosstalk-mcp**, and deliver a working full-stack TODO app without a human writing a single line of code.

---

## 2. The Problem

Building full-stack features requires constant back-and-forth between BE and FE developers: agreeing on API contracts, data shapes, endpoint names, and error formats. This coordination is slow, error-prone, and hard to automate — until now.

**DevDuo** replaces that coordination layer with two AI agents that negotiate like real developers, using crosstalk-mcp as their secure communication channel.

---

## 3. Agent Roles

| Agent | Role | Responsibility |
|---|---|---|
| **BE Agent** | Backend Developer | Analyzes the feature, picks a stack, builds the API, posts the contract to crosstalk-mcp |
| **FE Agent** | Frontend Developer | Reads the contract from crosstalk-mcp, picks a compatible UI stack, builds the frontend, confirms integration |
| **crosstalk-mcp** | Secure Relay | The only communication channel between agents — authenticated, async, network-based |

---

## 4. The Conversation Flow

```
User: "Build me a TODO app"
        │
        ▼
┌─────────────────────┐
│     BE Agent        │
│  1. Analyzes task   │
│  2. Picks stack     │
│     (e.g. FastAPI)  │
│  3. Builds API      │
│  4. Posts contract  │
│     to MCP channel  │
└────────┬────────────┘
         │  crosstalk-mcp channel: "be-to-fe"
         │  Message: {
         │    "endpoints": [
         │      "GET /todos",
         │      "POST /todos",
         │      "DELETE /todos/{id}"
         │    ],
         │    "schema": { "id": "int", "title": "str", "done": "bool" },
         │    "base_url": "http://localhost:8000"
         │  }
         ▼
┌─────────────────────┐
│     FE Agent        │
│  1. Reads contract  │
│  2. Picks UI stack  │
│     (e.g. React)    │
│  3. Builds frontend │
│  4. Confirms to MCP │
└────────┬────────────┘
         │  crosstalk-mcp channel: "fe-to-be"
         │  Message: {
         │    "status": "ready",
         │    "consumed_endpoints": ["GET /todos", "POST /todos"],
         │    "notes": "Used axios for HTTP calls"
         │  }
         ▼
┌─────────────────────┐
│   Integrated App    │
│   Full-stack TODO   │
│   Running locally   │
│   or on Cloud Run   │
└─────────────────────┘
```

---

## 5. Key Course Concepts Demonstrated (≥ 3 required)

| # | Concept | How DevDuo uses it |
|---|---|---|
| ✅ 1 | **Multi-agent system (ADK)** | BE Agent + FE Agent, distinct roles, independent execution |
| ✅ 2 | **MCP server** | crosstalk-mcp IS the MCP server — built by the submitter |
| ✅ 3 | **Security features** | Token-authenticated MCP channels; agents can't communicate outside the relay |
| ✅ 4 | **Agent skills** | Each agent has specialized skills: stack selection, code generation, contract publishing |
| ✅ 5 | **Vibe coding** | User describes the feature in plain English — agents handle everything else |

---

## 6. Google Infrastructure

| GCP Service | Role |
|---|---|
| **Vertex AI (Gemini 1.5 Pro)** | LLM backbone for both agents |
| **Cloud Run** | Hosts crosstalk-mcp relay + optional demo UI |
| **Agent Development Kit (ADK)** | Agent orchestration framework |
| **Secret Manager** | Stores RELAY_TOKEN and Gemini API keys |
| **Cloud Build** | CI/CD from GitHub |

---

## 7. What Makes This Stand Out

1. **Meta concept** — agents building software is compelling and visual for judges
2. **crosstalk-mcp as the star** — not a side tool, it IS the integration layer
3. **Stack agnosticism** — agents reason about what to use, they don't just follow a template
4. **Real output** — judges get actual running code, not just a chatbot response
5. **Mirrors real dev workflow** — BE/FE contract negotiation is a universal pain point

---

## 8. Build Milestones

| # | Milestone | What happens |
|---|---|---|
| 1 | ✅ Blueprint | Done |
| 2 | ✅ Deploy crosstalk-mcp to Cloud Run | Live at the relay URL in `.env`; token auth + MCP handshake verified |
| 3 | ✅ BE Agent | Gemini-powered (`be_agent/agent.py`), builds FastAPI TODO API, posts contract to MCP |
| 4 | ✅ FE Agent | Reads contract from MCP (`fe_agent/agent.py`), builds React UI, posts confirmation |
| 5 | ✅ End-to-end run | `orchestrate.py` runs the full pipeline; verified working live in browser (CORS bug found & fixed in generated backend) |
| 6 | ✅ Demo UI | `demo_ui/` — live 2s-polling monitor of both MCP channels, verified rendering real contract + confirmation messages |
| 7 | Kaggle write-up + video | See `KAGGLE_WRITEUP.md` draft — needs your repo link + demo video |

---

## 9. Submission Checklist

- [ ] Public GitHub repo with clean README
- [ ] crosstalk-mcp credited and linked
- [ ] Live demo or video walkthrough (2-3 min)
- [ ] Kaggle writeup covering pitch + implementation
- [ ] Architecture diagram
- [ ] At least 3 course concepts clearly called out in the writeup

---

*Next → Step 2: Deploy crosstalk-mcp to Cloud Run with token auth and validate the channel end-to-end.*
