import io
import logging
import textwrap
import urllib.parse
import asyncio
import aiohttp
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")

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

def render_image(layout_data: dict) -> bytes:
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
    
    async def fetch_section_image(session, sec):
        prompt = sec.get("illustration_prompt", "abstract technology")
        img_prompt = f"{prompt}, vibrant 3C isometric 3D render, studio lighting, depth of field, high quality"
        encoded_prompt = urllib.parse.quote(img_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={base_img_width}&height={base_img_height}&nologo=true"
        
        try:
            async with session.get(img_url, timeout=10) as res:
                content = await res.read()
                sec_img = Image.open(io.BytesIO(content)).convert("RGBA")
        except:
            sec_img = Image.new("RGBA", (base_img_width, base_img_height), (30, 41, 59, 255))
            
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

    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_section_image(session, sec) for sec in sections]
            return await asyncio.gather(*tasks)

    image_results = asyncio.run(fetch_all())
    
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
    for _ in range(15):
        x, y = random.randint(0, width), random.randint(0, total_height)
        s = random.randint(100, 400)
        draw.ellipse([x, y, x+s, y+s], fill=(255,255,255,5))

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
    footer_txt = f"Powered by VibeGraphic Engine • Compiled for {handle}"
    lw = draw.textbbox((0,0), footer_txt, font=footer_font)[2]
    draw.text(((width - lw)/2, total_height - 100), footer_txt, fill="#475569", font=footer_font)

    buf = io.BytesIO()
    img.convert('RGB').save(buf, format='PNG', optimize=True)
    return buf.getvalue()

def render_carousel(carousel_data: dict, width: int = 1080, height: int = 1080) -> list[bytes]:
    """
    Renders a set of carousel slides (1080x1080) with premium typography and auto-scaling.
    """
    logger.info(f"Rendering premium carousel: {carousel_data.get('title')}")
    slides = carousel_data.get("slides", [])
    theme = carousel_data.get("theme", {})
    bg_color_hex = theme.get("background_color", "#0F172A")
    bg_color = hex_to_rgb(bg_color_hex)
    primary_color = theme.get("primary_color", "#3B82F6")
    handle = carousel_data.get("author_handle", "@VibeGraphic")

    async def fetch_slide_image(session, slide):
        prompt = f"{slide.get('image_prompt')}, premium 3D isometric render, isolated, studio lighting"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=600&nologo=true"
        try:
            async with session.get(url, timeout=10) as res:
                content = await res.read()
                img = Image.open(io.BytesIO(content)).convert("RGBA")
                # Apply drop shadow
                return apply_drop_shadow(img, blur_radius=20, shadow_alpha=100), get_dominant_color(img)
        except:
            return Image.new("RGBA", (600, 600), (0,0,0,0)), (59, 130, 246)

    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[fetch_slide_image(session, s) for s in slides])

    image_results = asyncio.run(fetch_all())
    rendered_slides = []

    for idx, (slide, (elevated_img, dom_color)) in enumerate(zip(slides, image_results)):
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # 1. Background Decoration
        draw.ellipse([width-400, -200, width+200, 400], fill=(255,255,255,10))
        draw.ellipse([-200, height-400, 400, height+200], fill=(dom_color[0], dom_color[1], dom_color[2], 15))
        
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
        draw.text((80, height - 90), handle, fill=primary_color, font=footer_font)
        
        # Page indicator with pill background
        page_txt = f"{idx+1} / {len(slides)}"
        pw = draw.textbbox((0,0), page_txt, font=footer_font)[2]
        draw.rounded_rectangle([width - pw - 100, height - 100, width - 60, height - 50], radius=25, fill=(255,255,255,20))
        draw.text((width - pw - 80, height - 90), page_txt, fill="#94A3B8", font=footer_font)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        rendered_slides.append(buf.getvalue())
    
    return rendered_slides
