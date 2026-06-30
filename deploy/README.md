# DevDuo — Step 2: Deploy crosstalk-mcp Relay

## What this does

Deploys the **crosstalk-mcp Python relay** to Google Cloud Run with:
- Token authentication via `RELAY_TOKEN`
- Secret stored in **GCP Secret Manager** (not in env vars)
- HTTPS endpoint (Cloud Run provides this automatically)
- Scale-to-zero (free when idle)

## Files

| File | Purpose |
|---|---|
| `deploy_relay.sh` | One-shot deploy to Cloud Run |
| `test_relay.sh` | Validates relay is live, auth works, messages flow |
| `../.env.example` | Template for environment variables |

## Steps

### 1. Edit the config section in `deploy_relay.sh`
```bash
PROJECT_ID="your-gcp-project-id"   # your actual GCP project
REGION="us-central1"                # or closest region to you
```

### 2. Run the deploy
```bash
chmod +x deploy_relay.sh
./deploy_relay.sh
```

This will:
- Enable Cloud Run + Secret Manager APIs
- Generate a `RELAY_TOKEN` and store it in Secret Manager
- Pull `ghcr.io/humbre-tonto/crosstalk-mcp-python:latest` from GHCR
- Deploy to Cloud Run on port 8765
- Print the live HTTPS URL and token

### 3. Save the output
Copy the `RELAY_URL` and `RELAY_TOKEN` from the deploy output into your `.env` file:
```bash
cp .env.example .env
# then edit .env with the values
```

### 4. Validate the relay
```bash
chmod +x test_relay.sh
RELAY_URL=https://your-relay-url.run.app \
RELAY_TOKEN=your-token \
./test_relay.sh
```

All 6 tests should pass. If they do, the relay is ready and you can move to Step 3 (BE Agent).

## Architecture at this point

```
Internet
   │  HTTPS
   ▼
Cloud Run (crosstalk-relay)
   │  ghcr.io/humbre-tonto/crosstalk-mcp-python:latest
   │  RELAY_TOKEN ← Secret Manager
   │  SQLite storage (ephemeral — ok for demo)
   │
   ├── POST /mcp  ← agents connect here
   └── GET  /api  ← human-readable REST mirror
```

## Notes

- SQLite on Cloud Run is ephemeral (resets on cold start). Fine for a demo.
- For production you'd mount a Cloud SQL instance — but that's out of scope here.
- The relay is stateless enough that a cold start just means an empty mailbox.
