# DevDuo — Demo UI

Live monitor showing the BE Agent and FE Agent negotiating over crosstalk-mcp
in real time. Polls the relay's REST mirror every 2 seconds and renders both
channels (`be-to-fe`, `fe-to-be`) side by side.

## Why a proxy?

The relay enforces a Bearer token on every HTTP request, including the CORS
preflight `OPTIONS` request browsers send automatically — which can't carry
an Authorization header. That makes the relay's REST endpoints uncallable
directly from a static page. `proxy.py` is a small same-machine relay: it
holds the token server-side, answers preflights itself, and forwards GET
requests to the real relay.

## Run it

```bash
# from the project root
source .venv/bin/activate
python demo_ui/proxy.py          # starts on http://localhost:8092

# in another terminal
cd demo_ui && python3 -m http.server 8090
# open http://localhost:8090
```

Click **Connect** (defaults to the local proxy). Run `python orchestrate.py
"Build me a TODO app"` in another terminal to watch the BE → FE conversation
appear live.
