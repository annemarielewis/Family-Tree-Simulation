from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from samplers import pick_column

@dataclass
class LoadedData:
    rank_to_prob: List[Dict[str, Any]]
    last_names: List[str]
    gender_name_prob: List[Dict[str, Any]]
    life_expectancy: List[Dict[str, Any]]
    birth_marriage: List[Dict[str, Any]]

def _read_csv_dicts(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]

def _coerce_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        s = str(x).strip()
        if s == "":
            return default
        return float(s)
    except Exception:
        return default

def _coerce_int(x: Any, default: int = 0) -> int:
    try:
        if x is None:
            return default
        s = str(x).strip()
        if s == "":
            return default
        return int(float(s))
    except Exception:
        return default

def load_all(data_dir: Path) -> LoadedData:
    rank_to_prob = _read_csv_dicts(data_dir / "rank_to_probability.csv")
    last_names_rows = _read_csv_dicts(data_dir / "last_names.csv")
    gender_name_prob = _read_csv_dicts(data_dir / "gender_name_probability.csv")
    life_expectancy = _read_csv_dicts(data_dir / "life_expectancy.csv")
    birth_marriage = _read_csv_dicts(data_dir / "birth_and_marriage_rates.csv")

    # Normalize last names into a simple list
    last_names: List[str] = []
    if last_names_rows:
        cols = list(last_names_rows[0].keys())
        name_col = pick_column(cols, "last_name", "surname", "name", "lastname", "family_name")
        if name_col is None:
            # take first column if unknown
            name_col = cols[0]
        for row in last_names_rows:
            v = str(row.get(name_col, "")).strip()
            if v:
                last_names.append(v)
    return LoadedData(
        rank_to_prob=rank_to_prob,
        last_names=last_names,
        gender_name_prob=gender_name_prob,
        life_expectancy=life_expectancy,
        birth_marriage=birth_marriage,
    )

def detect_rank_prob_columns(rank_rows: List[Dict[str, Any]]) -> Tuple[str, str]:
    cols = list(rank_rows[0].keys())
    rank_col = pick_column(cols, "rank", "name_rank", "r")
    prob_col = pick_column(cols, "probability", "prob", "p", "weight", "freq", "frequency")
    if rank_col is None:
        rank_col = cols[0]
    if prob_col is None:
        prob_col = cols[1] if len(cols) > 1 else cols[0]
    return rank_col, prob_col

def detect_gender_name_columns(rows: List[Dict[str, Any]]) -> Tuple[str, str, str]:
    cols = list(rows[0].keys())
    name_col = pick_column(cols, "name", "first_name", "firstname", "given_name")
    gender_col = pick_column(cols, "gender", "sex")
    prob_col = pick_column(cols, "probability", "prob", "p", "weight", "freq", "frequency")
    if name_col is None:
        name_col = cols[0]
    if gender_col is None:
        # if missing, assume dataset separated by file or implicit; we will default to "U"
        gender_col = "__missing_gender__"
    if prob_col is None:
        prob_col = cols[1] if len(cols) > 1 else cols[0]
    return name_col, gender_col, prob_col

def detect_life_expectancy_columns(rows: List[Dict[str, Any]]) -> Tuple[str, str]:
    cols = list(rows[0].keys())
    gender_col = pick_column(cols, "gender", "sex")
    # Expect either "life_expectancy" or "expected_age" or "mean_age" etc.
    le_col = pick_column(cols, "life_expectancy", "expected_age", "mean_age", "age", "years")
    if gender_col is None:
        gender_col = cols[0]
    if le_col is None:
        le_col = cols[1] if len(cols) > 1 else cols[0]
    return gender_col, le_col

def detect_birth_marriage_columns(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    We support several common shapes:

    - By year only:
        year, birth_rate, marriage_rate
    - By year+age:
        year, age, birth_rate, marriage_rate
    - By year+age group:
        year, age_min, age_max, birth_rate, marriage_rate

    We'll detect:
        year_key, age_key (optional), age_min_key/age_max_key (optional),
        birth_key, marriage_key
    """
    cols = list(rows[0].keys())
    year_key = pick_column(cols, "year", "yr", "calendar_year")
    birth_key = pick_column(cols, "birth_rate", "births", "fertility_rate", "birth", "birthrate")
    marriage_key = pick_column(cols, "marriage_rate", "marriages", "partner_rate", "marriage", "marriagerate")

    age_key = pick_column(cols, "age", "mother_age", "adult_age")
    age_min_key = pick_column(cols, "age_min", "agemin", "min_age", "agefrom")
    age_max_key = pick_column(cols, "age_max", "agemax", "max_age", "ageto")

    if year_key is None:
        year_key = cols[0]
    if birth_key is None:
        # allow "births_per_1000" etc.
        birth_key = pick_column(cols, "births_per_1000", "births_per_100", "birth_probability")
        if birth_key is None:
            birth_key = cols[1] if len(cols) > 1 else cols[0]
    if marriage_key is None:
        marriage_key = pick_column(cols, "marriages_per_1000", "marriages_per_100", "marriage_probability")
        if marriage_key is None:
            marriage_key = cols[2] if len(cols) > 2 else (cols[1] if len(cols) > 1 else cols[0])

    return {
        "year": year_key,
        "age": age_key or "",
        "age_min": age_min_key or "",
        "age_max": age_max_key or "",
        "birth": birth_key,
        "marriage": marriage_key,
    }