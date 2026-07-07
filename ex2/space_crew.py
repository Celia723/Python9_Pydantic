from enum import Enum
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ValidationError, model_validator


class CrewRank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: CrewRank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def validate_mission(self):
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")
        has_lider = any(m.rank in [CrewRank.CAPTAIN, CrewRank.COMMANDER]
                        for m in self.crew)
        if not has_lider:
            raise ValueError(
                "Miission Must have at least one Commander or Captain")
        if self.duration_days > 365:
            experts = sum(m.years_experience >= 5 for m in self.crew)
            if experts < len(self.crew) / 2:
                raise ValueError(
                    "Long missions (> 365 days)" +
                    "need 50% experienced crew (5+ years)")
        if any(not m.is_active for m in self.crew):
            raise ValueError("All crew members must be active")
        return self


if __name__ == "__main__":
    print("Space Mission Crew Validation")
    print("=========================================")

    comandante = CrewMember(
        member_id="C01", name="Sarah Connor", rank=CrewRank.COMMANDER,
        age=40, specialization="Mission Command",
        years_experience=10, is_active=True
    )
    teniente = CrewMember(
        member_id="L01", name="John Smith", rank=CrewRank.LIEUTENANT,
        age=32, specialization="Navigation", years_experience=6, is_active=True
    )
    oficial = CrewMember(
        member_id="O01", name="Alice Johnson", rank=CrewRank.OFFICER,
        age=28, specialization="Engineering",
        years_experience=3, is_active=True
    )

    try:
        mision_valida = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime.now(),
            duration_days=900,
            crew=[comandante, teniente, oficial],
            budget_millions=2500.0
        )
        print("Valid mission created:")
        print(f"Mission: {mision_valida.mission_name}")
        print(f"ID: {mision_valida.mission_id}")
        print(f"Destination: {mision_valida.destination}")
        print(f"Duration: {mision_valida.duration_days} days")
        print(f"Budget: ${mision_valida.budget_millions}M")
        print(f"Crew size: {len(mision_valida.crew)}")
        print("Crew members:")
        for m in mision_valida.crew:
            print(f" - {m.name} ({m.rank.value}) - {m.specialization}")

    except ValidationError as e:
        print("Error inesperado en misión válida:")
        print(e)

    print("=========================================")

    try:
        #   Incorrect mission test
        mision_invalida = SpaceMission(
            mission_id="M2024_FAIL",
            mission_name="Unguided Mission",
            destination="Moon",
            launch_date=datetime.now(),
            duration_days=100,
            crew=[oficial],
            budget_millions=500.0
        )
    except ValidationError as e:
        print("Expected validation error:")
        print(e.errors()[0]["msg"])
