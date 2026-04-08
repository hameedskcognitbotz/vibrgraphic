import json
import re
import random
from google import genai
from google.genai import types
from openai import AsyncOpenAI
from app.core.config import settings
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)
GEMINI_TEXT_MODEL = "gemini-3-flash-preview"

# ---------------------------------------------------------------------------
# Gemini client (re-used across requests)
# ---------------------------------------------------------------------------
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


# ---------------------------------------------------------------------------
# LLM prompt
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are a senior AI backend engineer, expert content creator and professional educator.
Your goal is to transform raw topics or articles into high-impact visual content.
When acting for Content Creators: focus on hooks, viral potential, and "A-ha" moments.
When acting for Educators: focus on pedagogical clarity, breakdown of complex concepts, and definitions.
Favor concise, practical phrasing that performs well for saves and shares.
Lead with strong hooks, specific takeaways, and a clear final CTA.
"""

USER_PROMPT_TEMPLATE = """
Generate a highly detailed infographic design in JSON format.

Topic: "{topic}"
Target Audience: {audience}

Requirements:
* Generate 6–8 sections
* Each section must include:
  * heading (topic-specific)
  * description (short)
  * 2–4 bullet points
  * icon name (e.g., "robot", "chart", "education")
  * illustration_prompt (for image/icon)
  * color (hex code)
  * layout_position (left, right, center, grid-1, grid-2, etc.)
* Choose a layout type dynamically:
  * "grid"
  * "circular"
  * "step-flow"
  * "timeline"
* Add theme:
  * background_color
  * primary_color
  * secondary_color
* Add charts:
  {{"type": "bar" or "pie", "title": "", "labels": [], "data": []}}
* Add statistics:
  Example: "75% adoption rate"
* Add center highlight element

IMPORTANT:
* Content must be optimized for {audience}
* Output must be unique for each topic
* No generic content
* Include real-world insights
* Headings should be punchy and specific, not generic
* Descriptions should stay under 22 words where possible
* Bullet points should feel useful enough to save or repost
"""

CAROUSEL_PROMPT_TEMPLATE = """
Generate a high-engagement social media carousel design in JSON format.
Topic: "{topic}"
Target Audience: {audience}

Requirements:
* Generate 4–10 slides
* Slide 1 MUST be a high-impact hook "Cover Slide"
* Slides 2 to N-1: Core educational or informative content
* Slide N: Call to Action (CTA) or summary
* Each slide must include:
  * title (hook-driven or descriptive)
  * content (2-4 concise bullet points)
  * image_prompt (vivid, stylish illustration description)
  * footer_note (optional insight)
* Theme:
  * background_color
  * primary_color
  * secondary_color
* author_handle: Suggest a placeholder like "@user_handle"

IMPORTANT:
* Content must be optimized for {audience}
* Output must be unique for each topic
* Slide 1 should feel instantly saveable/shareable
* Keep slide bullets short, concrete, and creator-friendly
"""


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

from app.schemas.infographic import InfographicData, CarouselData


def _mock_theme(seed: random.Random) -> dict:
    palettes = [
        {"background_color": "#0F172A", "primary_color": "#3B82F6", "secondary_color": "#1E293B"},
        {"background_color": "#111827", "primary_color": "#10B981", "secondary_color": "#0B3B2E"},
        {"background_color": "#1F2937", "primary_color": "#F59E0B", "secondary_color": "#78350F"},
    ]
    return seed.choice(palettes)


def _build_mock_infographic(topic: str, audience: str, tone: str) -> dict:
    seed = random.Random(f"{topic}:{audience}:{tone}")
    theme = _mock_theme(seed)
    sections = []
    icons = ["chart", "lightbulb", "target", "shield", "rocket", "globe", "database", "network"]
    positions = ["left", "right", "grid-1", "grid-2", "center", "timeline"]
    for idx in range(6):
        sections.append(
            {
                "heading": f"{topic}: Insight {idx + 1}",
                "description": f"A practical {tone.lower()} perspective for {audience} readers.",
                "points": [
                    f"Core concept {idx + 1} and why it matters.",
                    f"Current trend impacting {topic.lower()}.",
                    f"Actionable takeaway for {audience}.",
                ],
                "icon": icons[idx % len(icons)],
                "illustration_prompt": f"{topic} concept art, clean editorial style, section {idx + 1}",
                "color": seed.choice(["#3B82F6", "#10B981", "#F59E0B", "#EC4899", "#6366F1"]),
                "layout_position": positions[idx % len(positions)],
            }
        )

    return {
        "title": f"{topic}: Essential Breakdown",
        "layout": "grid",
        "theme": theme,
        "sections": sections,
        "charts": [
            {
                "type": "bar",
                "title": f"{topic} Adoption Trend",
                "labels": ["2022", "2023", "2024", "2025"],
                "data": [28, 41, 57, 73],
            }
        ],
        "statistics": [
            "73% of teams expect increased adoption in the next year",
            "2.1x productivity gains reported by early adopters",
            "58% cite skills as the primary bottleneck",
        ],
        "center_element": {
            "title": "Key Signal",
            "subtitle": f"{topic} is moving from hype to implementation",
            "icon": "zap",
        },
    }


def _build_mock_carousel(topic: str, audience: str, tone: str) -> dict:
    seed = random.Random(f"carousel:{topic}:{audience}:{tone}")
    theme = _mock_theme(seed)
    slides = []
    for idx in range(4):
        slides.append(
            {
                "title": f"{topic} Slide {idx + 1}",
                "content": [
                    f"Point {idx + 1}.1 tailored for {audience}",
                    f"Point {idx + 1}.2 with a {tone.lower()} angle",
                    f"Point {idx + 1}.3 practical recommendation",
                ],
                "image_prompt": f"{topic} social carousel illustration, slide {idx + 1}",
                "footer_note": "Generated with resilient fallback mode",
            }
        )

    slides[0]["title"] = f"{topic}: The 60-Second Breakdown"
    slides[-1]["title"] = "What To Do Next"
    return {
        "title": f"{topic} Carousel",
        "topic": topic,
        "slides": slides,
        "theme": theme,
        "author_handle": "@VibeGraphic",
    }


def _mock_structured_content(topic: str, audience: str, is_carousel: bool, tone: str) -> dict:
    if is_carousel:
        return _build_mock_carousel(topic, audience, tone)
    return _build_mock_infographic(topic, audience, tone)


async def generate_structured_content(
    topic: str,
    audience: str = "general",
    is_carousel: bool = False,
    tone: str = "Educational",
    template_key: str | None = None,
    export_preset: str | None = None,
    brand_context: dict | None = None,
    generation_mode: str = "creative",
) -> dict:
    """
    Calls an LLM to generate rich infographic or carousel content.
    """
    if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY:
        if settings.ALLOW_MOCK_FALLBACK_ON_AI_ERROR:
            logger.warning("No LLM API key configured; using mock content fallback.")
            return _mock_structured_content(topic, audience, is_carousel, tone)
        raise ValueError("No LLM API Key found. Configure GEMINI_API_KEY or OPENAI_API_KEY.")

    tone_instruction = f" The tone of the content should be {tone}."
    template_instruction = ""
    if template_key:
        template_instruction = (
            f" Use the '{template_key}' content template and reflect that structure explicitly."
        )
    preset_instruction = ""
    if export_preset:
        preset_instruction = (
            f" Optimize the output for the '{export_preset}' export preset and likely social posting context."
        )
    brand_instruction = ""
    if brand_context:
        brand_parts = []
        if brand_context.get("brand_name"):
            brand_parts.append(f"brand name '{brand_context['brand_name']}'")
        if brand_context.get("social_handle"):
            brand_parts.append(f"social handle '{brand_context['social_handle']}'")
        if brand_context.get("cta_text"):
            brand_parts.append(f"CTA '{brand_context['cta_text']}'")
        if brand_parts:
            brand_instruction = " Incorporate creator branding with " + ", ".join(brand_parts) + "."
    grounding_instruction = ""
    if generation_mode == "grounded":
        grounding_instruction = (
            " Prioritize factual claims, realistic chart values, and verifiable trends."
            " Avoid invented statistics; use conservative, plausible figures when uncertain."
        )
    if is_carousel:
        prompt = (
            CAROUSEL_PROMPT_TEMPLATE.format(topic=topic, audience=audience)
            + tone_instruction
            + template_instruction
            + preset_instruction
            + brand_instruction
            + grounding_instruction
        )
        schema = CarouselData
    else:
        prompt = (
            USER_PROMPT_TEMPLATE.format(topic=topic, audience=audience)
            + tone_instruction
            + template_instruction
            + preset_instruction
            + brand_instruction
            + grounding_instruction
        )
        schema = InfographicData

    logger.info(
        f"Received request to generate {'carousel' if is_carousel else 'infographic'} for topic: '{topic}'"
    )

    # Provider 1: OpenAI
    if settings.OPENAI_API_KEY and not settings.GEMINI_API_KEY:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        for attempt in range(2):
            try:
                response = await client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": prompt},
                    ],
                    response_format=schema,
                    temperature=0.9,
                )
                result = response.choices[0].message.parsed.model_dump()
                return _apply_creator_guardrails(result, is_carousel, brand_context, generation_mode)
            except Exception as e:
                if attempt == 1:
                    if settings.ALLOW_MOCK_FALLBACK_ON_AI_ERROR:
                        logger.warning(f"OpenAI generation failed, using mock fallback: {e}")
                        return _apply_creator_guardrails(
                            _mock_structured_content(topic, audience, is_carousel, tone),
                            is_carousel,
                            brand_context,
                            generation_mode,
                        )
                    raise e
                logger.info(f"Retrying OpenAI due to error: {e}")

    # Provider 2: Google Gemini (Default)
    else:
        client = _get_client()
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=GEMINI_TEXT_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.9,
                        tools=[types.Tool(google_search=types.GoogleSearch())] if generation_mode == "grounded" else None,
                    ),
                )

                raw_content = response.text
                parsed_data = schema.model_validate_json(raw_content)
                return _apply_creator_guardrails(parsed_data.model_dump(), is_carousel, brand_context, generation_mode)

            except Exception as e:
                if attempt == max_retries - 1:
                    if settings.ALLOW_MOCK_FALLBACK_ON_AI_ERROR:
                        logger.warning(f"Gemini generation failed, using mock fallback: {e}")
                        return _apply_creator_guardrails(
                            _mock_structured_content(topic, audience, is_carousel, tone),
                            is_carousel,
                            brand_context,
                            generation_mode,
                        )
                    raise e
                logger.info(f"Retrying Gemini due to error: {e}")


async def refine_structured_content(
    data: dict, instruction: str, is_carousel: bool = False
) -> dict:
    """
    Refines existing structured content based on a natural language instruction.
    """
    if is_carousel:
        schema = CarouselData
    else:
        schema = InfographicData

    prompt = f"Original Content: {json.dumps(data)}\n\nRefinement Instruction: {instruction}\n\nPlease output the updated JSON in the same schema."

    # We'll use the Gemini (Flash) as it's great for instructional follow-through
    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            system_instruction="You are a professional content editor. Your goal is to improve the provided content based on instructions while maintaining the JSON schema.",
            temperature=0.7,
        ),
    )

    raw_content = response.text
    parsed_data = schema.model_validate_json(raw_content)
    return _apply_creator_guardrails(parsed_data.model_dump(), is_carousel, generation_mode=generation_mode)


def _shorten_text(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]).rstrip(",.") + "..."


def _apply_creator_guardrails(
    data: dict,
    is_carousel: bool,
    brand_context: dict | None = None,
    generation_mode: str = "creative",
) -> dict:
    brand_context = brand_context or {}
    visual_prompt_suffix = (
        " Use clean headings and label-safe composition; avoid garbled text rendering."
        " If any text appears inside the illustration, keep it short and legible."
    )
    if generation_mode == "grounded":
        visual_prompt_suffix += " Keep charts and visuals fact-anchored and realistic."

    if is_carousel:
        slides = data.get("slides", [])
        if slides:
            slides[0]["title"] = _shorten_text(slides[0].get("title", "Save-worthy breakdown"), 8)
            for slide in slides:
                slide["content"] = [_shorten_text(point, 10) for point in slide.get("content", [])[:4]]
                image_prompt = slide.get("image_prompt", "").strip()
                slide["image_prompt"] = (image_prompt + " " + visual_prompt_suffix).strip()
            slides[-1]["title"] = _shorten_text(slides[-1].get("title", "What to do next"), 8)
            cta = brand_context.get("cta_text") or "Follow for more creator-ready visuals"
            existing_content = slides[-1].get("content", [])
            slides[-1]["content"] = (existing_content[:3] + [cta])[:4]
        if brand_context.get("social_handle"):
            data["author_handle"] = brand_context["social_handle"]
        return data

    sections = data.get("sections", [])
    for section in sections:
        section["heading"] = _shorten_text(section.get("heading", ""), 7)
        section["description"] = _shorten_text(section.get("description", ""), 18)
        section["points"] = [_shorten_text(point, 10) for point in section.get("points", [])[:4]]
        illustration_prompt = section.get("illustration_prompt", "").strip()
        section["illustration_prompt"] = (illustration_prompt + " " + visual_prompt_suffix).strip()

    statistics = data.get("statistics", [])
    data["statistics"] = [_shorten_text(stat, 8) for stat in statistics[:4]]
    center_element = data.get("center_element") or {}
    if brand_context.get("cta_text"):
        center_element["subtitle"] = _shorten_text(brand_context["cta_text"], 12)
        data["center_element"] = center_element
    return data
