import os
import json
from anthropic import Anthropic
from data import CREATIVES
from weather import get_weather

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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
    print("\n" + "="*60)
    print(f"🎯 AGENT STARTED: {billboard['name']} ({billboard['location']})")
    print("="*60)

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

    print("🧠 Step 1: Sending request to Claude with available tools...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        tools=tools,
        messages=messages
    )
    print(f"   ↳ Claude's stop reason: '{response.stop_reason}'")

    step = 2
    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"💭 Claude's reasoning before tool call: \"{block.text.strip()}\"")

            if block.type == "tool_use" and block.name == "get_weather":
                lat = block.input["lat"]
                lon = block.input["lon"]
                print(f"🔧 Step {step}: Claude called tool 'get_weather'")
                print(f"   ↳ Arguments: lat={lat}, lon={lon}")

                weather_data = get_weather(lat, lon)
                print(f"   ↳ Tool result: {weather_data}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(weather_data)
                })

        messages.append({"role": "user", "content": tool_results})

        step += 1
        print(f"🧠 Step {step}: Sending tool result back to Claude for final decision...")
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system_prompt,
            tools=tools,
            messages=messages
        )
        print(f"   ↳ Claude's stop reason: '{response.stop_reason}'")

    final_text = ""
    for block in response.content:
        if block.type == "text":
            final_text += block.text

    final_text = final_text.strip().replace("```json", "").replace("```", "").strip()

    result = json.loads(final_text)

    print("\n✅ FINAL DECISION:")
    print(f"   Selected creative: {result['selected_creative_id']}")
    print(f"   Weather summary:   {result['weather_summary']}")
    print(f"   Reasoning:         {result['reasoning']}")
    print("="*60 + "\n")

    return result