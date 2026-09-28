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

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import json
import os

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from app.a2ui_utils import a2ui_callback
from app.external_tools import get_live_destination_weather
from app.firestore_tools import (
    add_destination,
    calculate_trip_budget,
    get_destination_details,
    search_destinations,
)
from app.image_tools import generate_destination_image
from app.video_tools import generate_destination_video
from app.maps_tools import find_nearby_places, geocode_address

# Build system prompt using A2UI v0.8 SchemaManager and BasicCatalog
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a helpful travel concierge AI assistant designed to help users explore travel destinations, search locations, and plan trips. "
        "You pay close attention to and remember all user dietary restrictions, food allergies (such as peanut, gluten, dairy, shellfish, or penicillin allergies), "
        "and medical/health sensitivities from previous conversations, and proactively use them to personalize recommendations and keep the user safe."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


def _load_agent_engine_resource_name() -> str | None:
    """Read Agent Engine resource name from deployment_metadata.json if available."""
    metadata_path = os.path.join(
        os.path.dirname(__file__), "..", "deployment_metadata.json"
    )
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path) as f:
                data = json.load(f)
                runtime_id = data.get("remote_agent_runtime_id")
                if runtime_id and runtime_id != "None":
                    return runtime_id
        except Exception:
            pass
    return None


code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=_load_agent_engine_resource_name()
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


def memory_bank_service_builder():
    """Memory service builder for deployed runtime."""
    resource_id = _load_agent_engine_resource_name()
    if resource_id:
        memory_bank_id = resource_id.split("/")[-1]
    else:
        memory_bank_id = "8672203900280897536"
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-03-914ab565751f",
        location="us-central1",
        agent_engine_id=memory_bank_id,
    )


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        get_live_destination_weather,
        search_destinations,
        get_destination_details,
        add_destination,
        calculate_trip_budget,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
