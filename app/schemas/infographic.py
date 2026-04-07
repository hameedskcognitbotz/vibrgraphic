"""
Pydantic schemas for the rich infographic content output.
These mirror the JSON structure returned by generate_structured_content().
"""
from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

class ThemeSchema(BaseModel):
    background_color: str = Field(..., description="Hex code for background color")
    primary_color: str = Field(..., description="Hex code for primary color")
    secondary_color: str = Field(..., description="Hex code for secondary color")

class ChartData(BaseModel):
    type: Literal["bar", "pie", "line"] = Field(..., description="Type of chart")
    title: str = Field(..., description="A short, descriptive title for the chart")
    labels: List[str] = Field(..., description="Category or axis labels")
    data: List[float] = Field(..., description="Numeric values corresponding to labels")

class SectionSchema(BaseModel):
    heading: str = Field(..., description="Short section title (topic-specific)")
    description: str = Field(..., description="Short description of the section")
    points: List[str] = Field(..., min_length=2, max_length=4, description="2–4 informative bullet points")
    icon: str = Field(..., description="Single icon keyword relevant to topic (e.g. robot, chart, education)")
    illustration_prompt: str = Field(..., description="A vivid image generation prompt")
    color: str = Field(..., description="Hex code for the section specific color")
    layout_position: str = Field(..., description="Position in layout e.g. left, right, center, grid-1, grid-2, etc.")

class CenterElementSchema(BaseModel):
    title: str = Field(..., description="Main title or stat for center element")
    subtitle: str = Field(..., description="Secondary text for center element")
    icon: str = Field(..., description="Icon keyword for center element")

class InfographicData(BaseModel):
    title: str = Field(..., description="Compelling main headline for the infographic")
    layout: Literal["grid", "circular", "step-flow", "timeline"] = Field(..., description="Dynamically chosen layout type")
    theme: ThemeSchema = Field(..., description="Color theme for the infographic")
    sections: List[SectionSchema] = Field(..., min_length=6, max_length=8, description="6–8 content sections relevant ONLY to the topic")
    charts: List[ChartData] = Field(..., description="A list of relevant data charts")
    statistics: List[str] = Field(..., description="Key statistics (e.g. '75% adoption rate')")
    center_element: CenterElementSchema = Field(..., description="Center highlight element data")
