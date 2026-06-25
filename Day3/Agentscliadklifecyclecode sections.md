# Vibe Coding AI Agents: Managing the Agent Lifecycle with Agents CLI and ADK 2.0

> Sections containing code blocks, extracted from:
> https://codelabs.developers.google.com/agents-cli-adk-lifecycle
>
> Source content licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (text) and [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) (code samples).

---

## 2. Set up Authentication & Environment

### Option 1: Gemini API Key (Google AI Studio)

If you are using a standard Gemini API key (which you can obtain from Google AI Studio), export it in your IDE terminal session:

```bash
export GEMINI_API_KEY="your_api_key_here"
export GOOGLE_GENAI_USE_ENTERPRISE=FALSE
```

### Option 2: Google Cloud Application Default Credentials

If you are using Vertex AI on Google Cloud, authenticate with Google Cloud Application Default Credentials (ADC) and set your active Google Cloud project:

```bash
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=REPLACE-WITH-YOUR-PROJECT_ID # Replace with your project ID
export GOOGLE_CLOUD_LOCATION=REPLACE-WITH-LOCATION # Replace the location
```

---

## 3. Set up Agents CLI & Skills

Open a terminal and run:

```bash
uvx google-agents-cli setup
```

**Expected Output (trimmed):**

```text
█▀█ █▀▀ █▀▀ █▄ █ ▀█▀ █▀ █▀▀ █ █
█▀█ █▄█ ██▄ █ ▀█ █ ▄█ █▄▄ █▄ █

Your coding agent just got an upgrade.

1. Authentication
─────────────────
✓ Authenticated with Google Cloud

2. CLI Installation
───────────────────
▸ uv tool install google-agents-cli
✓ Installed google-agents-cli

3. Skills Installation
──────────────────────
▸ npx -y skills add https://github.com/google/agents-cli -y --all -g
◇ Found 7 skills
~/.agents/skills/google-agents-cli-adk-code
~/.agents/skills/google-agents-cli-deploy
~/.agents/skills/google-agents-cli-eval
~/.agents/skills/google-agents-cli-observability
~/.agents/skills/google-agents-cli-publish
~/.agents/skills/google-agents-cli-scaffold
~/.agents/skills/google-agents-cli-workflow
```

---

## 4. Create your Agent Project

Prompt Antigravity:

```text
Use ADK 2.0 to create a new graph workflow agent project called
customer-support-agent. I don't want to deploy this agent, so you can skip
the deployment files. The workflow should act as a customer support
representative for a shipping company. It should first classify if the user
query is related to shipping (rates, tracking, delivery, returns) or
unrelated. If it is related to shipping, route to a shipping FAQ agent to
answer the question. If it is unrelated, route to a node that politely
declines to answer.
```

Antigravity automatically runs the scaffolding command:

```bash
agents-cli scaffold create customer-support-agent --prototype --yes
```

---

## 5. Explore the Agent Code

Ask Antigravity to explain the generated code:

```text
Read and explain the project structure of my new agent project. Walk me
through how `app/agent.py` is configured, highlighting the role of the
tools, nodes, edges, and the root Workflow.
```

Example generated code:

```python
# app/agent.py

from __future__ import annotations

from typing import Any, Literal

from google.adk.agents.context import Context
from google.adk.apps.app import App
from google.adk.events.event import Event
from google.adk.workflow import Edge
from google.adk.workflow import Workflow
from google.adk.workflow.agents.llm_agent import LlmAgent
from google.adk.workflow.node import node
from pydantic import BaseModel
from pydantic import Field


class InquiryCategory(BaseModel):
  category: Literal['shipping', 'unrelated'] = Field(
      description=(
          'Determine if the user query is related to shipping (rates, tracking,'
          ' delivery times, returns) or unrelated.'
      )
  )


def save_query(node_input: str):
  """Saves user query in state for downstream nodes."""
  yield Event(data=node_input, state={'user_query': node_input})


categorize_agent = LlmAgent(
    name='categorize',
    model='gemini-3.1-flash-lite',
    instruction='You are an expert classifier. Categorize the user query.',
    output_key='inquiry_category',
    output_schema=InquiryCategory,
)


@node
def route_inquiry(ctx: Context, node_input: Any):
  """Routes the workflow based on the classified category."""
  category_data = ctx.state.get('inquiry_category', {})
  category = category_data.get('category', 'unrelated')
  query = ctx.state.get('user_query', '')
  yield Event(data=query, route=category)


faq_agent = LlmAgent(
    name='shipping_faq',
    model='gemini-3.1-flash-lite',
    instruction="""You are a customer support representative for a shipping company. Answer user questions based ONLY on the shipping FAQ below. Do not answer questions outside of the FAQ.

    SHIPPING FAQ:
    - Rates: Standard shipping is $5.99. Express shipping is $12.99. Orders
      over $50 qualify for free standard shipping.
    - Tracking: You can track your order by entering your tracking number on
      our website's tracking page.
    - Delivery Times: Standard delivery takes 3-5 business days. Express
      delivery takes 1-2 business days.
    - Returns: We offer free returns within 30 days of delivery. Please make
      sure the item is in its original condition.
    """,
)


@node
def handle_unrelated(ctx: Context, node_input: Any):
  """Handles unrelated inquiries politely."""
  yield Event(
      data=(
          'I am sorry, I am a shipping customer support assistant and can only'
          ' answer questions related to our shipping FAQ.'
      )
  )


root_agent = Workflow(
    name='customer_support_workflow',
    edges=[
        *Edge.chain('START', save_query, categorize_agent, route_inquiry),
        (route_inquiry, faq_agent, 'shipping'),
        (route_inquiry, handle_unrelated, 'unrelated'),
    ],
)

app = App(
    name='customer_support_agent',
    root_agent=root_agent,
)
```

> **Note:** The codelab source has a couple of stray typos in this snippet (`model='gemini-3.1-flash-lite''` with an extra quote, and `` `gemini-3.1-flash-lite' `` in the Key Concepts prose with a mismatched quote). They've been left in below as-is for the literal export, but corrected to `model='gemini-3.1-flash-lite',` in the code block above so it's actually runnable.

---

## 6. Automated Linting

Prompt Antigravity:

```text
Run linting on my agent project to verify its health.
```

Antigravity executes this behind the scenes:

```bash
agents-cli lint
```

---

## 7. Interactive Testing with the Playground

Prompt Antigravity:

```text
Launch the local development playground for my agent.
```

Antigravity starts the local development server:

```bash
agents-cli playground
```

Default URL: `http://127.0.0.1:8080/dev-ui/?app=app`

Test message:

```text
How much is standard shipping?
```

Test message (unrelated query):

```text
What is the weather like?
```

### Test Real-Time Auto-Reloading

Modify the `faq_agent` instruction by asking Antigravity:

```text
Modify the faq_agent instruction in app/agent.py to make the shipping rates
response more playful and enthusiastic. Add some emojis and highlight the
free shipping threshold.
```

Then send a new message to test auto-reloading:

```text
How much is standard shipping?
```

---

## 8. Command Line Execution

Prompt Antigravity:

```text
Run a CLI query asking my agent how long standard delivery takes.
```

Antigravity executes:

```bash
agents-cli run "How long does standard delivery take?"
```

---

## 9. Cleanup

1. Stop the local playground server with `Ctrl + C`.
2. Remove the local project files:

```bash
rm -rf customer-support-agent
```
