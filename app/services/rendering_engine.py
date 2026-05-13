import io
import logging
import textwrap
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
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

def draw_aurora_gradient(width, height, dominant_colors):
    """
    Creates a modern 'Mesh Gradient' effect using overlapping radial blobs.
    """
    # Use a very deep, rich slate as the base
    base = Image.new("RGBA", (width, height), (7, 7, 14, 255)) 
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # Draw 4-6 large blurred color blobs (Auroras)
    for color_hex in dominant_colors[:6]:
        try:
            rgb = hex_to_rgb(color_hex)
        except:
            rgb = (37, 99, 235) # Fallback blue
            
        blob_size = random.randint(int(width*0.9), int(width*1.6))
        blob = Image.new("RGBA", (blob_size, blob_size), (0, 0, 0, 0))
        d = ImageDraw.Draw(blob)
        
        # Draw radial gradient in the blob
        for r in range(blob_size // 2, 0, -10):
            alpha = int(35 * (1 - (r / (blob_size // 2))))
            d.ellipse([blob_size//2 - r, blob_size//2 - r, blob_size//2 + r, blob_size//2 + r], 
                       fill=(rgb[0], rgb[1], rgb[2], alpha))
        
        blob = blob.filter(ImageFilter.GaussianBlur(radius=120))
        x = random.randint(-blob_size//2, width - blob_size//2)
        y = random.randint(-blob_size//2, height - blob_size//2)
        overlay.paste(blob, (x, y), blob)
    
    return Image.alpha_composite(base, overlay)

def apply_frosted_glass_blur(bg_img, rect, radius=45, blur_radius=30, brightness=1.18):
    """
    Crops the background, blurs it, and pastes it back with a tint to create a real frosted glass effect.
    """
    rect = [int(r) for r in rect]
    # 1. Crop the area from background
    crop = bg_img.crop(rect).convert("RGBA")
    
    # 2. Apply heavy blur
    blurred = crop.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 3. Enhance brightness for that 'lit from behind' look
    enhancer = ImageEnhance.Brightness(blurred)
    blurred = enhancer.enhance(brightness)
    
    # 4. Add a white 'frost' tint + subtle highlight
    frost = Image.new("RGBA", blurred.size, (255, 255, 255, 18))
    blurred = Image.alpha_composite(blurred, frost)
    
    # 5. Create the card mask with rounded corners
    mask = Image.new("L", blurred.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, blurred.size[0], blurred.size[1]], radius=radius, fill=255)
    
    # 6. Final composite
    card = Image.new("RGBA", blurred.size, (0,0,0,0))
    card.paste(blurred, (0,0), mask=mask)
    
    # 7. Add double border (glow + sharp line)
    d_card = ImageDraw.Draw(card)
    d_card.rounded_rectangle([0, 0, blurred.size[0], blurred.size[1]], radius=radius, 
                            outline=(255, 255, 255, 30), width=4)
    d_card.rounded_rectangle([0, 0, blurred.size[0], blurred.size[1]], radius=radius, 
                            outline=(255, 255, 255, 60), width=1)
    
    return card

def add_film_grain(img, intensity=0.045):
    """Adds a professional film grain texture."""
    width, height = img.size
    noise = Image.effect_noise((width // 2, height // 2), 30)
    noise = noise.resize((width, height), Image.Resampling.NEAREST).convert("RGBA")
    alpha_mask = noise.split()[0].point(lambda p: int(p * intensity))
    noise.putalpha(alpha_mask)
    return Image.alpha_composite(img, noise)

def get_dominant_color(img):
    """Extracts dominant color for syncing design elements."""
    small_img = img.copy().resize((1, 1), Image.Resampling.LANCZOS)
    return small_img.getpixel((0, 0))

def apply_drop_shadow(img, offset=(15, 15), blur_radius=30, shadow_alpha=160):
    """Creates a high-end floating effect for illustrations."""
    shadow = Image.new("RGBA", (img.width + abs(offset[0]) + blur_radius*2, img.height + abs(offset[1]) + blur_radius*2), (0,0,0,0))
    alpha = img.getchannel('A')
    shadow.paste((0, 0, 0, shadow_alpha), (blur_radius, blur_radius), mask=alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    final_img = Image.new("RGBA", shadow.size, (0,0,0,0))
    final_img.paste(shadow, (0,0))
    final_img.paste(img, (blur_radius - offset[0]//2, blur_radius - offset[1]//2), mask=img)
    return final_img

def _get_image_client() -> genai.Client | None:
    global _image_client
    if _image_client is not None: return _image_client
    if not settings.GEMINI_API_KEY: return None
    try:
        _image_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return _image_client
    except Exception as err:
        logger.warning(f"Gemini image client init failed: {err}")
        return None

def _aspect_ratio(width: int, height: int) -> str:
    ratio = width / height if height else 1
    if abs(ratio - 1.0) < 0.05: return "1:1"
    if abs(ratio - 4 / 5) < 0.05: return "4:5"
    if abs(ratio - 9 / 16) < 0.05: return "9:16"
    if abs(ratio - 16 / 9) < 0.05: return "16:9"
    return "1:1"

def _extract_image_bytes(response: types.GenerateContentResponse) -> bytes | None:
    parts = []
    if getattr(response, "candidates", None):
        for candidate in response.candidates:
            content = getattr(candidate, "content", None)
            candidate_parts = getattr(content, "parts", None) if content else None
            if candidate_parts: parts.extend(candidate_parts)
    if not parts and getattr(response, "parts", None): parts.extend(response.parts)
    for part in parts:
        inline_data = getattr(part, "inline_data", None)
        if inline_data and getattr(inline_data, "data", None): return inline_data.data
    return None

def _placeholder_image(width: int, height: int) -> Image.Image:
    return Image.new("RGBA", (width, height), (30, 41, 59, 255))

def _generate_gemini_image(prompt: str, width: int, height: int, generation_mode: str = "creative") -> Image.Image:
    client = _get_image_client()
    if client is None: return _placeholder_image(width, height)
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=[types.Modality.IMAGE],
                image_config=types.ImageConfig(aspectRatio=_aspect_ratio(width, height)),
                tools=[types.Tool(google_search=types.GoogleSearch())] if generation_mode == "grounded" else None,
            ),
        )
        image_bytes = _extract_image_bytes(response)
        if not image_bytes: return _placeholder_image(width, height)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        return ImageOps.fit(img, (width, height), Image.Resampling.LANCZOS)
    except Exception as err:
        logger.warning(f"Gemini image generation failed: {err}")
        return _placeholder_image(width, height)

def get_preset_spec(export_preset: str | None, is_carousel: bool) -> dict:
    if export_preset in PRESET_SPECS: return PRESET_SPECS[export_preset]
    return {"width": 1080, "height": 1080} if is_carousel else {"width": 1300, "height": 1800}

def _fit_to_canvas(img: Image.Image, target_width: int, target_height: int, bg_color: tuple[int, int, int]) -> Image.Image:
    fitted = ImageOps.contain(img, (target_width, target_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_width, target_height), bg_color)
    offset = ((target_width - fitted.width) // 2, (target_height - fitted.height) // 2)
    canvas.paste(fitted, offset)
    return canvas

def render_image(layout_data: dict, export_preset: str | None = None, generation_mode: str = "creative") -> bytes:
    logger.info("Rendering ultra-premium infographic with Aurora gradients and frosted glass...")
    
    title = layout_data.get("title", "Infographic Title").upper()
    sections = layout_data.get("sections", [])
    theme = layout_data.get("theme", {})
    handle = layout_data.get("author_handle", "@VibeGraphic")
    
    title_font = get_font(72, is_bold=True, family="Montserrat")
    section_title_font = get_font(40, is_bold=True, family="Montserrat")
    body_font = get_font(24, family="Inter")
    point_font = get_font(24, is_bold=True, family="Inter")
    footer_font = get_font(22, family="Inter")

    width = 1300 
    margin_x = 90
    card_width = width - (margin_x * 2)
    base_img_width, base_img_height = 460, 340
    
    all_accent_colors = [theme.get("primary_color", "#3B82F6"), theme.get("secondary_color", "#8B5CF6")]
    wrapped_sections = []
    total_height = 280 + (len(textwrap.wrap(title, width=32)) * 90)
    
    for sec in sections:
        prompt = sec.get("illustration_prompt", "abstract neon technology")
        img_prompt = f"{prompt}, premium 3D isometric masterpiece, volumetric lighting, deep focus, label-safe, 8k resolution"
        sec_img = _generate_gemini_image(img_prompt, base_img_width, base_img_height, generation_mode)
        
        mask = Image.new("L", sec_img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, sec_img.width, sec_img.height], radius=45, fill=255)
        rounded_img = Image.new("RGBA", sec_img.size, (0,0,0,0))
        rounded_img.paste(sec_img, (0,0), mask=mask)
        
        dom_color = get_dominant_color(rounded_img)
        all_accent_colors.append('#%02x%02x%02x' % dom_color[:3])
        elevated_img = apply_drop_shadow(rounded_img, blur_radius=40, shadow_alpha=190)
        
        desc_wrap = textwrap.wrap(sec.get("description", ""), width=45)
        points_wrap = [textwrap.wrap(f"• {pt}", width=45) for pt in sec.get("points", [])]
        
        text_h = 130 + (len(desc_wrap) * 38) + (sum(len(p) for p in points_wrap) * 36)
        sec_h = max(text_h, elevated_img.height + 110)
        
        wrapped_sections.append({
            "heading": textwrap.wrap(sec.get("heading", ""), width=40),
            "description": desc_wrap, "points": points_wrap,
            "height": sec_h, "image": elevated_img, "accent_color": dom_color
        })
        total_height += sec_h + 100
    
    total_height += 200
    bg = draw_aurora_gradient(width, total_height, all_accent_colors)
    draw = ImageDraw.Draw(bg)

    curr_y = 140
    for line in textwrap.wrap(title, width=32):
        lw = draw.textbbox((0,0), line, font=title_font)[2]
        draw.text(((width - lw)/2 + 4, curr_y + 4), line, fill=(0,0,0,150), font=title_font)
        draw.text(((width - lw)/2, curr_y), line, fill="#FFFFFF", font=title_font)
        curr_y += 95
    curr_y += 80

    for idx, sec in enumerate(wrapped_sections):
        card_rect = [margin_x, curr_y, margin_x + card_width, curr_y + sec["height"]]
        glass_card = apply_frosted_glass_blur(bg, card_rect, radius=50)
        bg.paste(glass_card, (int(card_rect[0]), int(card_rect[1])), glass_card)
        
        is_even = idx % 2 == 0
        img_x = margin_x + 60 if is_even else margin_x + card_width - sec["image"].width - 60
        text_x = margin_x + sec["image"].width + 100 if is_even else margin_x + 80
        
        bg.paste(sec["image"], (int(img_x), int(curr_y + 55)), sec["image"])
        
        inner_y = curr_y + 80
        accent = sec["accent_color"]
        draw.line([text_x, inner_y, text_x + 100, inner_y], fill=(accent[0], accent[1], accent[2], 255), width=12)
        inner_y += 60
        
        for line in sec["heading"]:
            draw.text((text_x, inner_y), line, fill="#FFFFFF", font=section_title_font)
            inner_y += 56
        inner_y += 28
        
        for line in sec["description"]:
            draw.text((text_x, inner_y), line, fill="#CBD5E1", font=body_font)
            inner_y += 38
        inner_y += 35
        
        for lines in sec["points"]:
            first = True
            for line in lines:
                prefix = "• " if first else "  "
                draw.text((text_x, inner_y), f"{prefix}{line}", fill="#F8FAFC" if first else "#94A3B8", font=point_font if first else body_font)
                inner_y += 36
                first = False
            inner_y += 18
            
        curr_y += sec["height"] + 100

    footer_txt = f"CREATED WITH VIBEGRAPHIC • {handle}"
    lw = draw.textbbox((0,0), footer_txt, font=footer_font)[2]
    draw.text(((width - lw)/2, total_height - 100), footer_txt, fill="#94A3B8", font=footer_font)

    final = add_film_grain(bg, intensity=0.05)
    final = final.convert('RGB')
    
    if export_preset:
        spec = get_preset_spec(export_preset, False)
        final = _fit_to_canvas(final, spec["width"], spec["height"], (10,10,18))

    buf = io.BytesIO()
    final.save(buf, format='PNG', optimize=True)
    return buf.getvalue()

def render_carousel(carousel_data: dict, width: int = 1080, height: int = 1080, export_preset: str | None = None, generation_mode: str = "creative") -> list[bytes]:
    spec = get_preset_spec(export_preset, True)
    width, height = spec["width"], spec["height"]
    slides_data = carousel_data.get("slides", [])
    theme = carousel_data.get("theme", {})
    accent_base = theme.get("primary_color", "#3B82F6")
    handle = carousel_data.get("author_handle", "@VibeGraphic")
    
    master_bg = draw_aurora_gradient(width, height, [accent_base, theme.get("secondary_color", "#8B5CF6")])
    
    rendered_slides = []
    for idx, slide in enumerate(slides_data):
        slide_bg = master_bg.copy()
        draw = ImageDraw.Draw(slide_bg)
        
        img_prompt = f"{slide.get('image_prompt')}, premium 3D design asset, volumetric lighting, deep shadows"
        illustration = _generate_gemini_image(img_prompt, 640, 640, generation_mode)
        illustration = apply_drop_shadow(illustration, blur_radius=50, shadow_alpha=170)
        
        title_text = slide.get("title", "").upper()
        font_size = 80
        title_font = get_font(font_size, is_bold=True, family="Montserrat")
        while font_size > 48:
            wrapped = textwrap.wrap(title_text, width=int(18 * (80/font_size)))
            if (len(wrapped) * (font_size + 20)) < 340: break
            font_size -= 4
            title_font = get_font(font_size, is_bold=True, family="Montserrat")
        
        cy = 120
        for line in textwrap.wrap(title_text, width=int(22 * (80/font_size))):
            draw.text((100, cy), line, fill="#FFFFFF", font=title_font)
            cy += font_size + 20
        
        scale = min(1.0, (height - cy - 380) / illustration.height)
        if scale < 1.0:
            illustration = illustration.resize((int(illustration.width * scale), int(illustration.height * scale)))
        slide_bg.paste(illustration, (int((width - illustration.width)/2), cy + 50), illustration)
        cy += illustration.height + 80
        
        body_font = get_font(38, family="Inter")
        for point in slide.get("content", []):
            if cy > height - 170: break
            for line in textwrap.wrap(f"• {point}", width=40):
                draw.text((100, cy), line, fill="#E2E8F0", font=body_font)
                cy += 52
            cy += 20
            
        footer_font = get_font(32, is_bold=True, family="Inter")
        draw.text((100, height - 120), handle, fill=accent_base, font=footer_font)
        
        final_slide = add_film_grain(slide_bg, intensity=0.045)
        buf = io.BytesIO()
        final_slide.convert("RGB").save(buf, format="PNG")
        rendered_slides.append(buf.getvalue())
        
    return rendered_slides
