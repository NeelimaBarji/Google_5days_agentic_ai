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

## What "eval coverage" means

A skill achieves complete eval coverage by satisfying four conditions mapped directly to the
primary failure modes:
• Trigger Failure: Verifying trigger behavior with both positive (should fire) and negative
(should not fire) test cases.
• Execution Failure: Ensuring correct outputs across a representative range of
expected inputs.
• Regression: Confirming that adding the skill causes zero performance drops in the
existing library.
• Token Budget Failure: Bounding the skill's token footprint to ensure it does not degrade
performance on unrelated turns.
This checklist governs graduation; failure on any single condition holds the skill in the draft
tier, regardless of its happy-path performance. Once verified, the skill and its accompanying
eval suite are ready for production deployment (detailed in Section 5).

# 5. From Prototype to Production

Sections 1 to 4 covered what skills are, how to write one, and how to evaluate them. This
section is about what changes when you put a working prototype in front of a real customer.
The short version: the model is no longer the interesting part, and skills are the engineering
primitive that lets you ship reliably.
Google's Agents CLI17 in Agent Platform is a CLI and skills package for building, evaluating,
and deploying AI agents on Google Cloud. Agents are built with Google's Agent Development
Kit (ADK) and Agents CLI handles everything around it: scaffolding, evaluation, deployment,
and observability.

<img width="698" height="490" alt="Screenshot 2026-06-22 at 12 28 08 PM" src="https://github.com/user-attachments/assets/dfe685dd-6571-424b-9c10-a3290ac6955b" />

The working example points to three properties that generalize beyond Google’s setup:
• The expertise lives in the skills, not the runtime. The runtime is commoditized; the
seven skills are the durable asset.
• The skills package composes with what you already use. Install the skills and
your existing coding tool gains new capabilities; the same pattern to aim for internally:
capabilities that compose into existing tooling, not another portal.
• The full lifecycle ships as skills. Scaffold, build, evaluate, deploy, publish, observe. Every
stage that once needed its own tooling now fits the skills format.

### What's actually inside an agent runtime
Underneath the framework, the agent loop has converged across vendors: the runtime
maintains a conversation, calls the model, executes tools, reads files, returns a response.
What’s striking inside one of these runtimes is how little of the code is about reasoning.

<img width="708" height="441" alt="Screenshot 2026-06-22 at 12 32 55 PM" src="https://github.com/user-attachments/assets/e6eafc2e-fc1e-44d1-8129-dad51002eb97" />


### Why skills are the unit of improvement
The naive theory of agent improvement is that better models produce better agents. In
production, the model is the infrastructure and skills are the primitive that lets improvements
ship. Each new skill is a small, owned, testable unit of capability (as we set up in Section
1). When a new edge case appears, it takes editing one SKILL.md; the agent's effective
capability grows without the challenges of monolithic prompt engineering.
Three properties of skills make this work:
• They are conditional. Loaded only when their description matches the task.
• They are composable. One skill can call tools from another, or chain downstream, without
either knowing about the other (Section 7 develops the composition story in depth).
• They are owned. Each lives in a versioned folder with a clear author, so improvement is
distributed rather than bottlenecked through a central platform team.


<img width="684" height="404" alt="Screenshot 2026-06-22 at 12 36 32 PM" src="https://github.com/user-attachments/assets/345f46f6-6f05-46ce-877c-7e6778f7bcdb" />


#### The failure mode that breaks demos: context overflow
The most ** common failure mode of agents in production is not hallucination. It is context
overflow **: the model receiving more context than it can effectively use, and degrading silently
before the operator notices. Two strands of research ground this:

<img width="725" height="518" alt="Screenshot 2026-06-22 at 12 45 32 PM" src="https://github.com/user-attachments/assets/58777a5b-6922-4215-b1d7-75461a144770" />

## What this means for the token budget
Progressive disclosure, covered in Section 2, is the architectural answer: metadata for every
skill loads at startup, a skill’s body loads only when its description matches, and supporting
files load only when the body references them.
The math is worth showing. Consider an agent with fifty distinct workflows. As a single
system prompt, it loads 15,000 tokens every turn. As a skills library, it loads ~4,000 tokens
of descriptions plus the ~2,000-token body of the one active skill with ~6,000 tokens total,
with the other forty-nine bodies on disk. Anthropic has published examples where converting
a workflow to skills cut active context from roughly 150,000 tokens to 2,000, a reduction of
more than 98 percent.
<img width="681" height="346" alt="Screenshot 2026-06-22 at 3 18 09 PM" src="https://github.com/user-attachments/assets/c48d47ea-be98-4e03-911b-84c912fc31ad" />

Three practical implications follow:
• Capacity is the wrong metric. A 1M-token window can show significant degradation at
50K tokens.
• Active context is a budget, not a vessel. Every token in front of the model takes
attention from every other. Treat the system prompt the way infra teams treat memory: a
finite resource, allocated deliberately.
• Skills resolve the constraint. They keep active context small while keeping available
capability effectively unbounded.
Once a team has a working library, the questions shift from maintaining a single skill to
evolution, composition, and the larger ecosystem.


# 6. On Meta-Skills and Self-Improving Skills

So far, every skill in this document has been written by a human. A domain expert sits down,
drafts a SKILL.md, tests it, ships it. That's the right place to start. But once you have a
working library, the natural next question is: can the agent help write, evaluate, and improve
skills too?
This is the meta-skills territory. Skills whose job is to author, evaluate, or improve other skills.
In practice, these "meta-skills" fall into four buckets:

1. Authoring. Skills that take a description of a workflow and produce a draft SKILL.md.
Google's ADK21 has a "skill factory" pattern that does this through its SkillToolset.
Anthropic ships a skill-creator Skill22 that walks you through creation, evaluation,
and tuning.
2. Assisted authoring from traces. Instead of asking a human to describe a workflow,

watch the agent do it successfully a few times, then turn that trace into a skill. The skill-
creator workflow supports this directly through trace-based harvesting. The human's

job shifts from writing the skill to confirming that the harvested version captures the
right steps.

<img width="697" height="340" alt="Screenshot 2026-06-22 at 3 20 48 PM" src="https://github.com/user-attachments/assets/2a36dbab-0957-493e-97c3-8b2ea8cf8d43" />

3. Improvement. Skills that take an existing skill plus a set of failing evaluation cases and
propose edits. Saboo's SkillOptimizer24 and Anthropic's description-optimization loop are
both examples. Another is Karpathy's autoresearch pattern25, where an agent proposes
a change to a target file, runs a bounded experiment, and keeps the change only if a
metric improves.

<img width="720" height="277" alt="Screenshot 2026-06-22 at 3 22 58 PM" src="https://github.com/user-attachments/assets/9af98f98-01ba-4d6e-8e43-2ed5f7497a11" />

4. Library evolution. Skills that grow the library over time, the way Voyager grew its own
Minecraft skill library26. The agent finishes a task it had no skill for, notices that it just

solved a recurring problem, and proposes adding a new skill to cover it. Schmid's self-
learning-skill27 is a community reference implementation of this pattern.

## Where this falls apart?
Meta-skills only work if your evaluation suite is good. An agent that's allowed to edit its own
skills will happily optimize for whatever metric you point it at, including metrics that are easy
to game. The Section 4 evaluation work is what keeps this honest. Without solid trigger
accuracy tests, regression tests, and human spot-checks, an autonomous improvement loop
will quietly make your library worse while reporting that it's getting better.
A few habits that have held up:
• Anything an agent writes enters the library at the draft tier, regardless of how
confident the meta-skill is. It graduates through the same Read / Draft / Act ladder from
Section 4 as any human-written skill.

• Keep a human in the loop for the first few edits. Even when the metric clearly improves,
scan the diff. The kind of mistake an agent makes (overfitting the description to a few
test cases, breaking a downstream skill it didn't know existed) is exactly the kind a human
catches in 30 seconds.
• Don't start with meta-skills. Get the manual authoring loop working first. The fastest
way to get a bad library is to point an agent at an empty folder and ask it to generate
fifty skills.

# 7. Composing and Packaging Skills
Real workflows do not fit inside a skill. The composition problem is how skills reference each
other, pass state, and avoid circular dependencies.
Passing raw LLM outputs between isolated skills in a monolithic system is ineffective: state
gets obfuscated, execution becomes non-deterministic, and debugging is hard. Agent
architecture has evolved from naive prompt chaining to predictable orchestration.

Execution Routing: DAG Orchestration
Early architectures proved brittle and susceptible to compounding errors when early stages
hallucinated. The industry solution is Directed Acyclic Graph (DAG) orchestration.
• Decoupled State: State routing in a DAG architecture does not rely on accumulating
execution history within the LLM's prompt.
• File Message Bus: The DAG controller orchestrates handoffs by passing structured
schema references between subagent nodes.
• Protected Attention: Abstracting the payload from the model's text input prevents
context window bloat and preserves the model's capacity.

Environment Packaging: Capability Profiles
Activating every skill degrades natural language routing and overwhelms the context
window. Architects should utilize tools to manage "Capability Profiles," which function as
specialized personas tailored to specific execution states. A profile acts as a modular tool
bundle defining:
• Active skills and tool access.
• System instructions and operational guardrails.
• Automated workflows and subagent topologies.
• LLM parameters, such as model choice and temperature.
During execution, the orchestration layer unloads previous system instructions and flushes
stale variables before swapping the new Capability Profile into memory. This strict teardown
and rebuild process prevents context loss.

Populating the Graph: The Canonical Skill Taxonomy
To build DAG, discrete engineering capabilities map to specific node functions within an
execution graph nodes:
• Generator: Convert user intent into structured artifacts.
• Reviewer & Gate: Deterministic gates blocking execution if validation fails.
• Pipeline: Orchestrate linear paths within the broader DAG environment.
• Inversion & Recovery: Force the agent to clarify assumption before execution.
• Domain Context Wrappers: Act as reference nodes teaching domain conventions.

### Context Debt and Shifting Intelligence Left
Skills burn model attention, which is a scarce resource. When authors attempt deterministic
behavior at runtime by bloating skill descriptions (e.g., "ALWAYS DO X"), they accumulate
Context Debt. Models learn to ignore these capitalized imperatives, exactly as a human
developer ignores a wall of unreadable warning text.
The engineering best practice is to Shift Intelligence Left. Instead of hoping an LLM
correctly interprets complex rules at runtime, distill subjective judgments into skills. By
pushing logic out of the LLM's prompt and into standard, testable scripts, you reduce the
chaotic surface area of your application.

<img width="673" height="389" alt="Screenshot 2026-06-22 at 3 30 44 PM" src="https://github.com/user-attachments/assets/2415c48c-77e2-43c2-bbb0-b735b4d62a6a" />

### Actionable Best Practices
• Write Software, Not Rules: Replace negative LLM instructions with deterministic
software constraints that make invalid actions impossible.
• Implement Progressive Disclosure: Load complex instructions dynamically only when
the skill is explicitly invoked.
• Decouple State: Never use the LLM context window as a database. Pass only URIs or
pointers to the subagents via the file system or message bus.


# 8. How to Decide Among the Hundreds
of Skills That Exist
By early 2026, public skill marketplaces had crossed 40,000 listings, with the leading
platform reporting tens of thousands of new skills published in the first weeks of January
alone. At Google Cloud Next 2026, Google launched its official Agent Skills repository at
github.com/google/skills, with skills installable via npx skills install github.
com/google/skills for use across Antigravity CLI, and any other coding agent that
supports the Skills standard. The Anthropic skills repository, the Google ADK skill library, the
Google official skills repository, and community marketplaces such as awesome-llm-apps
now host more skills than any practitioner could review individually. The selection problem is
real and growing.

Three heuristics help.
1. First, prefer first-party skills for vendor-specific tools. Google's BigQuery skill, the official
Stripe skill, anything written by the people who built the underlying system. They will be
more correct and more maintained than community alternatives.
2. Second, pin everything you depend on. Community skills evolve, and an unpinned
dependency that worked yesterday can fail tomorrow.
3. Third, audit before adopting. A skill is code that runs in your context. Treat it like any other
dependency, with the same supply-chain hygiene.
Not all sources are equal. Three categories of skill source exist in early 2026, and the right
operational stance is different for each:

<img width="697" height="397" alt="Screenshot 2026-06-22 at 3 31 52 PM" src="https://github.com/user-attachments/assets/1c73d55c-0488-4aa5-89db-636e2a68d71c" />

# 9. Conclusion
We began this whitepaper by looking at a surprisingly simple concept: a folder containing
a markdown file and a few optional scripts. Yet, this lightweight structure, the Agent Skill, is
fundamentally reshaping how we build AI Agents. It finally provides foundation models with

true, testable procedural memory, allowing them to remember how to execute tasks step-by-
step. By relying on the magic of progressive disclosure, skills solve the problem of context

rot. A single, general-purpose agent can now seamlessly access many specialized workflows
without choking its token budget.
The pattern we keep coming back to in this paper is that the format is deliberately small so
that the interesting work happens around it, not inside it. Evaluating Skills under realistic
co-loaded conditions is interesting. Composing Skills into workflows without using the
context window as a message bus is interesting. Letting agents draft Skills from successful
traces, with humans reviewing rather than authoring, is interesting. Encoding two decades
of institutional knowledge into a versioned, testable, governable library is interesting.
All of these are now tractable in a way they weren't twelve months ago, because the
primitive exists.
Throughout this paper, we have also tried to be specific about what's settled, what's still
emerging, and what's likely to change. The format is settled: agentskills.io is now an open
standard with adoption across every major coding agent, AI chatbot, and agent framework
that matters. The architecture around it is still emerging: evaluation under co-loaded
conditions, Skills-library-level optimization, agent-driven Skill creation, and the governance
patterns that make all of this safe at scale.

If you are starting today, our suggestion is the one we've made throughout: start small, start
with knowledge you already have, treat Skills as code, measure what you ship, and don't
reach for a multi-agent architecture when a Skills will do. The teams that figure this out now
will build cleaner systems than the teams that wait for the industry consensus to catch up.
The format is settled. The work is just beginning.





















