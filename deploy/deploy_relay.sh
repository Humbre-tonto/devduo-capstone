#!/bin/bash
# =============================================================
# DevDuo — Step 2: Deploy crosstalk-mcp relay to Cloud Run
# =============================================================
# Run this once from your local machine with gcloud installed.
# Prerequisites:
#   - gcloud CLI installed and authenticated (gcloud auth login)
#   - A GCP project created
#   - Billing enabled on the project
# =============================================================

set -euo pipefail

# ── CONFIG — edit these ──────────────────────────────────────
PROJECT_ID="devduo-capstone-1796"      # e.g. devduo-capstone
REGION="us-central1"
SERVICE_NAME="crosstalk-relay"
IMAGE="us-central1-docker.pkg.dev/devduo-capstone-1796/devduo/crosstalk-mcp-python:latest"
# ─────────────────────────────────────────────────────────────

echo "🔧 Setting project..."
gcloud config set project "$PROJECT_ID"

echo "🔌 Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  --quiet

echo "🔑 Generating RELAY_TOKEN and storing in Secret Manager..."
RELAY_TOKEN=$(openssl rand -hex 24)

# Store in Secret Manager (safe — never in env vars directly)
echo -n "$RELAY_TOKEN" | gcloud secrets create relay-token \
  --data-file=- \
  --replication-policy="automatic" 2>/dev/null || \
echo -n "$RELAY_TOKEN" | gcloud secrets versions add relay-token --data-file=-

echo "🚀 Deploying crosstalk-mcp to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --port 8765 \
  --allow-unauthenticated \
  --set-secrets="RELAY_TOKEN=relay-token:latest" \
  --set-env-vars="RELAY_DB=/tmp/relay.db" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --quiet

echo ""
echo "✅ Deployment complete!"
echo ""

# Get the live URL
RELAY_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --format "value(status.url)")

echo "📡 Relay URL: $RELAY_URL"
echo "🔐 RELAY_TOKEN: $RELAY_TOKEN"
echo ""
echo "⚠️  Save the RELAY_TOKEN above — you'll need it for the agents."
echo "    Store it in your .env file (never commit it to git)."
echo ""
echo "── Next: run ./test_relay.sh to validate the relay ──"
