# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pydantic import BaseModel

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.workflow import Workflow, START, node
from google.genai import types
import google.auth

# Safely set up project environment
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        os.environ["GOOGLE_CLOUD_PROJECT"] = "day3_agent_lifecycle"

if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "US"

# Respect GOOGLE_GENAI_USE_ENTERPRISE setting
use_enterprise = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "False").lower() in (
    "true",
    "1",
)
if use_enterprise:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
else:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# Define Pydantic output schema for the classifier agent
class ClassificationResult(BaseModel):
    is_shipping_related: bool


# 1. Classifier Agent (LlmAgent)
# It determines if the user query is related to shipping
classifier_agent = LlmAgent(
    name="classifier_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""Classify if the user query is related to shipping (such as rates, tracking, delivery, or returns) or unrelated.
Return is_shipping_related=True if it is related to shipping, and False otherwise.""",
    output_schema=ClassificationResult,
)


# 2. Router Node (Function Node)
# It parses the classification output, grabs the original user query text, and routes downstream
@node
def route_query(ctx: Context, node_input: dict) -> Event:
    is_shipping = node_input.get("is_shipping_related", False)

    # Extract the original user query from session history to pass to downstream nodes
    user_query = ""
    for event in ctx.session.events:
        if event.author == "user" and event.content and event.content.parts:
            user_query = "".join(part.text for part in event.content.parts if part.text)
            break

    if is_shipping:
        return Event(output=user_query, actions=EventActions(route="shipping"))
    else:
        return Event(output=user_query, actions=EventActions(route="unrelated"))


# 3. Shipping FAQ Agent (LlmAgent)
# It answers shipping-related questions
shipping_faq_agent = LlmAgent(
    name="shipping_faq_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a helpful customer support representative for a shipping company.
Answer the user's question about shipping rates, tracking, delivery, or returns clearly, accurately, and politely.

Specifically for shipping rates:
1. Make your response extremely playful, enthusiastic, and full of positive energy! 🥳🎉
2. Use fun emojis (like 🚚, 📦, ✨, 🚀) to spice up the message.
3. Be sure to prominently highlight our amazing free shipping threshold: FREE SHIPPING on all orders over $50! 🎁💃""",
)


# 4. Decline Node (Function Node)
# It politely declines to answer unrelated queries
@node
def decline_to_answer(node_input: str) -> Event:
    msg = "I am a customer support representative for a shipping company. I can only assist with shipping-related queries (such as rates, tracking, delivery, and returns). Please let me know how I can help you with those!"
    return Event(
        content=types.Content(role="model", parts=[types.Part.from_text(text=msg)]),
        output=msg,
    )


# Construct the Graph Workflow
root_agent = Workflow(
    name="customer_support_workflow",
    edges=[
        (START, classifier_agent),
        (classifier_agent, route_query),
        (route_query, {"shipping": shipping_faq_agent, "unrelated": decline_to_answer}),
    ],
    description="Customer support representative workflow for a shipping company.",
)

app = App(
    root_agent=root_agent,
    name="app",
)
