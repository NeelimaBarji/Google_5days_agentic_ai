# 1. Introduction
Google Antigravity is an agentic development platform that is designed to help you develop in this era of agents. Antigravity serves as your AI agents' central command center, providing a unified platform to launch, monitor, and orchestrate their activities.

In this codelab, we will first learn about Agent Skills, a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. You will be able to learn what Agent Skills are, their benefits and how they are constructed. You will then build multiple Agent Skills ranging from a Git formatter, template generator, tool code scaffolding and more, all usable within Antigravity.

Prerequisites:

Antigravity installed and configured.
Basic understanding of Google Antigravity. It is recommended to complete the codelab: Getting Started with Google Antigravity.
Back


# 2. Why Skills
Modern AI agents have evolved from simple listeners to complex reasoners that integrate with local file systems and external tools (via MCP servers). However, indiscriminately loading an agent with entire codebases and hundreds of tools leads to Context Saturation and "Tool Bloat." Even with large context windows, dumping 40–50k tokens of unused tools into active memory causes high latency, financial waste, and "context rot," where the model becomes confused by irrelevant data.

## The Solution: Agent Skills
To solve this, Anthropic introduced Agent Skills, shifting the architecture from monolithic context loading to Progressive Disclosure. Instead of forcing the model to "memorize" every specific workflow (like database migrations or security audits) at the start of a session, these capabilities are packaged into modular, discoverable units.

## How It Works
The model is initially exposed only to a lightweight "menu" of metadata. It loads the heavy procedural knowledge (instructions and scripts) only when the user's intent specifically matches a skill. This ensures that a developer asking to refactor authentication middleware gets security context without loading unrelated CSS pipelines, keeping the context lean, fast, and cost-effective.
