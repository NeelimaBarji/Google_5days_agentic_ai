"""
DevLoop Orchestrator Agent
Reads a Jira ticket, classifies change type (BE/FE), and runs the full SDLC pipeline.
"""

import json
from google.adk.agents import LlmAgent, SequentialAgent
from agents.analysis_agent import analysis_agent
from agents.dev_agent import dev_agent
from agents.test_generator_agent import test_generator_agent
from agents.integration_test_agent import integration_test_agent
from agents.test_doc_agent import test_doc_agent
from agents.mr_agent import mr_agent
from agents.review_agent import review_agent
from agents.fix_agent import fix_agent
from agents.security_agent import security_agent
from mcp_servers.toolsets import get_jira_toolset
from config import GEMINI_MODEL, MCP_SECURITY_INSTRUCTION

ORCHESTRATOR_PROMPT = """
You are DevLoop Orchestrator — an autonomous SDLC agent for a Java Spring Boot + React product management system.

Given a Jira ticket ID, you will:
1. Fetch the ticket details using get_ticket tool
2. Determine change type: BACKEND (Spring Boot change) or FRONTEND (React change)
3. Set the context for downstream agents:
   - ticket_id, title, description, acceptance_criteria
   - change_type: "BACKEND" or "FRONTEND"
   - affected_files: list of files likely to change
4. Pass this context to the pipeline

Rules for classifying change type:
- BACKEND: new API endpoint, new field in entity, business logic change, DB schema change
- FRONTEND: new UI component, new filter/search, form change, display change

Always output a JSON context block:
{
  "ticket_id": "...",
  "title": "...",
  "description": "...",
  "acceptance_criteria": ["..."],
  "change_type": "BACKEND|FRONTEND",
  "affected_files": ["..."],
  "branch_name": "feature/<ticket_id_lowercase>"
}
"""

orchestrator_agent = LlmAgent(
    name="OrchestratorAgent",
    model=GEMINI_MODEL,
    instruction=ORCHESTRATOR_PROMPT + MCP_SECURITY_INSTRUCTION,
    tools=[get_jira_toolset(["get_ticket"])],
    output_key="pipeline_context",
)

devloop_pipeline = SequentialAgent(
    name="DevLoopPipeline",
    description="End-to-end SDLC pipeline: Analysis → Dev → Test → MR → Review → Fix → Security",
    sub_agents=[
        orchestrator_agent,
        analysis_agent,
        dev_agent,
        test_generator_agent,
        integration_test_agent,
        test_doc_agent,
        mr_agent,
        review_agent,
        fix_agent,
        security_agent,
    ],
)
