from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, Field


class EncounterCreate(BaseModel):
    nickname: str = Field(min_length=1, max_length=100)
    gender: str = Field(pattern="^(male|female|other)$")
    country_code: str = Field(min_length=2, max_length=3)
    country_name: str = Field(min_length=1, max_length=100)
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date: datetime
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class EncounterUpdate(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class EncounterResponse(BaseModel):
    id: str
    nickname: str
    gender: str
    country_code: str
    country_name: str
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    date: datetime
    notes: Optional[str]
    photo_url: Optional[str]
    rating: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class CountryStats(BaseModel):
    country_code: str
    country_name: str
    count: int


class StatsResponse(BaseModel):
    total_encounters: int
    total_countries: int
    countries_detail: List[CountryStats]
    by_gender: Dict[str, int]
