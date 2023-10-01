import json

from icecream import ic
from pydantic import BaseModel
from typing import List, Dict


class Attributes(BaseModel):
    EXPERIENCE: float
    LEVEL: float
    HIT_POINTS: float
    ABILITY_POINTS: float
    MOVEMENT: float
    SPEED: float
    DEXTERITY: float
    MAGIC: float
    STRENGTH: float
    DEFENSE: float


class Unit(BaseModel):
    ResRef: str
    FirstName: str
    LastName: str
    Class: str
    PortraintLocation: str
    Sprite: str
    Type: str
    MovementSoundLocation: str
    Attributes: Attributes
    Inventory: Dict[str, int]
    Abilities: List[int]


class GameData(BaseModel):
    name: str
    lastUpdated: int
    version: str
    totalPlayTimeInSeconds: float
    currentScene: str
    units: List[Unit]

    @classmethod
    def load(cls, file_path: str = None) -> "GameData":
        try:
            if not file_path:
                file_path = "roe.json"
            with open(file_path, "r") as f:
                data = json.load(f)
                return cls.model_validate(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            ic(f"Failed to load game data: {e}")

    def dump(self) -> str:
        return json.dumps(self.model_dump(), indent=4)
