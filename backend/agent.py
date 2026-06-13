import os
import json
from anthropic import Anthropic
from data import CREATIVES
from weather import get_weather

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Define the tool Claude can call
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather conditions for a given latitude and longitude. Returns temperature (F), condition, and description.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude of the location"},
                "lon": {"type": "number", "description": "Longitude of the location"}
            },
            "required": ["lat", "lon"]
        }
    }
]

def choose_creative(billboard, local_context=None):
    creative_list = "\n".join(
        f"- {c['id']}: {c['name']} — {c['description']}" for c in CREATIVES
    )

    system_prompt = f"""You are an AI agent that controls a digital out-of-home (OOH) billboard.

Billboard location: {billboard['name']} ({billboard['location']})
Latitude: {billboard['lat']}, Longitude: {billboard['lon']}
Local context: {local_context or "None provided"}

Available creatives:
{creative_list}

Use the get_weather tool to check current conditions at this billboard's location, then choose the SINGLE best creative to display right now.

Once you have the weather, respond ONLY with valid JSON in this exact format, no other text:
{{
  "selected_creative_id": "...",
  "weather_summary": "Brief summary of the weather you used",
  "reasoning": "A 2-3 sentence explanation of why this creative was chosen given the conditions."
}}"""

    messages = [{"role": "user", "content": "Choose the best creative for this billboard right now."}]

    # First call - Claude decides to use the tool
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        tools=tools,
        messages=messages
    )

    # Handle tool use loop
    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "get_weather":
                lat = block.input["lat"]
                lon = block.input["lon"]
                weather_data = get_weather(lat, lon)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(weather_data)
                })

        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

    # Final response - extract the JSON
    final_text = ""
    for block in response.content:
        if block.type == "text":
            final_text += block.text

    final_text = final_text.strip().replace("```json", "").replace("```", "").strip()

    return json.loads(final_text)