from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt_handler import get_current_user
from database import get_db
from models.user import User
from schemas.encounter import (
    EncounterCreate,
    EncounterResponse,
    EncounterUpdate,
    StatsResponse,
)
from services.encounter_service import (
    create_encounter,
    delete_encounter,
    get_encounter_by_id,
    get_encounters,
    get_stats,
    update_encounter,
)

router = APIRouter(prefix="/encounters", tags=["encounters"])


@router.get("/", response_model=list[EncounterResponse])
async def list_encounters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_encounters(db, current_user.id)


@router.post("/", response_model=EncounterResponse, status_code=201)
async def add_encounter(
    data: EncounterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_encounter(db, current_user.id, data)


@router.get("/stats", response_model=StatsResponse)
async def stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_stats(db, current_user.id)


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_one(
    encounter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_encounter_by_id(db, current_user.id, encounter_id)


@router.patch("/{encounter_id}", response_model=EncounterResponse)
async def update(
    encounter_id: str,
    data: EncounterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_encounter(db, current_user.id, encounter_id, data)


@router.delete("/{encounter_id}", status_code=204)
async def delete(
    encounter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_encounter(db, current_user.id, encounter_id)
