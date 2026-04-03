#!/bin/bash
#
# AgentRoute Oracle - cURL Examples
#
# This script shows how to use AgentRoute Oracle with cURL commands.
#
# Usage:
#   bash examples/curl_example.sh
#

set -e

# Configuration
API_URL="https://agentroute-oracle.onrender.com"
L402_TOKEN="your_l402_token_here"  # You'll get this after paying the first invoice

echo "🚀 AgentRoute Oracle - cURL Examples"
echo ""

# Example 1: Basic route query (without L402 token - will get invoice)
echo "Example 1: Get optimal route (first query - will need payment)"
echo "=============================================================="
echo ""

SOURCE="agent_wallet_001"
DESTINATION="merchant_wallet_001"
AMOUNT=10000

echo "Sending request to AgentRoute Oracle..."
echo "Source:      $SOURCE"
echo "Destination: $DESTINATION"
echo "Amount:      $AMOUNT sats"
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/route" \
  -H "Content-Type: application/json" \
  -d "{
    \"source\": \"$SOURCE\",
    \"destination\": \"$DESTINATION\",
    \"amount_sats\": $AMOUNT,
    \"timeout_seconds\": 30
  }")

echo "Response:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

# Example 2: Route query with L402 token
echo ""
echo "Example 2: Get optimal route (with L402 token)"
echo "=============================================================="
echo ""

echo "Sending request with L402 token..."
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/route" \
  -H "Content-Type: application/json" \
  -H "Authorization: L402 $L402_TOKEN" \
  -d "{
    \"source\": \"agent_001\",
    \"destination\": \"merchant_001\",
    \"amount_sats\": 5000,
    \"timeout_seconds\": 30
  }")

echo "Response:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

# Example 3: Multiple queries
echo ""
echo "Example 3: Multiple route queries"
echo "=============================================================="
echo ""

ROUTES=(
  '{"source":"agent_001","destination":"merchant_001","amount_sats":5000}'
  '{"source":"agent_001","destination":"merchant_002","amount_sats":15000}'
  '{"source":"agent_002","destination":"merchant_001","amount_sats":8000}'
)

for i in "${!ROUTES[@]}"; do
  echo "Query $((i+1)): ${ROUTES[$i]}"
  
  RESPONSE=$(curl -s -X POST "$API_URL/route" \
    -H "Content-Type: application/json" \
    -H "Authorization: L402 $L402_TOKEN" \
    -d "${ROUTES[$i]}")
  
  # Extract fee and hops from response
  FEE=$(echo "$RESPONSE" | jq '.fee_sats' 2>/dev/null || echo "N/A")
  HOPS=$(echo "$RESPONSE" | jq '.hops' 2>/dev/null || echo "N/A")
  
  echo "  ✅ Fee: $FEE sats | Hops: $HOPS"
  echo ""
done

# Example 4: Save response to file
echo ""
echo "Example 4: Save response to file"
echo "=============================================================="
echo ""

OUTPUT_FILE="route_response.json"

echo "Saving response to $OUTPUT_FILE..."
curl -s -X POST "$API_URL/route" \
  -H "Content-Type: application/json" \
  -H "Authorization: L402 $L402_TOKEN" \
  -d '{
    "source": "agent_001",
    "destination": "merchant_001",
    "amount_sats": 10000
  }' > "$OUTPUT_FILE"

echo "✅ Response saved to $OUTPUT_FILE"
echo ""
echo "Content:"
cat "$OUTPUT_FILE" | jq . 2>/dev/null || cat "$OUTPUT_FILE"
echo ""

# Example 5: Pretty print response
echo ""
echo "Example 5: Pretty print response with custom formatting"
echo "=============================================================="
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/route" \
  -H "Content-Type: application/json" \
  -H "Authorization: L402 $L402_TOKEN" \
  -d '{
    "source": "agent_001",
    "destination": "merchant_001",
    "amount_sats": 10000
  }')

echo "✨ OPTIMAL ROUTE FOUND"
echo "=================================================="
echo "Route ID:          $(echo "$RESPONSE" | jq -r '.route_id' 2>/dev/null || echo 'N/A')"
echo "Number of hops:    $(echo "$RESPONSE" | jq -r '.hops' 2>/dev/null || echo 'N/A')"
echo "Estimated fee:     $(echo "$RESPONSE" | jq -r '.fee_sats' 2>/dev/null || echo 'N/A') sats"
echo "Success prob:      $(echo "$RESPONSE" | jq -r '.success_probability' 2>/dev/null || echo 'N/A')"
echo "Timestamp:         $(echo "$RESPONSE" | jq -r '.timestamp' 2>/dev/null || echo 'N/A')"
echo "=================================================="
echo ""

# Example 6: Error handling
echo ""
echo "Example 6: Error handling"
echo "=============================================================="
echo ""

echo "Querying with invalid parameters..."
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/route" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "",
    "destination": "",
    "amount_sats": 0
  }')

echo "Response (should be error):"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

echo "✅ All examples completed!"
