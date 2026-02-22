from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Person:
    pid: int
    first_name: str
    last_name: str
    gender: str  # e.g., "F", "M"
    birth_year: int
    death_year: Optional[int] = None

    partner_id: Optional[int] = None
    children_ids: List[int] = field(default_factory=list)

    def is_alive(self, year: int) -> bool:
        if year < self.birth_year:
            return False
        if self.death_year is None:
            return True
        return year <= self.death_year

    def age_in(self, year: int) -> int:
        return year - self.birth_year

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "partner_id": self.partner_id,
            "children_ids": list(self.children_ids),
        }