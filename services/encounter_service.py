from collections import Counter

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.encounter import Encounter
from schemas.encounter import EncounterCreate, EncounterUpdate, StatsResponse, CountryStats


async def create_encounter(
    db: AsyncSession, user_id: str, data: EncounterCreate
) -> Encounter:
    encounter = Encounter(user_id=user_id, **data.model_dump())
    db.add(encounter)
    await db.commit()
    await db.refresh(encounter)
    return encounter


async def get_encounters(db: AsyncSession, user_id: str) -> list[Encounter]:
    result = await db.execute(
        select(Encounter)
        .where(Encounter.user_id == user_id)
        .order_by(Encounter.date.desc())
    )
    return list(result.scalars().all())


async def get_encounter_by_id(
    db: AsyncSession, user_id: str, encounter_id: str
) -> Encounter:
    result = await db.execute(
        select(Encounter).where(
            Encounter.id == encounter_id, Encounter.user_id == user_id
        )
    )
    encounter = result.scalar_one_or_none()
    if not encounter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")
    return encounter


async def update_encounter(
    db: AsyncSession, user_id: str, encounter_id: str, data: EncounterUpdate
) -> Encounter:
    encounter = await get_encounter_by_id(db, user_id, encounter_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(encounter, key, value)
    await db.commit()
    await db.refresh(encounter)
    return encounter


async def delete_encounter(
    db: AsyncSession, user_id: str, encounter_id: str
) -> None:
    encounter = await get_encounter_by_id(db, user_id, encounter_id)
    await db.delete(encounter)
    await db.commit()


async def get_stats(db: AsyncSession, user_id: str) -> StatsResponse:
    encounters = await get_encounters(db, user_id)

    country_counter: Counter[str] = Counter()
    country_names: dict[str, str] = {}
    gender_counter: Counter[str] = Counter()

    for enc in encounters:
        country_counter[enc.country_code] += 1
        country_names[enc.country_code] = enc.country_name
        gender_counter[enc.gender] += 1

    countries_detail = [
        CountryStats(country_code=code, country_name=country_names[code], count=count)
        for code, count in country_counter.most_common()
    ]

    return StatsResponse(
        total_encounters=len(encounters),
        total_countries=len(country_counter),
        countries_detail=countries_detail,
        by_gender=dict(gender_counter),
    )
