from pydantic import BaseModel, Field, field_validator
from typing import Any

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=6, max_length=100)

class LoginRequest(BaseModel):
    email: str
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    rooms: list[str] = Field(min_length=1)
    style: str = Field(default="Modern", max_length=50)
    items: dict[str, int] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=500)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=10_000)
    event_type: str = Field(min_length=2, max_length=60)
    venue: str = Field(default="Indoor", max_length=80)
    city: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=500)

class Recommendation(BaseModel):
    name: str
    category: str
    platform: str
    estimated_price: float
    quantity: int = 1
    subtotal: float
    reason: str
    link: str

class PlannerResult(BaseModel):
    planner: str
    budget: float
    allocation: dict[str, float]
    total_estimate: float
    remaining: float
    summary: str
    recommendations: list[Recommendation]
    ai_used: bool = False
    disclaimer: str = "Prices and availability are estimates unless connected to an official provider API."

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="Elegant", max_length=80)
    metal: str = Field(default="Any", max_length=50)
    notes: str = Field(default="", max_length=500)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
