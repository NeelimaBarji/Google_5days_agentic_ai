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


<img width="746" height="502" alt="Screenshot 2026-06-23 at 9 56 45 AM" src="https://github.com/user-attachments/assets/a63e7eac-005b-4ae2-8b39-4e98412bdfc3" />


# 3. Agent Skills and Antigravity
In the Antigravity ecosystem, the Skills act as specialized training modules that bridge the gap between the generalist models and your specific context. They allow the agent to "equip" a defined set of instructions and protocols—such as database migration standards or security checks—only when a relevant task is requested. By dynamically loading these execution protocols, Skills effectively transform the AI from a generic programmer into a specialist that rigorously adheres to an organization's codified best practices and safety standards.

## What is a Skill in Antigravity?
In the context of Google Antigravity, a Skill is a directory-based package containing a definition file (SKILL.md) and optional supporting assets (scripts, references, templates).

It is a mechanism for on-demand capability extension.

On-Demand: Unlike a System Prompt (which is always loaded), a Skill is only loaded into the agent's context when the agent determines it is relevant to the user's current request. This optimizes the context window and prevents the agent from being distracted by irrelevant instructions. In large projects with dozens of tools, this selective loading is crucial for performance and reasoning accuracy.
Capability Extension: Skills can do more than just instruct; they can execute. By bundling Python or Bash scripts, a Skill can give the agent the ability to perform complex, multi-step actions on the local machine or external networks without the user needing to manually run commands. This transforms the agent from a text generator into a tool user.

### Skills v/s the Ecosystem (Tools, Rules and Workflows)
While Model Context Protocol (MCP) functions as the agent's "hands"—providing heavy-duty, persistent connections to external systems like GitHub or PostgreSQL—Skills act as the "brains" that direct them.

MCP handles the stateful infrastructure, whereas Skills are lightweight, ephemeral task definitions that package the methodology for using those tools. This serverless approach allows agents to execute ad-hoc tasks (like generating changelogs or migrations) without the operational overhead of running persistent processes, loading the context only when the task is active and releasing it immediately after.

Skills are agent-triggered: the model automatically detects the user's intent and dynamically equips the specific expertise required. This architecture allows for powerful composability; for example, a global Rule can enforce the use of a "Safe-Migration" Skill during database changes, or a single Workflow can orchestrate multiple Skills to build a robust deployment pipeline.

# 4. Creating Skills
Creating a Skill in Antigravity follows a specific directory structure and file format. This standardization ensures that skills are portable and that the agent can reliably parse and execute them. The design is intentionally simple, relying on widely understood formats like Markdown and YAML, lowering the barrier to entry for developers wishing to extend their IDE's capabilities.

## Directory Structure
A typical Skill directory looks like this:

<img width="805" height="332" alt="Screenshot 2026-06-23 at 9 59 55 AM" src="https://github.com/user-attachments/assets/498435e4-c153-4f84-ac7b-44a631c24fd8" />


### The SKILL.md Definition File
The SKILL.md file is the brain of the Skill. It tells the agent what the skill is, when to use it, and how to execute it.

It consists of two parts:

YAML Frontmatter
Markdown Body.
YAML Frontmatter

This is the metadata layer. It is the only part of the skill that is indexed by the agent's high-level router. When a user sends a prompt, the agent semantic-matches the prompt against the description fields of all available skills.

---
name: database-inspector
description: Use this skill when the user asks to query the database, check table schemas, or inspect user data in the local PostgreSQL instance.
---


#### Key Fields:

name: This is not mandatory. Must be unique within the scope. Lowercase, hyphens allowed (e.g., postgres-query, pr-reviewer). If it's not provided, it will default to the directory name.
description: This is mandatory and the most important field. It functions as the "trigger phrase." It must be descriptive enough for the LLM to recognize semantic relevance. A vague description like "Database tools" is insufficient. A precise description like "Executes read-only SQL queries against the local PostgreSQL database to retrieve user or transaction data. Use this for debugging data states" ensures the skill is picked up correctly.


##### The Markdown Body

The body contains the instructions. This is "prompt engineering" persisted to a file. When the skill is activated, this content is injected into the agent's context window.

The body should include:

Goal: A clear statement of what the skill achieves.
Instructions: Step-by-step logic.
Examples: Few-shot examples of inputs and outputs to guide the model's performance.
Constraints: "Do not" rules (e.g., "Do not run DELETE queries").


<img width="793" height="403" alt="Screenshot 2026-06-23 at 10 02 10 AM" src="https://github.com/user-attachments/assets/a781f889-9d0f-47c7-9cae-83bfe9eb5493" />

#### Script Integration
One of the most powerful features of Skills is the ability to delegate execution to scripts. This allows the agent to perform actions that are difficult or impossible for an LLM to do directly (like binary execution, complex mathematical calculation, or interacting with legacy systems).

Scripts are placed in the scripts/ subdirectory. The SKILL.md references them by relative path.


# 5. Authoring Skills

The goal of this section is to build out Skills that integrate into Antigravity and progressively show various features like resources / scripts / etc.

You can download the Skills from the Github repo here: https://github.com/rominirani/antigravity-skills.

Before we understand how each of these skills were built, let us see how we configure them and make them available within the Antigravity suite of products. The folders below are applicable at the time of publishing this lab.

## Using Antigravity or Antigravity CLI

Skills can be defined at two scopes, allowing for both project-specific and user-specific i.e. global skills.:

Global Scope (~/.gemini/config/skills/): Available across all Antigravity products (Antigravity, Antigravity IDE, Antigravity CLI) and projects. These skills are available across all projects on the user's machine. This is suitable for general utilities like "Format JSON," "Generate UUIDs," "Review Code Style," or integration with personal productivity tools.
Project/Workspace Scope (<project-root>/.agents/skills/): This would make the skill available only within a specific project. This is ideal for project-specific scripts, such as deployment to a specific environment, database management for that app, or generating boilerplate code for a proprietary framework.

## Installing the Skills in either Antigravity or Antigravity CLI
For this tutorial, all we need to do is the following steps (you can do it your way too):

Step 1: Do a git clone of https://github.com/rominirani/antigravity-skills

Step 2: Now depending on whether you are using Antigravity or Antigravity CLI, you can navigate into the antigravity-skills/skills_tutorial folder.

Step 3: You will find a set of skills, packaged into their respective folders. Copy the following 4 folders:

git-commit-formatter
license-header-adder
database-schema-validator
json-to-pydantic
into the targeted skills folder for the product (project scope or global scope).

Step 4: If you are using Antigravity or Antigravity CLI , copy it to the <project-root>/.agents/skills/ (project scope).

If you have launched Antigravity, you can ask a simple question "What skills are available?" and it responds with the same. You can see the 4 skills that are listed there. You might have additional skills too, if you have installed them in your environment.

<img width="820" height="641" alt="Screenshot 2026-06-23 at 10 09 23 AM" src="https://github.com/user-attachments/assets/edca97a0-d5fb-4306-9c8b-33eaafd6b0cd" />







