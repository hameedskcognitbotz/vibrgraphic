import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Color themes keyed by template name
TEMPLATE_THEMES = {
    "modern":      {"primary_color": "#6366F1", "accent_color": "#A5B4FC", "font_family": "Inter"},
    "minimal":     {"primary_color": "#111827", "accent_color": "#9CA3AF", "font_family": "DM Sans"},
    "corporate":   {"primary_color": "#1D4ED8", "accent_color": "#93C5FD", "font_family": "Roboto"},
    "bold":        {"primary_color": "#DC2626", "accent_color": "#FCA5A5", "font_family": "Poppins"},
    "data-driven": {"primary_color": "#059669", "accent_color": "#6EE7B7", "font_family": "IBM Plex Sans"},
}

DEFAULT_THEME = {"primary_color": "#1F2937", "accent_color": "#6B7280", "font_family": "Inter"}


def apply_template(structured_data: dict, design_index: int = 0) -> dict:
    """
    Adapts the single rich infographic data into layout metadata ready for
    the rendering engine.
    """
    logger.info("Applying layout template to rich structured data...")

    # If the legacy 'designs' structure still exists for some reason, handle it
    if "designs" in structured_data and isinstance(structured_data["designs"], list):
        designs = structured_data["designs"]
        if designs:
            selected = designs[min(design_index, len(designs) - 1)]
            template_name = selected.get("template", "modern")
            styling = TEMPLATE_THEMES.get(template_name, DEFAULT_THEME)
            return {
                "template_name": template_name,
                "title": structured_data.get("title", ""),
                "sections": selected.get("sections", []),
                "chart": selected.get("chart", {}),
                "styling": styling,
                "content_blocks": {
                    "title": structured_data.get("title", ""),
                    "sections": selected.get("sections", [])
                }
            }

    # New single-infographic structure
    theme = structured_data.get("theme", {})
    primary = theme.get("primary_color", "#4F46E5")
    secondary = theme.get("secondary_color", "#10B981")

    layout_data = {
        "template_name": structured_data.get("layout", "circular"),
        "title": structured_data.get("title", ""),
        "sections": structured_data.get("sections", []),
        "charts": structured_data.get("charts", []),
        "center_element": structured_data.get("center_element", {}),
        "styling": {
            "primary_color": primary,
            "accent_color": secondary,
            "font_family": "Inter"
        },
        # For backward compatibility with the current Pillow renderer
        "content_blocks": {
            "title": structured_data.get("title", ""),
            "sections": structured_data.get("sections", []),
            "charts": structured_data.get("charts", [])
        }
    }

    logger.info(
        f"Template '{layout_data['template_name']}' applied with {len(layout_data['sections'])} sections."
    )
    return layout_data
