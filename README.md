# DevDuo — Two Coding Agents, One Codebase

Two Gemini-powered ADK agents — one Backend, one Frontend — build their half
of a feature independently and negotiate the integration contract through
**crosstalk-mcp**, a self-hosted, token-authenticated MCP relay on Cloud Run.

Full pitch, architecture, and course-concept mapping: see
[KAGGLE_WRITEUP.md](KAGGLE_WRITEUP.md). Build log and milestones:
[project-blueprint.md](project-blueprint.md).

## Layout

| Path | What it is |
|---|---|
| `deploy/` | Scripts to deploy crosstalk-mcp to Cloud Run (`deploy_relay.sh`) and validate it (`test_relay.sh`) |
| `be_agent/` | Backend Developer agent — designs and writes the API, posts the contract to MCP |
| `fe_agent/` | Frontend Developer agent — reads the contract, designs and writes the UI, posts confirmation |
| `orchestrate.py` | Runs BE → FE against a single feature request, end to end |
| `demo_ui/` | Live monitor of both MCP channels — watch the agents negotiate in real time |

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp deploy/.env.example .env   # fill in RELAY_URL / RELAY_TOKEN / GOOGLE_API_KEY
# RELAY_URL + RELAY_TOKEN come from running deploy/deploy_relay.sh against your own GCP project

python orchestrate.py "Build me a TODO app"
```

Generated code lands in `be_agent/output/` and `fe_agent/output/`.

To watch the BE/FE handoff live:

```bash
python demo_ui/proxy.py &
cd demo_ui && python3 -m http.server 8090
# open http://localhost:8090, click Connect
```

See `demo_ui/README.md` for why the proxy exists.
