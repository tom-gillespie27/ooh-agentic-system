import os
import json
from anthropic import Anthropic
from data import CREATIVES

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def choose_creative(billboard, weather, local_context=None):
    creative_list = "\n".join(
        f"- {c['id']}: {c['name']} — {c['description']}" for c in CREATIVES
    )

    prompt = f"""You are an AI agent that controls a digital out-of-home (OOH) billboard.

Billboard location: {billboard['name']} ({billboard['location']})
Current weather: {weather['temp']}°F, {weather['condition']} ({weather['description']})
Local context: {local_context or "None provided"}

Available creatives:
{creative_list}

Based on the current conditions, choose the SINGLE best creative to display right now.

Respond ONLY with valid JSON in this exact format, no other text:
{{
  "selected_creative_id": "...",
  "reasoning": "A 2-3 sentence explanation of why this creative was chosen given the conditions."
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()
    # Strip markdown fences if Claude adds them
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_text)