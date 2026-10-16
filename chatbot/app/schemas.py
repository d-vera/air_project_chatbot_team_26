from enum import Enum
from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
    ES = "ES"
    EN = "EN"


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The natural-language question about air quality measurements.",
        examples=["What is the current temperature?", "¿Cuál es el promedio de CO2 en la última semana?"],
    )


class ChatResponse(BaseModel):
    reply: str = Field(
        ...,
        description="The AI-generated natural-language answer in the user's preferred language.",
    )
    language: LanguageEnum = Field(
        ...,
        description="The language of the response, matching the user's preference.",
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Machine-readable error code.")
    message: str = Field(..., description="Human-readable error description.")


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Service health status.")
    version: str = Field("1.0.0", description="API version.")
