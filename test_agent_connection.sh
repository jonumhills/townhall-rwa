#!/bin/bash

# Test Elasticsearch Agent Connection
# This script mimics exactly what the frontend ChatAssistant.jsx does

echo "🧪 Testing Elasticsearch Agent Builder Connection"
echo "=================================================="
echo ""

KIBANA_ENDPOINT="https://townhall-e15ba3.kb.us-east-1.aws.elastic.cloud"
ELASTIC_API_KEY="b0pzN0Rad0JhUkI2dk15TV84M1c6RVh3b3BiYW4yZVVHamZzQU9aVEFpUQ=="
ELASTIC_AGENT_NAME="townhall_city_analyst"

echo "Configuration:"
echo "  Endpoint: $KIBANA_ENDPOINT"
echo "  Agent: $ELASTIC_AGENT_NAME"
echo "  API Key: ${ELASTIC_API_KEY:0:20}..."
echo ""

TEST_MESSAGE="Show me the top 5 developers"

echo "📤 Sending Test Query: '$TEST_MESSAGE'"
echo ""

curl -s -w "\n\n📊 HTTP Status: %{http_code}\n" \
  -X POST "${KIBANA_ENDPOINT}/api/agent_builder/converse" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
  -H "kbn-xsrf: true" \
  -d "{
    \"input\": \"${TEST_MESSAGE}\",
    \"agent_id\": \"${ELASTIC_AGENT_NAME}\"
  }" | jq '.' 2>/dev/null || cat

echo ""
echo "✅ Test Complete!"
echo ""
echo "Expected Response Structure:"
echo "  {"
echo "    \"conversation_id\": \"...\","
echo "    \"status\": \"completed\","
echo "    \"response\": {"
echo "      \"message\": \"...agent's response...\""
echo "    }"
echo "  }"
