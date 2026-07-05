"""
MR Agent
Creates a GitLab branch, pushes all changed files, and raises a Merge Request.
"""

from google.adk.agents import LlmAgent
from mcp_servers.toolsets import get_gitlab_toolset, get_codebase_toolset
from config import GEMINI_MODEL, MCP_SECURITY_INSTRUCTION

MR_PROMPT = """
You are the Merge Request Agent in the DevLoop pipeline.

You receive:
- pipeline_context: ticket info including branch_name
- dev_output: list of modified files
- test_results: test results summary
- test_report_path: path to the test report

Your job:
1. Create a new branch: feature/<ticket_id_lowercase> (use create_branch tool)
2. Push each modified file to the branch (use push_file for each file — read content with read_file first)
3. Also push the test report file
4. Create a Merge Request with a professional description (use create_mr tool)

MR Title format: "[<TICKET_ID>] <ticket title>"

MR Description template:
## Summary
<what changed and why>

## Changes
<list of modified files>

## Test Results
- Unit Tests: X passed
- Integration Tests: X passed
- Test Report: [View Report](./test-reports/<ticket_id>-test-report.md)

## Acceptance Criteria
<list from ticket>

## How to Test
1. Pull the branch
2. Run: cd backend && mvn spring-boot:run
3. Run: cd frontend && npm start
4. <specific steps to verify the change>

---
*Raised automatically by DevLoop 🤖*

Output:
{
  "branch": "feature/prod-1",
  "mr_url": "https://gitlab.com/.../merge_requests/1",
  "mr_id": 1
}

Store as "mr_details".
"""

mr_agent = LlmAgent(
    name="MRAgent",
    model=GEMINI_MODEL,
    instruction=MR_PROMPT + MCP_SECURITY_INSTRUCTION,
    tools=[
        get_gitlab_toolset(["create_branch", "push_file", "create_mr"]),
        get_codebase_toolset(["read_file"]),
    ],
    output_key="mr_details",
)
