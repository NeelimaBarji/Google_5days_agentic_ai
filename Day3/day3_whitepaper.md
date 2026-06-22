# Introduction:
refer: https://drive.google.com/file/d/1Wso-CM4aAvTxFZa5wjBntKM3IVSg7PWW/view

Agent Skills are a way to equip your agent with knowledge and company context. An Agent
Skill is a folder containing a ** SKILL.md file , with scripts/, references/, and assets/
directories **.

Agent Skills are becoming the standard for cross-platform portability. But why the
sudden adoption velocity? We believe Agent Skills tackle four main friction points in AI
agent development:

-Too many instructions, worse results.
-Knowing how, not just knowing what.
-Multi-agent overload.
-portability

## What is an Agent Skill (and How to Build Your First One)
1. The first path is driven by subject matter experts, who already have institutional
knowledge written down somewhere. Think of a compliance officer with a 30-page runbook,
or an HR manager with onboarding guides for new hires. None of them need to learn to code
to write and start using a Skill. They already have the content; the only job left is to translate it
into a format the agent can use smartly.
2. The second path involves developers wrapping agentic or coded workflows into Skills.
If an agent successfully executes a non-trivial, repetitive task, you don't want it to have to
figure out the process from scratch next time. Instead, you want the agent to create a Skill
out of this successful run. In short, we are observing an emerging pattern: anything that is a
good, reusable workflow becomes a Skill, and you don't have to write it yourself, the agent
does, you review. This is already meta-skills territory, which we introduce gently here before
going deep on it in Section 6.


### Skill Anatomy & Progressive Disclosure
Before going into the different paths, let’s review the Skill anatomy. Every skill lives in its own
directory and must contain a SKILL.md. To see the full canonical structure, as defined by the
open standard at agentskills.io, let's look at a practical example.
Below is an illustrative folder for a Skill designed to conduct daily cafe preparation.
(Remember, the only mandatory file is SKILL.md. The rest is optional):

<img width="735" height="270" alt="Screenshot 2026-06-22 at 10 14 57 AM" src="https://github.com/user-attachments/assets/0da2c46d-6342-4bbe-8eec-1a827e5620bb" />

The innovative piece is the progressive disclosure. Skills load in three levels:
1. Metadata (name + description) is always in the agent's context.
2. SKILL.md body is loaded only when the skill triggers.
3. Bundled resources are loaded strictly as needed (and scripts execute without ever
polluting the token window).

This means you can have a hundred installed skills but only pay the tiny token cost for their
metadata on every turn. Let's get practical and look at how to build one.

** Path A: Translating what you already know **

<img width="680" height="487" alt="Screenshot 2026-06-22 at 10 17 24 AM" src="https://github.com/user-attachments/assets/12f443c2-3476-408d-aef1-d25b668638d5" />

Once the SKILL.md is drafted, you build out the rest of the folder. This is where progressive
disclosure starts paying off. Anything that doesn't need to be in the SKILL.md body goes
somewhere else:
• Scripts. Deterministic work (parsing exports, math, formatting) lives in scripts/. The model
decides what to do; the script does the heavy lifting.
• References. Knowledge that is only relevant once the skill is running (domain principles,
definitions, edge case handling) lives in references/ and loads on demand.
• Assets. Templates and schemas live in assets/.
Rule of thumb: if the SKILL.md is starting to get long, the next paragraph probably belongs
in references/ and not in the body.

** Path B: Crystallizing what the agent just did **
The agent completed a task successfully. You noticed the workflow was reusable. You want
the next instance of that kind of task to benefit from what was just learned.


** Wait but how does a Skill differ from MCP and AGENTS.md? **

- Skill vs. MCP. These do not compete, they compose. Model Context Protocol is about reach:
an MCP server connects the agent to an external system (Drive, Salesforce, BigQuery, or an
internal API). A Skill is about know-how: it teaches the agent how to think about a particular
kind of work. When a Skill needs data, it tells the agent to call a tool, typically one provided by
an MCP server.
- Skill vs. AGENTS.md. From one side AGENTS.md is always loaded within the project; Skills
load on demand. The cleanest setups use both. Keep AGENTS.md tight (project conventions,
stack, build commands, etc.) and if needed use it also as a router into the Skills library, with a
short catalog at the bottom that tells the agent what’s available.


## Evaluating Skills

Now you have a first skill, or maybe a small library of them. The question that immediately
follows is: how do you know they actually work? How skills fail, how to test them, and the four
conditions every skill should pass before it earns a place in your library.
An Agent Skill without a test is a hope, not a capability.

When researchers recently benchmarked 84 real-world agent tasks in SkillsBench (2025)7
,
they found that 19% performed worse with a skill than without one. These poorly designed
skills were not just neutral noise, they actively degraded capability. Fortunately, these failures
are predictable and fall into four distinct modes:
1. Trigger Failure: The wrong skill fires, or the correct one fails to fire.
2. Execution Failure: The skill triggers correctly, but produces incorrect output or errant
tool calls.
3. Token Budget Failure: A massive skill body crowds the context window, degrading
performance on unrelated turns.
4. Regression: A newly added skill overlaps with an existing one, breaking previously
working routing.

Trigger failures surface in routing logs; execution failures in output quality; token budget
failures under realistic context load; regression failures only when the full library is
exercised together.

<img width="693" height="477" alt="Screenshot 2026-06-22 at 10 36 53 AM" src="https://github.com/user-attachments/assets/a7896da4-dabf-45e5-9d1d-97dea96068d1" />











