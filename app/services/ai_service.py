import json
import re
import random
from google import genai
from google.genai import types
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.infographic import InfographicData
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

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
"""


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

from app.schemas.infographic import InfographicData, CarouselData


async def generate_structured_content(
    topic: str,
    audience: str = "general",
    is_carousel: bool = False,
    tone: str = "Educational",
) -> dict:
    """
    Calls an LLM to generate rich infographic or carousel content.
    """
    if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY:
        raise ValueError(
            "No LLM API Key found. Configure GEMINI_API_KEY or OPENAI_API_KEY."
        )

    tone_instruction = f" The tone of the content should be {tone}."
    if is_carousel:
        prompt = (
            CAROUSEL_PROMPT_TEMPLATE.format(topic=topic, audience=audience)
            + tone_instruction
        )
        schema = CarouselData
    else:
        prompt = (
            USER_PROMPT_TEMPLATE.format(topic=topic, audience=audience)
            + tone_instruction
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
                return result
            except Exception as e:
                if attempt == 1:
                    raise e
                logger.info(f"Retrying OpenAI due to error: {e}")

    # Provider 2: Google Gemini (Default)
    else:
        client = _get_client()
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.9,
                    ),
                )

                raw_content = response.text
                parsed_data = schema.model_validate_json(raw_content)
                return parsed_data.model_dump()

            except Exception as e:
                if attempt == max_retries - 1:
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
        model="gemini-2.5-flash",
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
    return parsed_data.model_dump()
