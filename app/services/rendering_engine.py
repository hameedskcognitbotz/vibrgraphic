import io
import logging
import textwrap
import requests
import urllib.parse
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def get_font(size: int, is_bold: bool = False):
    try:
        # On Windows, try to load standard fonts
        font_name = "arialbd.ttf" if is_bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except IOError:
        return ImageFont.load_default()

def draw_gradient_background(draw, width, height, start_color, end_color):
    """Draws a smooth linear gradient from top to bottom."""
    r1, g1, b1 = start_color
    r2, g2, b2 = end_color
    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def render_image(layout_data: dict) -> bytes:
    """
    Renders a stunning, premium infographic using Pillow.
    Fetches real images dynamically per section, and wraps deep rich text.
    """
    logger.info("Rendering premium layout with pictures via Pillow...")
    
    content_blocks = layout_data.get("content_blocks", {})
    title = content_blocks.get("title", "Infographic Title").upper()
    sections = content_blocks.get("sections", [])
    
    # Fonts
    title_font = get_font(56, is_bold=True)
    section_title_font = get_font(32, is_bold=True)
    body_font = get_font(20)
    point_font = get_font(20, is_bold=True)
    footer_font = get_font(18)

    # Layout dimensions
    width = 1300 
    margin_x = 80
    card_width = width - (margin_x * 2)
    img_width = 400
    img_height = 300
    
    # Calculate Title Height
    wrapped_title = textwrap.wrap(title, width=35)
    title_height = 100 + (len(wrapped_title) * 60)
    
    total_height = title_height
    wrapped_sections = []
    
    def fetch_section_image(sec):
        # Fetch image logic
        base_prompt = sec.get("image_prompt", "abstract technology")
        img_prompt = f"{base_prompt}, vibrant 3D isometric illustration, transparent background style"
        encoded_prompt = urllib.parse.quote(img_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={img_width}&height={img_height}&nologo=true"
        
        try:
            logger.info(f"Downloading image for prompt: {img_prompt}")
            res = requests.get(img_url, timeout=10)
            sec_img = Image.open(io.BytesIO(res.content)).convert("RGBA")
        except Exception as e:
            logger.error(f"Failed to fetch image: {e}")
            # Fallback blank box outline
            sec_img = Image.new("RGBA", (img_width, img_height), color=(30, 41, 59, 255))
            d = ImageDraw.Draw(sec_img)
            d.rectangle([0,0, img_width-1, img_height-1], fill=(40,50,70,255), outline=(100,100,100,255), width=2)
            d.text((50, 140), "Image Unavailable", fill="white", font=body_font)
            
        # Optional rounded corners for fetched images
        mask = Image.new("L", (img_width, img_height), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([0, 0, img_width, img_height], radius=20, fill=255)
        rounded_img = Image.new("RGBA", sec_img.size, (0,0,0,0))
        rounded_img.paste(sec_img, (0,0), mask=mask)
        return rounded_img

    # Fetch all images in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sections) if sections else 1) as executor:
        rounded_images = list(executor.map(fetch_section_image, sections))
    
    for sec, rounded_img in zip(sections, rounded_images):
        desc_wrap = textwrap.wrap(sec.get("description", ""), width=55)
        points_wrap = []
        for pt in sec.get("points", []):
            lines = textwrap.wrap(f"• {pt}", width=55)
            points_wrap.append(lines)
            
        # Determine height based on the maximum between text vs image
        text_h = 40 + (len(textwrap.wrap(sec.get("heading", ""), width=50)) * 40) + (len(desc_wrap) * 30) + 30 + sum(len(lines) * 28 for lines in points_wrap) + 50
        sec_h = max(text_h, img_height + 80)
        
        wrapped_sections.append({
            "heading": textwrap.wrap(sec.get("heading", ""), width=50),
            "description": desc_wrap,
            "points": points_wrap,
            "height": sec_h,
            "image": rounded_img
        })
        total_height += sec_h + 40 # gap between cards
        
    total_height += 150 # Footer spacing
    
    # Create high-res Image Canvas
    img = Image.new('RGB', (width, total_height))
    draw = ImageDraw.Draw(img)

    # Gradient Background (Deep Slate to Midnight Violet)
    draw_gradient_background(draw, width, total_height, (15, 23, 42), (46, 16, 101))

    # Pattern
    draw.ellipse([-100, -100, 300, 300], fill=(255, 255, 255, 5))
    draw.ellipse([width-400, total_height-500, width+100, total_height+100], fill=(139, 92, 246, 10))

    # Draw Title
    current_y = 60
    for line in wrapped_title:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_w = bbox[2] - bbox[0]
        except AttributeError:
            line_w, _ = draw.textsize(line, font=title_font)
            
        x_pos = (width - line_w) / 2
        draw.text((x_pos+3, current_y+3), line, fill=(0,0,0,150), font=title_font) # deeper shadow
        draw.text((x_pos, current_y), line, fill="#F8FAFC", font=title_font)
        current_y += 65
    current_y += 40

    # Draw Cards 
    for idx, sec in enumerate(wrapped_sections):
        card_rect = [margin_x, current_y, margin_x + card_width, current_y + sec["height"]]
        try:
            draw.rounded_rectangle(card_rect, radius=20, fill="#1E293B", outline="#3B82F6", width=2)
        except AttributeError:
            draw.rectangle(card_rect, fill="#1E293B", outline="#3B82F6", width=2)
            
        # Image Placement Logic (Alternate left/right)
        is_even = idx % 2 == 0
        img_x = margin_x + 30 if is_even else margin_x + card_width - img_width - 30
        text_x_start = margin_x + 30 + img_width + 40 if is_even else margin_x + 40
        
        # Paste Image
        img_y = current_y + 40
        img.paste(sec["image"], (int(img_x), int(img_y)), sec["image"])
        
        # Draw Text
        inner_y = current_y + 40
        
        # Heading
        for line in sec["heading"]:
            draw.text((text_x_start, inner_y), line, fill="#38BDF8", font=section_title_font)
            inner_y += 40
        inner_y += 10
        
        # Description
        for line in sec["description"]:
            draw.text((text_x_start, inner_y), line, fill="#E2E8F0", font=body_font)
            inner_y += 30
        inner_y += 20
        
        # Points
        for line_group in sec["points"]:
            for i, line in enumerate(line_group):
                x_offset = text_x_start + 20 if i == 0 else text_x_start + 35
                color = "#A7F3D0" if i == 0 else "#94A3B8" # light green for bullets
                font_to_use = point_font if i == 0 else body_font
                draw.text((x_offset, inner_y), line, fill=color, font=font_to_use)
                inner_y += 28
            inner_y += 10
            
        current_y += sec["height"] + 40

    # Draw Footer
    footer_txt = "Generated securely by AI Infographic Generator  |  Stunning Graphical Layouts"
    try:
        bbox = draw.textbbox((0, 0), footer_txt, font=footer_font)
        fw = bbox[2] - bbox[0]
    except AttributeError:
        fw, _ = draw.textsize(footer_txt, font=footer_font)
        
    draw.line([(width/2 - 200, current_y), (width/2 + 200, current_y)], fill="#475569", width=1)
    draw.text(((width - fw) / 2, current_y + 30), footer_txt, fill="#94A3B8", font=footer_font)

    # Export
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG', optimize=True)
    return img_byte_arr.getvalue()
