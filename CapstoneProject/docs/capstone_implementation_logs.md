# Capstone Project Implementation Logs

## Objective
The main goal was to analyze and execute the Multi-Agent DevLoop SDLC Pipeline end-to-end using Google ADK (`python devloop.py run PROD-1`).

## Phase 1: Environment Setup & Tool Refactoring
1. **Virtual Environment**: 
   - Created a `.venv` using `uv` to manage isolated dependencies.
   - Fixed `cryptography` source compilation errors by using `uv pip install --only-binary=:all: -r requirements.txt`.
2. **Google ADK Compatibility Updates**: 
   - Noticed that `LlmAgent` in the current Google ADK version does not accept string tool names directly. 
   - Created `mcp_servers/toolsets.py` to expose factory functions returning configured `McpToolset` instances wrapping the local MCP servers (Codebase, GitLab, Jira, Security, and API tests).
   - Refactored all 10 agents in the `agents/` directory to use these strongly typed toolsets.

## Phase 2: Troubleshooting Gemini Quotas
1. **API Limitations (Free Tier)**:
   - Early test executions of `devloop.py` hit immediate `429 RESOURCE_EXHAUSTED` and `503 UNAVAILABLE (High Demand)` errors. 
   - These occurred because the `devloop.py` script aggressively iterates through agents as fast as possible, tripping Google AI Studio's 15 Requests Per Minute (RPM) limits for free accounts.
2. **Model Troubleshooting**:
   - Swapped `gemini-3.5-flash` out for `gemini-2.5-flash` and `gemini-2.0-flash`. 
   - Discovered that `gemini-2.0-flash` had a hard limit of `0 requests` for the specific API Key in use. 
   - Ultimately settled on standardizing all agents to use `gemini-2.5-flash`, which consistently tested successfully on the key.
3. **Pacing Implementation**:
   - To avoid triggering the `503 High Demand` and 429 quota exhaustion on the free tier, we modified `devloop.py` to include a manual `asyncio.sleep(40)` pause between every agent turn. This successfully spaces out the API calls.

## Phase 3: Final Execution Analysis
The pipeline successfully initializes and starts routing tickets through the multi-agent system. However, the execution was permanently halted by a `429 RESOURCE_EXHAUSTED` error.

**Root Cause**: 
Google AI Studio's Free Tier strictly imposes a maximum limit of **20 requests per day** (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`) for the `gemini-2.5-flash` model. Because the DevLoop pipeline utilizes 10 distinct agents (Analysis, Dev, Test Generator, Integration Test, Code Review, Security, MRAgent, etc.), running the pipeline just once or twice completely depletes the 20-request daily allowance. 

**Conclusion and Next Steps**:
The codebase refactoring is complete, and the ADK agents successfully compile and communicate with the local `McpToolset` endpoints. To record a full end-to-end execution of this pipeline for the capstone without hitting the 20-request cap or 503 load-balancer errors, you must use a Google Cloud project with an active billing account rather than a Free-Tier API key.
