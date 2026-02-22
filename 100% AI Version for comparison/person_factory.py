from __future__ import annotations
import random
from typing import Dict, Any, List, Optional, Tuple

from person import Person
from samplers import weighted_choice, clamp01, infer_rate_scale
from data_loader import (
    detect_rank_prob_columns,
    detect_gender_name_columns,
    detect_life_expectancy_columns,
)

class PersonFactory:
    def __init__(
        self,
        rng: random.Random,
        rank_to_prob: List[Dict[str, Any]],
        last_names: List[str],
        gender_name_prob: List[Dict[str, Any]],
        life_expectancy: List[Dict[str, Any]],
    ):
        self.rng = rng
        self.rank_to_prob = rank_to_prob
        self.last_names = last_names or ["Smith"]

        # Prepare first-name distribution
        self.rank_col, self.rank_prob_col = detect_rank_prob_columns(rank_to_prob)
        self._rank_weights = []
        self._ranks = []
        for row in rank_to_prob:
            r = str(row.get(self.rank_col, "")).strip()
            if not r:
                continue
            self._ranks.append(r)
            self._rank_weights.append(float(str(row.get(self.rank_prob_col, "0") or "0").strip() or 0))

        # Prepare gender/name distribution
        self.name_col, self.gender_col, self.name_prob_col = detect_gender_name_columns(gender_name_prob)
        self._names_by_gender: Dict[str, Tuple[List[str], List[float]]] = {}
        for row in gender_name_prob:
            name = str(row.get(self.name_col, "")).strip()
            if not name:
                continue
            gender = str(row.get(self.gender_col, "U")).strip() if self.gender_col != "__missing_gender__" else "U"
            prob = float(str(row.get(self.name_prob_col, "0") or "0").strip() or 0)
            g = gender.upper()[:1] if gender else "U"
            self._names_by_gender.setdefault(g, ([], []))
            self._names_by_gender[g][0].append(name)
            self._names_by_gender[g][1].append(prob)

        # Life expectancy by gender (expected age at death)
        self.le_gender_col, self.le_col = detect_life_expectancy_columns(life_expectancy)
        self._life_by_gender: Dict[str, List[float]] = {}
        for row in life_expectancy:
            g = str(row.get(self.le_gender_col, "U")).strip().upper()[:1]
            le = float(str(row.get(self.le_col, "0") or "0").strip() or 0)
            if le > 0:
                self._life_by_gender.setdefault(g, []).append(le)

        # If no gender-specific, fall back to all
        all_le = []
        for vs in self._life_by_gender.values():
            all_le.extend(vs)
        self._life_by_gender.setdefault("U", all_le or [78.0])

        self._next_id = 1

    def _sample_gender(self) -> str:
        # Simple baseline; if you want it data-driven, add a gender ratio CSV.
        return "F" if self.rng.random() < 0.5 else "M"

    def _sample_first_name(self, gender: str) -> str:
        g = gender.upper()[:1]
        if g in self._names_by_gender and self._names_by_gender[g][0]:
            names, weights = self._names_by_gender[g]
            return weighted_choice(names, weights, self.rng)

        # fallback to "U" bucket
        if "U" in self._names_by_gender and self._names_by_gender["U"][0]:
            names, weights = self._names_by_gender["U"]
            return weighted_choice(names, weights, self.rng)

        # final fallback
        return "Alex"

    def _sample_last_name(self, allowed: Optional[List[str]] = None) -> str:
        pool = allowed if allowed else self.last_names
        return self.rng.choice(pool) if pool else "Smith"

    def _sample_expected_death_age(self, gender: str) -> int:
        g = gender.upper()[:1]
        pool = self._life_by_gender.get(g) or self._life_by_gender["U"]
        # Use a normal-ish spread around mean life expectancy:
        mean = sum(pool) / max(1, len(pool))
        # SD 12 is a reasonable broad spread; clamp to realistic
        age = int(round(self.rng.gauss(mean, 12.0)))
        age = max(1, min(age, 110))
        return age

    def create_person(
        self,
        birth_year: int,
        gender: Optional[str] = None,
        allowed_last_names: Optional[List[str]] = None,
    ) -> Person:
        gender = gender or self._sample_gender()
        first = self._sample_first_name(gender)
        last = self._sample_last_name(allowed_last_names)
        death_age = self._sample_expected_death_age(gender)
        death_year = birth_year + death_age

        p = Person(
            pid=self._next_id,
            first_name=first,
            last_name=last,
            gender=gender,
            birth_year=birth_year,
            death_year=death_year,
        )
        self._next_id += 1
        return p