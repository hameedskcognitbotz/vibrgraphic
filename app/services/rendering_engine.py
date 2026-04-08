import io
import logging
import textwrap
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")

PRESET_SPECS = {
    "instagram_carousel": {"width": 1080, "height": 1080},
    "linkedin_post": {"width": 1200, "height": 1500},
    "story": {"width": 1080, "height": 1920},
}

_image_client: genai.Client | None = None

def hex_to_rgb(hex_color: str):
    """Utility to convert hex (#RRGGBB) to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(size: int, is_bold: bool = False, family: str = "Inter"):
    """Loads bundled Inter or Montserrat fonts with a robust fallback."""
    try:
        if family == "Montserrat":
            font_path = os.path.join(FONT_DIR, "Montserrat-ExtraBold.ttf" if is_bold else "Montserrat-Bold.ttf")
        else:
            font_path = os.path.join(FONT_DIR, "Inter-Bold.ttf" if is_bold else "Inter-Regular.ttf")
        
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        
        # Fallback to standard names
        fallback = "arialbd.ttf" if is_bold else "arial.ttf"
        return ImageFont.truetype(fallback, size)
    except IOError:
        return ImageFont.load_default()

def draw_glass_card(draw, rect, fill_alpha=40, outline_alpha=80, radius=20):
    """Draws a premium semi-transparent card (Glassmorphism)."""
    # Create temp layer for transparency
    mask = Image.new("RGBA", (int(rect[2]-rect[0]), int(rect[3]-rect[1])), (0,0,0,0))
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, rect[2]-rect[0], rect[3]-rect[1]], radius=radius, 
                       fill=(255, 255, 255, fill_alpha), 
                       outline=(255, 255, 255, outline_alpha), width=2)
    return mask

def get_dominant_color(img):
    """Extracts dominant color for syncing design elements."""
    # Resize to 1x1 to get average color
    small_img = img.copy().resize((1, 1), Image.Resampling.LANCZOS)
    return small_img.getpixel((0, 0))

def apply_drop_shadow(img, offset=(10, 10), background_color=(0,0,0,0), blur_radius=15, shadow_alpha=120):
    """Creates a high-end floating effect for illustrations."""
    shadow = Image.new("RGBA", (img.width + offset[0] + blur_radius*2, img.height + offset[1] + blur_radius*2), (0,0,0,0))
    # Extract alpha mask of the image
    alpha = img.getchannel('A')
    shadow_mask = Image.new("L", img.size, shadow_alpha)
    shadow_img = Image.merge("RGBA", (Image.new("L", img.size, 0), Image.new("L", img.size, 0), Image.new("L", img.size, 0), alpha))
    
    shadow.paste((0, 0, 0, shadow_alpha), (blur_radius, blur_radius), mask=alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    final_img = Image.new("RGBA", shadow.size, (0,0,0,0))
    final_img.paste(shadow, (0,0))
    final_img.paste(img, (blur_radius - offset[0]//2, blur_radius - offset[1]//2), mask=img)
    return final_img

def _get_image_client() -> genai.Client | None:
    global _image_client
    if _image_client is not None:
        return _image_client
    if not settings.GEMINI_API_KEY:
        return None
    try:
        _image_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return _image_client
    except Exception as err:
        logger.warning(f"Gemini image client init failed: {err}")
        return None

def _aspect_ratio(width: int, height: int) -> str:
    ratio = width / height if height else 1
    if abs(ratio - 1.0) < 0.05:
        return "1:1"
    if abs(ratio - 4 / 5) < 0.05:
        return "4:5"
    if abs(ratio - 9 / 16) < 0.05:
        return "9:16"
    if abs(ratio - 16 / 9) < 0.05:
        return "16:9"
    return "1:1"

def _extract_image_bytes(response: types.GenerateContentResponse) -> bytes | None:
    parts = []
    if getattr(response, "candidates", None):
        for candidate in response.candidates:
            content = getattr(candidate, "content", None)
            candidate_parts = getattr(content, "parts", None) if content else None
            if candidate_parts:
                parts.extend(candidate_parts)
    if not parts and getattr(response, "parts", None):
        parts.extend(response.parts)

    for part in parts:
        inline_data = getattr(part, "inline_data", None)
        if inline_data and getattr(inline_data, "data", None):
            return inline_data.data
    return None

def _placeholder_image(width: int, height: int) -> Image.Image:
    return Image.new("RGBA", (width, height), (30, 41, 59, 255))

def _generate_gemini_image(prompt: str, width: int, height: int, generation_mode: str = "creative") -> Image.Image:
    client = _get_image_client()
    if client is None:
        return _placeholder_image(width, height)

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=[types.Modality.IMAGE],
                image_config=types.ImageConfig(
                    aspectRatio=_aspect_ratio(width, height),
                ),
                tools=[types.Tool(google_search=types.GoogleSearch())] if generation_mode == "grounded" else None,
            ),
        )
        image_bytes = _extract_image_bytes(response)
        if not image_bytes:
            return _placeholder_image(width, height)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        return ImageOps.fit(img, (width, height), Image.Resampling.LANCZOS)
    except Exception as err:
        logger.warning(f"Gemini image generation failed, using placeholder: {err}")
        return _placeholder_image(width, height)

def get_preset_spec(export_preset: str | None, is_carousel: bool) -> dict:
    if export_preset in PRESET_SPECS:
        return PRESET_SPECS[export_preset]
    return {"width": 1080, "height": 1080} if is_carousel else {"width": 1300, "height": 1800}

def _fit_to_canvas(img: Image.Image, target_width: int, target_height: int, bg_color: tuple[int, int, int]) -> Image.Image:
    fitted = ImageOps.contain(img, (target_width, target_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_width, target_height), bg_color)
    offset = ((target_width - fitted.width) // 2, (target_height - fitted.height) // 2)
    canvas.paste(fitted, offset)
    return canvas

def render_image(
    layout_data: dict,
    export_preset: str | None = None,
    generation_mode: str = "creative",
) -> bytes:
    """
    Renders a stunning, premium infographic via Pillow.
    Features: Typography bundling, Glassmorphism, Drop Shadows, and Smart Scaling.
    """
    logger.info("Rendering premium layout with Z-axis depth effects...")
    
    title = layout_data.get("title", "Infographic Title").upper()
    sections = layout_data.get("sections", [])
    theme = layout_data.get("theme", {})
    
    # Fonts (Montserrat for titles, Inter for body)
    title_font = get_font(58, is_bold=True, family="Montserrat")
    section_title_font = get_font(34, is_bold=True, family="Montserrat")
    body_font = get_font(21, family="Inter")
    point_font = get_font(21, is_bold=True, family="Inter")
    footer_font = get_font(18, family="Inter")

    # Layout dimensions
    width = 1300 
    margin_x = 80
    card_width = width - (margin_x * 2)
    base_img_width = 400
    base_img_height = 300
    
    # Wrapped Title
    wrapped_title = textwrap.wrap(title, width=32)
    title_height = 120 + (len(wrapped_title) * 70)
    
    total_height = title_height
    wrapped_sections = []
    
    def fetch_section_image(sec):
        prompt = sec.get("illustration_prompt", "abstract technology")
        mode_prompt = (
            " factual, grounded in recent public information, realistic chart context,"
            if generation_mode == "grounded"
            else " stylized creative direction,"
        )
        img_prompt = (
            f"{prompt}, premium infographic illustration,{mode_prompt}"
            " clean typography zones, label-safe composition, high detail, no gibberish text"
        )
        sec_img = _generate_gemini_image(img_prompt, base_img_width, base_img_height, generation_mode)
            
        # 1. Round corners
        mask = Image.new("L", sec_img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, sec_img.width, sec_img.height], radius=30, fill=255)
        rounded_img = Image.new("RGBA", sec_img.size, (0,0,0,0))
        rounded_img.paste(sec_img, (0,0), mask=mask)
        
        # 2. Extract dominant color for sync
        dom_color = get_dominant_color(rounded_img)
        
        # 3. Apply drop shadow
        elevated_img = apply_drop_shadow(rounded_img)
        return elevated_img, dom_color

    image_results = [fetch_section_image(sec) for sec in sections]
    
    for sec, (elevated_img, dom_color) in zip(sections, image_results):
        desc_wrap = textwrap.wrap(sec.get("description", ""), width=50)
        points_wrap = []
        for pt in sec.get("points", []):
            points_wrap.append(textwrap.wrap(f"• {pt}", width=50))
            
        # Height estimation
        summary_h = (len(desc_wrap) * 32) + sum(len(p)*30 for p in points_wrap) + (len(points_wrap)*8)
        text_h = 60 + (len(textwrap.wrap(sec.get("heading", ""), width=45)) * 42) + summary_h + 80
        sec_h = max(text_h, elevated_img.height + 60)
        
        wrapped_sections.append({
            "heading": textwrap.wrap(sec.get("heading", ""), width=45),
            "description": desc_wrap,
            "points": points_wrap,
            "height": sec_h,
            "image": elevated_img,
            "accent_color": dom_color
        })
        total_height += sec_h + 60
        
    total_height += 180
    
    img = Image.new('RGBA', (width, total_height), (30, 41, 59, 255))
    draw = ImageDraw.Draw(img)

    # 1. Gradient Background
    bg_start = hex_to_rgb(theme.get("background_color", "#0F172A"))
    bg_end = hex_to_rgb(theme.get("secondary_color", "#1E1B4B"))
    # Efficient fill
    for y in range(total_height):
        r = bg_start[0] + (bg_end[0] - bg_start[0]) * y // total_height
        g = bg_start[1] + (bg_end[1] - bg_start[1]) * y // total_height
        b = bg_start[2] + (bg_end[2] - bg_start[2]) * y // total_height
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Ambient Decorations
    # Draw decoration on a separate RGBA overlay, then alpha-composite.
    # This avoids alpha-drop artifacts when converting final output to RGB.
    ambient = Image.new("RGBA", (width, total_height), (0, 0, 0, 0))
    ambient_draw = ImageDraw.Draw(ambient)
    for _ in range(15):
        x, y = random.randint(0, width), random.randint(0, total_height)
        s = random.randint(100, 400)
        ambient_draw.ellipse([x, y, x + s, y + s], fill=(255, 255, 255, 10))
    img = Image.alpha_composite(img, ambient)
    draw = ImageDraw.Draw(img)

    # 3. Draw Title
    curr_y = 70
    for line in wrapped_title:
        lw, lh = draw.textsize(line, font=title_font) if hasattr(draw, 'textsize') else (draw.textbbox((0,0), line, font=title_font)[2], draw.textbbox((0,0), line, font=title_font)[3])
        draw.text(((width - lw)/2, curr_y), line, fill="#F8FAFC", font=title_font)
        curr_y += 75
    curr_y += 40

    # 4. Draw Glass Cards
    for idx, sec in enumerate(wrapped_sections):
        card_rect = [margin_x, curr_y, margin_x + card_width, curr_y + sec["height"]]
        
        # Glass card creation
        glass = draw_glass_card(img, card_rect)
        img.paste(glass, (int(card_rect[0]), int(card_rect[1])), glass)
        
        # Layout alternation
        is_even = idx % 2 == 0
        img_x = margin_x + 20 if is_even else margin_x + card_width - sec["image"].width - 20
        text_x = margin_x + sec["image"].width + 60 if is_even else margin_x + 50
        
        # Paste Image (Elevated)
        img.paste(sec["image"], (int(img_x), int(curr_y + 30)), sec["image"])
        
        # Text Rendering
        inner_y = curr_y + 50
        # Color Sync - Accent Line
        accent = sec["accent_color"]
        draw.line([text_x, inner_y, text_x + 60, inner_y], fill=(accent[0], accent[1], accent[2], 255), width=6)
        inner_y += 25
        
        for line in sec["heading"]:
            draw.text((text_x, inner_y), line, fill="#F1F5F9", font=section_title_font)
            inner_y += 44
        inner_y += 15
        
        for line in sec["description"]:
            draw.text((text_x, inner_y), line, fill="#94A3B8", font=body_font)
            inner_y += 32
        inner_y += 20
        
        for lines in sec["points"]:
            first = True
            for line in lines:
                prefix = "• " if first else "  "
                draw.text((text_x, inner_y), f"{prefix}{line}", fill="#CBD5E1" if first else "#64748B", font=point_font if first else body_font)
                inner_y += 30
                first = False
            inner_y += 10
            
        curr_y += sec["height"] + 50

    # 5. Footer
    handle = layout_data.get("author_handle", "@VibeGraphic")
    brand_name = layout_data.get("brand_name", "VibeGraphic")
    cta_text = layout_data.get("cta_text")
    footer_txt = f"{brand_name} • {handle}"
    if cta_text:
        footer_txt = f"{footer_txt} • {cta_text}"
    lw = draw.textbbox((0,0), footer_txt, font=footer_font)[2]
    draw.text(((width - lw)/2, total_height - 100), footer_txt, fill="#475569", font=footer_font)

    final_img = img.convert('RGB')
    preset_spec = get_preset_spec(export_preset, is_carousel=False)
    if export_preset:
        final_img = _fit_to_canvas(final_img, preset_spec["width"], preset_spec["height"], bg_start)

    buf = io.BytesIO()
    final_img.save(buf, format='PNG', optimize=True)
    return buf.getvalue()

def render_carousel(
    carousel_data: dict,
    width: int = 1080,
    height: int = 1080,
    export_preset: str | None = None,
    generation_mode: str = "creative",
) -> list[bytes]:
    """
    Renders a set of carousel slides (1080x1080) with premium typography and auto-scaling.
    """
    preset_spec = get_preset_spec(export_preset, is_carousel=True)
    width = preset_spec["width"]
    height = preset_spec["height"]
    logger.info(f"Rendering premium carousel: {carousel_data.get('title')}")
    slides = carousel_data.get("slides", [])
    theme = carousel_data.get("theme", {})
    bg_color_hex = theme.get("background_color", "#0F172A")
    bg_color = hex_to_rgb(bg_color_hex)
    primary_color = theme.get("primary_color", "#3B82F6")
    handle = carousel_data.get("author_handle", "@VibeGraphic")
    brand_name = carousel_data.get("brand_name", "VibeGraphic")
    cta_text = carousel_data.get("cta_text")

    def fetch_slide_image(slide):
        mode_prompt = (
            " factual, grounded in recent public information, realistic context,"
            if generation_mode == "grounded"
            else " highly creative art direction,"
        )
        prompt = (
            f"{slide.get('image_prompt')}, premium 3D isometric render,{mode_prompt}"
            " isolated object, clean heading-safe negative space, high detail, no gibberish text"
        )
        img = _generate_gemini_image(prompt, 600, 600, generation_mode)
        return apply_drop_shadow(img, blur_radius=20, shadow_alpha=100), get_dominant_color(img)

    image_results = [fetch_slide_image(slide) for slide in slides]
    rendered_slides = []

    for idx, (slide, (elevated_img, dom_color)) in enumerate(zip(slides, image_results)):
        img = Image.new("RGBA", (width, height), color=(*bg_color, 255))

        # 1. Background Decoration (alpha-safe overlay)
        ambient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ambient_draw = ImageDraw.Draw(ambient)
        ambient_draw.ellipse([width - 400, -200, width + 200, 400], fill=(255, 255, 255, 20))
        ambient_draw.ellipse(
            [-200, height - 400, 400, height + 200],
            fill=(dom_color[0], dom_color[1], dom_color[2], 24),
        )
        img = Image.alpha_composite(img, ambient)
        draw = ImageDraw.Draw(img)
        
        # 2. Smart Scaling Title
        title_text = slide.get("title", "").upper()
        font_size = 72
        title_font = get_font(font_size, is_bold=True, family="Montserrat")
        
        # Recursive shrink to fit
        while font_size > 40:
            wrapped = textwrap.wrap(title_text, width=int(20 * (72/font_size)))
            th = len(wrapped) * (font_size + 10)
            if th < 250: break
            font_size -= 4
            title_font = get_font(font_size, is_bold=True, family="Montserrat")
        
        y = 100
        for line in textwrap.wrap(title_text, width=int(22 * (72/font_size))):
            draw.text((80, y), line, fill="#FFFFFF", font=title_font)
            y += font_size + 10
        
        # 3. Illustration (Elevated)
        inner_img = elevated_img.resize((560, 560)) if elevated_img.width > 600 else elevated_img
        img.paste(inner_img, (int((width - inner_img.width)/2), y + 20), inner_img)
        y += inner_img.height + 40
        
        # 4. Content (with Color Sync)
        font_size_body = 34
        body_font = get_font(font_size_body, family="Inter")
        
        # Color syncing bullet point
        bullet_color = (dom_color[0], dom_color[1], dom_color[2])
        
        content_limit = height - 150
        for point in slide.get("content", []):
            if y > content_limit: break
            lines = textwrap.wrap(f"• {point}", width=45)
            for line in lines:
                draw.text((80, y), line, fill="#CBD5E1", font=body_font)
                y += 42
            y += 12

        # 5. Footer & Branding
        footer_font = get_font(26, is_bold=True, family="Inter")
        draw.text((80, height - 90), f"{brand_name} • {handle}", fill=primary_color, font=footer_font)
        if cta_text and idx == len(slides) - 1:
            draw.text((80, height - 140), cta_text, fill="#CBD5E1", font=get_font(22, family="Inter"))
        
        # Page indicator with pill background
        page_txt = f"{idx+1} / {len(slides)}"
        pw = draw.textbbox((0,0), page_txt, font=footer_font)[2]
        draw.rounded_rectangle([width - pw - 100, height - 100, width - 60, height - 50], radius=25, fill=(255,255,255,20))
        draw.text((width - pw - 80, height - 90), page_txt, fill="#94A3B8", font=footer_font)

        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        rendered_slides.append(buf.getvalue())
    
    return rendered_slides
