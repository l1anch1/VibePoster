# backend/ai/app/schemas.py
from pydantic import BaseModel
from typing import List, Literal, Union, Optional


class BaseLayer(BaseModel):
    id: str
    name: str
    type: Literal["text", "image"]
    x: int
    y: int
    width: int
    height: int
    rotation: int = 0
    opacity: float = 1.0


class TextLayer(BaseLayer):
    type: Literal["text"]
    content: str
    fontSize: int
    color: str
    fontFamily: str = "Yuanti TC"
    textAlign: str = "left"
    fontWeight: str = "normal"


class ImageLayer(BaseLayer):
    type: Literal["image"]
    src: str


class Canvas(BaseModel):
    width: int = 1080
    height: int = 1920
    backgroundColor: str = "#FFFFFF"


class PosterData(BaseModel):
    canvas: Canvas
    layers: List[Union[TextLayer, ImageLayer]]
