from __future__ import annotations
import random
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

def _norm(s: str) -> str:
    return "".join(ch.lower() for ch in s.strip() if ch.isalnum() or ch in ("_", "-"))

def pick_column(columns: Sequence[str], *candidates: str) -> Optional[str]:
    """
    Find the first matching column name from candidates, allowing fuzzy normalization.
    """
    norm_map = {_norm(c): c for c in columns}
    for cand in candidates:
        nc = _norm(cand)
        if nc in norm_map:
            return norm_map[nc]
    return None

def weighted_choice(items: Sequence[Any], weights: Sequence[float], rng: random.Random) -> Any:
    if not items:
        raise ValueError("weighted_choice: empty items")
    if len(items) != len(weights):
        raise ValueError("weighted_choice: items/weights length mismatch")
    total = 0.0
    cum = []
    for w in weights:
        w = max(0.0, float(w))
        total += w
        cum.append(total)
    if total <= 0:
        return rng.choice(list(items))
    r = rng.random() * total
    # linear scan is fine for typical sizes; if huge, replace with bisect
    for item, c in zip(items, cum):
        if r <= c:
            return item
    return items[-1]

def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x

def infer_rate_scale(values: List[float]) -> float:
    """
    Tries to infer if rates look like:
    - already probabilities (0..1)
    - per-100 (0..100)
    - per-1000 (0..1000)
    Returns a divisor so value/divisor becomes a probability-like number.
    """
    if not values:
        return 1.0
    vmax = max(values)
    if vmax <= 1.0:
        return 1.0
    if vmax <= 100.0:
        return 100.0
    if vmax <= 1000.0:
        return 1000.0
    # if it's huge, assume per-1000 still (best guess)
    return 1000.0

def lookup_best_match(table: List[Dict[str, Any]], year: int, year_key: str) -> Optional[Dict[str, Any]]:
    """
    If exact year isn't found, returns nearest earlier year; else nearest later.
    """
    if not table:
        return None
    exact = [row for row in table if int(row[year_key]) == year]
    if exact:
        return exact[0]
    years = sorted({int(row[year_key]) for row in table})
    earlier = [y for y in years if y <= year]
    later = [y for y in years if y >= year]
    if earlier:
        target = max(earlier)
    elif later:
        target = min(later)
    else:
        target = years[0]
    for row in table:
        if int(row[year_key]) == target:
            return row
    return None