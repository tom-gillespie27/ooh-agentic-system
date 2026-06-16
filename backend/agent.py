import os
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

from data import CREATIVES
from weather import get_weather
from events import get_local_events

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to backend/.env or your shell environment."
        )
    return Anthropic(api_key=api_key)


def parse_decision_json(text):
    cleaned = (
        text
        .strip()
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        json_start = cleaned.find("{")
        json_end = cleaned.rfind("}")
        if json_start == -1 or json_end == -1 or json_end < json_start:
            raise

        return json.loads(cleaned[json_start:json_end + 1])

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather conditions for a given latitude and longitude. Returns temperature (F), condition, and description.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude of the location"
                },
                "lon": {
                    "type": "number",
                    "description": "Longitude of the location"
                }
            },
            "required": ["lat", "lon"]
        }
    },
    {
        "name": "get_local_events",
        "description": "Get nearby local events such as sports games, concerts, festivals, and community events.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude of the location"
                },
                "lon": {
                    "type": "number",
                    "description": "Longitude of the location"
                }
            },
            "required": ["lat", "lon"]
        }
    }
]


def choose_creative(billboard, local_context=None):

    print("\n" + "=" * 60)
    print(f"🎯 AGENT STARTED: {billboard['name']} ({billboard['location']})")
    print("=" * 60)

    trace = []

    creative_list = "\n".join(
        f"- {c['id']}: {c['name']} — {c['description']}"
        for c in CREATIVES
    )

    system_prompt = f"""
You are a senior digital out-of-home (OOH) advertising strategist.

Billboard location:
{billboard['name']} ({billboard['location']})

Latitude: {billboard['lat']}
Longitude: {billboard['lon']}

Local context:
{local_context or "None provided"}

Available creatives:

{creative_list}

Advertising objectives:

1. Maximize audience relevance.
2. Use contextual advertising principles.
3. Consider weather conditions.
4. Consider nearby events.
5. Consider likely audience intent.
6. Select the creative most likely to drive engagement.

IMPORTANT:
Use available tools before making a decision.

Return ONLY valid JSON in exactly this format:

{{
  "selected_creative_id": "...",
  "confidence": 0,
  "rankings": [
    {{
      "creative": "...",
      "score": 0
    }}
  ],
  "weather_summary": "...",
  "event_summary": "...",
  "reasoning": "..."
}}

IMPORTANT:
You MUST call get_weather.
You MUST call get_local_events.

Do not make a decision until both tools have been used.
"""

    messages = [
        {
            "role": "user",
            "content": "Choose the best creative for this billboard right now."
        }
    ]

    print("🧠 Step 1: Sending request to Claude...")

    client = get_anthropic_client()

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=800,
        system=system_prompt,
        tools=tools,
        messages=messages
    )

    print(f"   ↳ Claude stop reason: {response.stop_reason}")

    step = 2

    while response.stop_reason == "tool_use":

        messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )

        tool_results = []

        for block in response.content:

            if block.type == "text" and block.text.strip():
                print(f"💭 Claude: {block.text.strip()}")

            if block.type == "tool_use":

                lat = block.input["lat"]
                lon = block.input["lon"]

                print(
                    f"🔧 Step {step}: Tool Call -> {block.name}"
                )

                print(
                    f"   ↳ Arguments: lat={lat}, lon={lon}"
                )

                if block.name == "get_weather":

                    weather_data = get_weather(lat, lon)

                    trace.append({
                        "tool": "get_weather",
                        "input": {
                            "lat": lat,
                            "lon": lon
                        },
                        "output": weather_data
                    })

                    print(
                        f"   ↳ Weather Result: {weather_data}"
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(weather_data)
                    })

                elif block.name == "get_local_events":

                    events_data = get_local_events(lat, lon)

                    trace.append({
                        "tool": "get_local_events",
                        "input": {
                            "lat": lat,
                            "lon": lon
                        },
                        "output": events_data
                    })

                    print(
                        f"   ↳ Events Result: {events_data}"
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(events_data)
                    })

        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )

        step += 1

        print(
            f"🧠 Step {step}: Sending tool results back to Claude..."
        )

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=800,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        print(
            f"   ↳ Claude stop reason: {response.stop_reason}"
        )

    final_text = ""

    for block in response.content:
        if block.type == "text":
            final_text += block.text

    try:
        result = parse_decision_json(final_text)

    except Exception as e:

        print("❌ Failed to parse Claude response:")
        print(final_text)

        result = {
            "selected_creative_id": "creative_streaming",
            "confidence": 50,
            "rankings": [
                {
                    "creative": "creative_streaming",
                    "score": 50
                }
            ],
            "weather_summary": "Unknown",
            "event_summary": "Unknown",
            "reasoning": f"Fallback selection. Parse error: {str(e)}"
        }

    result["trace"] = trace

    print("\n✅ FINAL DECISION")
    print(
        f"Creative: {result.get('selected_creative_id')}"
    )
    print(
        f"Confidence: {result.get('confidence')}"
    )
    print(
        f"Weather: {result.get('weather_summary')}"
    )
    print(
        f"Events: {result.get('event_summary')}"
    )
    print(
        f"Reasoning: {result.get('reasoning')}"
    )
    print("=" * 60 + "\n")

    return result
