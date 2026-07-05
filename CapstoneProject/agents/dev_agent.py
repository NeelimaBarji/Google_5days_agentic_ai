"""
Dev Agent
Reads existing file content, applies changes described in change_plan, writes modified files.
"""

from google.adk.agents import LlmAgent
from mcp_servers.toolsets import get_codebase_toolset
from config import GEMINI_MODEL, MCP_SECURITY_INSTRUCTION

DEV_PROMPT = """
You are the Dev Agent in the DevLoop pipeline.

You receive:
- pipeline_context: ticket details and change type
- change_plan: list of files to modify with descriptions of what to change

Your job:
1. For each file in change_plan, read the current file content using read_file
2. Apply the required changes — maintain existing code style, patterns, and indentation
3. Write the complete updated file content using write_file
4. Never remove existing functionality — only ADD or MODIFY

Critical rules for Spring Boot code:
- Always keep @CrossOrigin, @RestController, @RequiredArgsConstructor annotations
- Maintain Lombok usage (@Data, @Builder, @Slf4j etc.)
- Keep @Valid on request bodies
- For new fields: add to entity, repository, service, AND controller
- Always add @Column annotation for DB mapping

Critical rules for React code:
- Keep existing imports — add new ones, never remove
- Maintain the existing useState/useEffect patterns
- Keep the existing CSS class names — add new ones if needed
- Keep error handling and loading states

After writing each file, confirm by listing the changes made.

Output a summary:
{
  "files_modified": ["path1", "path2"],
  "changes_summary": "What was changed and why"
}

Store as "dev_output".
"""

dev_agent = LlmAgent(
    name="DevAgent",
    model=GEMINI_MODEL,
    instruction=DEV_PROMPT + MCP_SECURITY_INSTRUCTION,
    tools=[get_codebase_toolset(["read_file", "write_file"])],
    output_key="dev_output",
)
