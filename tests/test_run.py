"""
Standalone script: calls Gemini API (google-genai SDK) and prints rich infographic JSON output.
"""
import json, re, sys
from google import genai
from google.genai import types

GEMINI_API_KEY = "AIzaSyBKj9_vCCZ328-Dfhixfw64ZQp0y-Uem7I"
TOPIC = "Artificial Intelligence"

client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT = f"""
You are generating infographic content for the topic: "{TOPIC}"

Return ONLY a JSON object — no text outside the JSON — with this exact structure:

{{
  "title": "A compelling, specific title for the infographic",
  "designs": [
    {{
      "template": "<one of: modern | minimal | corporate | bold>",
      "chart": {{
        "type": "<bar | pie | line>",
        "labels": ["label1", "label2", "label3", "label4", "label5"],
        "data": [10, 20, 30, 40, 50]
      }},
      "sections": [
        {{
          "heading": "Section heading (4-7 words, punchy)",
          "description": "One-sentence overview of this section (max 20 words).",
          "points": [
            "Specific insight with a stat or number, e.g. Reduces costs by 30 percent via automation",
            "Another data-backed bullet point",
            "A third specific insight",
            "Optional fourth bullet if impactful"
          ],
          "icon": "single icon keyword, e.g. robot or chart or shield or rocket or globe or cpu",
          "image_prompt": "flat illustration prompt for an AI image generator, 8 to 12 words"
        }}
      ]
    }}
  ]
}}

RULES:
1. Generate EXACTLY 3 designs. Use templates in this order: modern, minimal, corporate.
2. Each design must have EXACTLY 5 sections.
3. Each section must have 3-4 bullet points in the points array.
4. Each bullet point MUST contain a specific number, percentage, or named example. NO generic statements.
5. Each image_prompt must be a vivid descriptive phrase for an AI image generator.
6. chart data must contain exactly 5 numeric values matching the 5 labels.
7. Vary section order and emphasis between designs.
8. Output ONLY the JSON object. Nothing else before or after.
""".strip()

print(f"Calling Gemini API for topic: '{TOPIC}'...\n")

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=PROMPT,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7
        )
    )

    raw = response.text.strip()

    # Strip markdown fences if any
    fenced = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", raw, re.IGNORECASE)
    if fenced:
        raw = fenced.group(1).strip()

    result = json.loads(raw)

    print("=" * 70)
    print("  GEMINI INFOGRAPHIC OUTPUT")
    print("=" * 70)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 70)
    print("\nSUMMARY:")
    print(f"  Title   : {result.get('title')}")
    print(f"  Designs : {len(result.get('designs', []))}")
    for i, d in enumerate(result.get("designs", [])):
        secs = d.get("sections", [])
        chart = d.get("chart", {})
        print(f"  Design #{i+1}: template={d.get('template'):<12} sections={len(secs)}  chart={chart.get('type')}")

except json.JSONDecodeError as e:
    print(f"[ERROR] Invalid JSON from Gemini: {e}")
    print("Raw response:\n", raw[:1000])
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    sys.exit(1)
