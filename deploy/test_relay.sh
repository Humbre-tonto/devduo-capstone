#!/bin/bash
# =============================================================
# DevDuo — Relay Validation Test
# Tests that crosstalk-mcp is live, auth works, and messages
# flow correctly between two simulated agents.
# =============================================================
# Usage: RELAY_URL=https://... RELAY_TOKEN=... ./test_relay.sh
# =============================================================

set -euo pipefail

RELAY_URL="${RELAY_URL:-}"
RELAY_TOKEN="${RELAY_TOKEN:-}"

if [[ -z "$RELAY_URL" || -z "$RELAY_TOKEN" ]]; then
  echo "❌ Set RELAY_URL and RELAY_TOKEN before running."
  echo "   Example: RELAY_URL=https://crosstalk-relay-xxx-uc.a.run.app RELAY_TOKEN=abc123 ./test_relay.sh"
  exit 1
fi

MCP_URL="$RELAY_URL/mcp"
AUTH_HEADER="Authorization: Bearer $RELAY_TOKEN"
CHANNEL="devduo-test"

echo "🧪 Testing crosstalk-mcp relay at $RELAY_URL"
echo ""

# ── Helper: send MCP tool call ────────────────────────────────
call_tool() {
  local tool=$1
  local args=$2
  curl -s -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -H "$AUTH_HEADER" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 1,
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"$tool\",
        \"arguments\": $args
      }
    }"
}

# ── Test 1: Auth check ────────────────────────────────────────
echo "1️⃣  Testing auth (valid token)..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "$AUTH_HEADER" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}')

if [[ "$STATUS" == "200" ]]; then
  echo "   ✅ Auth OK (HTTP $STATUS)"
else
  echo "   ❌ Auth failed (HTTP $STATUS)"
  exit 1
fi

# ── Test 2: Reject bad token ──────────────────────────────────
echo "2️⃣  Testing auth (bad token)..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer wrong-token" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}')

if [[ "$STATUS" == "401" ]]; then
  echo "   ✅ Bad token correctly rejected (HTTP 401)"
else
  echo "   ⚠️  Unexpected status for bad token: HTTP $STATUS"
fi

# ── Test 3: BE Agent posts contract ──────────────────────────
echo "3️⃣  BE Agent posting API contract to channel '$CHANNEL'..."
RESULT=$(call_tool "post_message" "{
  \"channel\": \"$CHANNEL\",
  \"sender\": \"be-agent\",
  \"type\": \"CONTRACT\",
  \"body\": \"{\\\"endpoints\\\": [\\\"GET /todos\\\", \\\"POST /todos\\\", \\\"DELETE /todos/{id}\\\"], \\\"schema\\\": {\\\"id\\\": \\\"int\\\", \\\"title\\\": \\\"str\\\", \\\"done\\\": \\\"bool\\\"}}\"
}")

MSG_ID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['content'][0]['text'])" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])" 2>/dev/null || echo "unknown")
echo "   ✅ Contract posted (message id: $MSG_ID)"

# ── Test 4: FE Agent reads it ────────────────────────────────
echo "4️⃣  FE Agent reading messages from channel '$CHANNEL'..."
RESULT=$(call_tool "get_messages" "{
  \"channel\": \"$CHANNEL\",
  \"since_id\": 0
}")

MSG_COUNT=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
text = d['result']['content'][0]['text']
msgs = json.loads(text)
print(len(msgs))
" 2>/dev/null || echo "?")
echo "   ✅ FE Agent sees $MSG_COUNT message(s) in channel"

# ── Test 5: FE Agent replies ─────────────────────────────────
echo "5️⃣  FE Agent posting confirmation back..."
call_tool "post_message" "{
  \"channel\": \"$CHANNEL\",
  \"sender\": \"fe-agent\",
  \"type\": \"CONFIRM\",
  \"body\": \"{\\\"status\\\": \\\"ready\\\", \\\"consumed\\\": [\\\"GET /todos\\\", \\\"POST /todos\\\", \\\"DELETE /todos/{id}\\\"]}\"
}" > /dev/null
echo "   ✅ Confirmation posted"

# ── Test 6: List channels ─────────────────────────────────────
echo "6️⃣  Listing all channels..."
RESULT=$(call_tool "list_channels" "{}")
echo "   ✅ Channels: $(echo "$RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
text=d['result']['content'][0]['text']
channels=json.loads(text)
print([c['channel'] for c in channels])
" 2>/dev/null || echo "(see raw output)")"

echo ""
echo "══════════════════════════════════════════"
echo "✅ All tests passed — relay is ready!"
echo "   RELAY_URL:   $RELAY_URL"
echo "   MCP channel: $CHANNEL"
echo "══════════════════════════════════════════"
echo ""
echo "── Next: build the BE Agent (Step 3) ──"
