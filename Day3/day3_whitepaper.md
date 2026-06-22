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



# The Evaluation Toolkit
## 
Five complementary testing patterns cover the full failure surface.

<img width="691" height="586" alt="Screenshot 2026-06-22 at 11 25 59 AM" src="https://github.com/user-attachments/assets/9bcd85a2-2b8d-4aef-9e3e-3cf8eb77d245" />

<img width="751" height="330" alt="Screenshot 2026-06-22 at 11 26 30 AM" src="https://github.com/user-attachments/assets/fcebde96-6e61-4e8c-abad-e239c97e1ba3" />


# The trigger is the first gate
A skill that never fires cannot help. A skill that fires too broadly injects irrelevant context.
Vercel's production analysis8

revealed a 56% non-invocation rate for skills expected to
activate consistently. More critically, a skill stripped of its instructions scored 58%, while the
agent without the skill scored 63%. This 5-point deficit demonstrates that a poorly-designed
skill can actively subtract capability.
In this same study, Vercel also noted that a passive AGENTS.md index of project conventions
achieved a 100% pass rate against a 53% baseline. This reinforces that skills are best
reserved for narrow, action-specific workflows, whereas global context should remain in
passive, always-accessible documentation.

Now, to hit the industry-standard 90% trigger accuracy rate, your SKILL.md description, the
only thing the model sees during routing, must pass four checks:
• Testable specificity: You must write 3 positive and 3 negative triggers.
• Clarity: Ambiguous queries don't overlap with adjacent skills.
• Execution fidelity: It describes actual performance, not aspirational behavior.
• Rephrasing stability: It routes consistently regardless of how the user phrases the intent.

## Output quality and tool trajectory
Once a skill triggers, test both the final output (what the agent says) and the tool trajectory
(what the agent does) separately.
A smart way to do this is to use the Evaluation-Driven Development (EDD). Invert the
workflow by writing three JSON evaluation cases (Input, Expected Tools, Expected Output)

before drafting the SKILL.md. It forces a clear functional spec upfront. When using LLM-as-
Judge to score outputs at scale, remember two non-negotiables: swap the positions of the

reference and actual outputs to eliminate ordering bias, and calibrate against human ratings
until you hit 90% agreement.
Latitude's analysis (March 2026)9

found that final-output-only scoring passes 20% to 40%
more cases than trajectory-aware scoring. This gap represents instances where the agent

reached the correct answer via an incorrect sequence of tool calls. Acceptable in read-
only scenarios. Critical in action-allowed skills, where incorrect tool trajectories can cause

irreversible side effects.

The Google ADK eval framework10 offers three trajectory scoring modes: EXACT (exact
order), IN_ORDER (ordered subset), and ANY_ORDER (unordered subset). Trajectory
validation should align with the skill tier: read-only skills can use ANY_ORDER, action-allowed
skills require IN_ORDER or EXACT.

<img width="675" height="451" alt="Screenshot 2026-06-22 at 11 36 20 AM" src="https://github.com/user-attachments/assets/e898acea-7cb3-408f-a824-b54ac4ed042a" />


# System vs. Skill: The Evaluation Illusion
Trajectory testing evaluates the composite system of the host agent interacting with the
skill rather than the skill in isolation. When a multi-skill trajectory fails, it is often impossible
to decouple agent routing, instruction quality, or execution fidelity. To simplify calibration,
evaluate skills via a "Single-Skill Sub-Agent pattern" (Agent + 1 Skill vs. Base Agent); save
complex multi-skill co-loading for advanced production staging.
Evaluation-Driven Development (EDD)11 inverts the workflow by writing three JSON
evaluation cases (Input, Expected Tools, Expected Output) before drafting the SKILL.md. It
forces a clear functional spec upfront.This forces a clear functional specification upfront. A
minimal eval case looks like this:


<img width="668" height="391" alt="Screenshot 2026-06-22 at 11 37 50 AM" src="https://github.com/user-attachments/assets/593dfbcc-e650-466a-8026-5d13a5063272" />


## Token budget: isolation is a trap
Never evaluate a skill purely in isolation. Agents in production co-load 5 to 15 skills
simultaneously. A skill body exceeding 5,000 tokens might work perfectly alone, but it will
cause ** context rot ** when co-loaded.

## <img width="729" height="504" alt="Screenshot 2026-06-22 at 11 39 49 AM" src="https://github.com/user-attachments/assets/9da51269-575f-4d3b-9b3d-7be4b05c706c" />
The Compound Evaluation Trap: Skill vs. Agent
Trajectory testing evaluates the composite system. The skill and the host agent together. If a
test fails, avoid over-engineering the 'SKILL.md' for a specific model, which ruins portability.
Instead, isolate execution logic from routing by using a "Two-Tiered Assert Framework":
validate underlying tool code independently, and audit `SKILL.md` triggers across multiple
model families to catch brittle, architecture-locked descriptions.
MCPVerse12 noted an 18.2% accuracy drop in Claude-4-Sonnet due to tool proliferation and
context attention competition. Additionally, Chroma Research (2025)13 found that all frontier
models degrade as input grows, particularly when hindered by co-loaded noise.


<img width="741" height="502" alt="Screenshot 2026-06-22 at 11 40 02 AM" src="https://github.com/user-attachments/assets/bf66361a-d521-43d8-a719-39035f1aa861" />

Because of this, skills must graduate through strict tiers of authority:
• Read-Only: LLM-as-Judge eval; 90% trigger accuracy.
• Draft-Only (Human Review): Golden dataset of 20+ cases; human approval.
• Action-Allowed: Full adversarial red-teaming; sustained success across multiple runs (not
just a single lucky pass); no rollback events; sustained pass^k.

pass^k measures consistent, rather than occasional, success by running the evaluation $k$
times and requiring success on every run. On tau-bench (Yao et al., 2024)14, GPT-4o scored
61% on pass^1 but dropped below 25% on pass^8, demonstrating that single-run success is a
poor predictor of production reliability.
When calibrating these thresholds, two factors are critical:
1. Production Degradation: ReliabilityBench15 shows that production performance typically
drops 20% to 30% compared to offline benchmark pass@1 numbers.
2. Simulation Bias: Simulation-based evaluations can suffer from an optimistic bias of up to
9% (the "Lost in Simulation"16 finding).
Consequently, human review of representative outputs remains the ultimate validation signal
for action-allowed graduation.













