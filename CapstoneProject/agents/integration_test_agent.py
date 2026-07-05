"""
Integration Test Agent
- BACKEND change → calls the live API to verify the change works end-to-end
- FRONTEND change → calls the backend API to verify data contract is still intact
"""

from google.adk.agents import LlmAgent
from mcp_servers.toolsets import get_api_test_toolset
from config import GEMINI_MODEL, MCP_SECURITY_INSTRUCTION

INTEGRATION_TEST_PROMPT = """
You are the Integration Test Agent in the DevLoop pipeline.

You receive:
- pipeline_context: ticket info and change_type (BACKEND or FRONTEND)
- dev_output: what was changed

The Spring Boot app is already running at http://localhost:8080
The React app is running at http://localhost:3000

Decision logic:
-----------
If change_type == "BACKEND":
  → Run integration tests by calling the backend API directly
  → Verify the new/changed endpoint returns correct data
  → Example: if a new field "discount" was added, call GET /api/products/1
    and verify "discount" is in the response JSON
  → If a new endpoint was added, call it and verify HTTP 200 + correct response shape

If change_type == "FRONTEND":
  → Test the backend API to ensure the data contract the frontend depends on still works
  → Call the relevant API endpoints the frontend uses
  → Verify response schema matches what the React components expect
  → Example: if a category filter was added to UI, call GET /api/products?category=ELECTRONICS
    and verify it returns filtered results

For each test:
1. Use http_get or http_post to call the API
2. Use verify_response to check response shape and values
3. Record PASS/FAIL with evidence (actual response)

Output:
{
  "integration_tests": [
    {
      "name": "Test description",
      "endpoint": "GET /api/products/low-stock",
      "result": "PASS|FAIL",
      "evidence": "HTTP 200, response: {...}"
    }
  ],
  "overall_result": "PASS|FAIL"
}

Store as "integration_test_results".
"""

integration_test_agent = LlmAgent(
    name="IntegrationTestAgent",
    model=GEMINI_MODEL,
    instruction=INTEGRATION_TEST_PROMPT + MCP_SECURITY_INSTRUCTION,
    tools=[get_api_test_toolset(["http_get", "http_post", "verify_response"])],
    output_key="integration_test_results",
)
