from __future__ import annotations
import json
import random
from typing import Dict, Any, List, Optional, Tuple

from config import SimConfig
from person import Person
from person_factory import PersonFactory
from samplers import clamp01, infer_rate_scale
from data_loader import detect_birth_marriage_columns

class FamilyTree:
    def __init__(
        self,
        cfg: SimConfig,
        rng: random.Random,
        factory: PersonFactory,
        birth_marriage_rows: List[Dict[str, Any]],
    ):
        self.cfg = cfg
        self.rng = rng
        self.factory = factory

        self.people: Dict[int, Person] = {}
        self.founder_ids: List[int] = []

        self.birth_marriage_rows = birth_marriage_rows or []
        self.bm_cols = detect_birth_marriage_columns(self.birth_marriage_rows) if self.birth_marriage_rows else {}

        # Pre-infer scaling factors for rates
        self._birth_scale = 1.0
        self._marriage_scale = 1.0
        if self.birth_marriage_rows:
            birth_vals = []
            marriage_vals = []
            bkey = self.bm_cols["birth"]
            mkey = self.bm_cols["marriage"]
            for row in self.birth_marriage_rows:
                try:
                    birth_vals.append(float(str(row.get(bkey, "")).strip() or 0))
                    marriage_vals.append(float(str(row.get(mkey, "")).strip() or 0))
                except Exception:
                    pass
            self._birth_scale = infer_rate_scale(birth_vals)
            self._marriage_scale = infer_rate_scale(marriage_vals)

    def _get_rate_row_candidates(self, year: int) -> List[Dict[str, Any]]:
        if not self.birth_marriage_rows:
            return []
        ykey = self.bm_cols["year"]
        # gather all rows matching year, else nearest earlier year, else nearest later
        years = sorted({int(float(str(r.get(ykey, "0") or "0"))) for r in self.birth_marriage_rows})
        if year in years:
            target_year = year
        else:
            earlier = [y for y in years if y <= year]
            later = [y for y in years if y >= year]
            target_year = max(earlier) if earlier else (min(later) if later else years[0])

        out = []
        for r in self.birth_marriage_rows:
            ry = int(float(str(r.get(ykey, "0") or "0")))
            if ry == target_year:
                out.append(r)
        return out

    def _rate_for_age(self, year: int, age: int, kind: str) -> float:
        """
        Returns a probability-ish annual rate for:
          kind="birth" or kind="marriage"
        Supports tables by (year), (year+age), or (year+age_min+age_max).
        """
        rows = self._get_rate_row_candidates(year)
        if not rows:
            return 0.0

        key = self.bm_cols[kind]
        age_key = self.bm_cols.get("age", "")
        amin_key = self.bm_cols.get("age_min", "")
        amax_key = self.bm_cols.get("age_max", "")

        def to_float(v) -> float:
            try:
                return float(str(v).strip() or 0)
            except Exception:
                return 0.0

        # Case A: year+age exact
        if age_key:
            exact = []
            for r in rows:
                try:
                    ra = int(float(str(r.get(age_key, "9999") or "9999")))
                    if ra == age:
                        exact.append(r)
                except Exception:
                    continue
            if exact:
                raw = to_float(exact[0].get(key, 0))
                scale = self._birth_scale if kind == "birth" else self._marriage_scale
                mult = self.cfg.birth_rate_multiplier if kind == "birth" else self.cfg.marriage_rate_multiplier
                return clamp01((raw / scale) * mult)

        # Case B: year+age range
        if amin_key and amax_key:
            matches = []
            for r in rows:
                try:
                    amin = int(float(str(r.get(amin_key, "9999") or "9999")))
                    amax = int(float(str(r.get(amax_key, "-1") or "-1")))
                    if amin <= age <= amax:
                        matches.append(r)
                except Exception:
                    continue
            if matches:
                raw = to_float(matches[0].get(key, 0))
                scale = self._birth_scale if kind == "birth" else self._marriage_scale
                mult = self.cfg.birth_rate_multiplier if kind == "birth" else self.cfg.marriage_rate_multiplier
                return clamp01((raw / scale) * mult)

        # Case C: year only (single row or average)
        raw_vals = [to_float(r.get(key, 0)) for r in rows]
        raw = sum(raw_vals) / max(1, len(raw_vals))
        scale = self._birth_scale if kind == "birth" else self._marriage_scale
        mult = self.cfg.birth_rate_multiplier if kind == "birth" else self.cfg.marriage_rate_multiplier
        return clamp01((raw / scale) * mult)

    def _add_person(self, p: Person) -> int:
        self.people[p.pid] = p
        return p.pid

    def _get_person(self, pid: int) -> Person:
        return self.people[pid]

    def _alive_unpartnered(self, year: int) -> List[int]:
        out = []
        for pid, p in self.people.items():
            if p.is_alive(year) and p.partner_id is None:
                out.append(pid)
        return out

    def _can_partner(self, p: Person, year: int) -> bool:
        if not p.is_alive(year):
            return False
        if p.partner_id is not None:
            return False
        age = p.age_in(year)
        return self.cfg.min_partner_age <= age <= self.cfg.max_partner_age

    def _can_have_child_this_year(self, parent: Person, year: int) -> bool:
        if not parent.is_alive(year):
            return False
        age = parent.age_in(year)
        if not (self.cfg.min_parent_age_for_child <= age <= self.cfg.max_parent_age_for_child):
            return False
        if len(parent.children_ids) >= self.cfg.max_children_per_person:
            return False
        if parent.partner_id is None:
            return False
        partner = self.people.get(parent.partner_id)
        if not partner or not partner.is_alive(year):
            return False
        # enforce age window for BOTH parents (safer + matches typical intent)
        partner_age = partner.age_in(year)
        if not (self.cfg.min_parent_age_for_child <= partner_age <= self.cfg.max_parent_age_for_child):
            return False
        return True

    def generate(self) -> None:
        # Create two founders born in 1950, and pair them
        a = self.factory.create_person(self.cfg.founders_birth_year, gender="F")
        b = self.factory.create_person(self.cfg.founders_birth_year, gender="M")

        self._add_person(a)
        self._add_person(b)
        a.partner_id = b.pid
        b.partner_id = a.pid

        self.founder_ids = [a.pid, b.pid]

        # simulate year by year
        for year in range(self.cfg.start_year, self.cfg.end_year + 1):
            self._simulate_year(year)

    def _simulate_year(self, year: int) -> None:
        # 1) Partner formation
        # We'll attempt to partner unpartnered alive people with probability from marriage_rate by age.
        unpartnered = [pid for pid in self._alive_unpartnered(year) if self._can_partner(self.people[pid], year)]
        self.rng.shuffle(unpartnered)

        # simple greedy matching: try to match each person with someone else close in age
        used = set()
        for pid in unpartnered:
            if pid in used:
                continue
            p = self.people[pid]
            if not self._can_partner(p, year):
                continue
            age = p.age_in(year)
            marry_p = self._rate_for_age(year, age, "marriage")
            if self.rng.random() > marry_p:
                continue

            # find candidate partners within a reasonable age difference
            candidates = []
            for qid in unpartnered:
                if qid == pid or qid in used:
                    continue
                q = self.people[qid]
                if not self._can_partner(q, year):
                    continue
                # Prefer opposite gender if you want; but allow any if dataset doesn't encode it.
                # Here we *prefer* opposite but allow same if nothing else.
                age_diff = abs(q.age_in(year) - age)
                if age_diff <= 12:  # tuning knob
                    candidates.append((age_diff, qid))

            if not candidates:
                continue
            candidates.sort(key=lambda t: t[0])
            _, partner_id = candidates[0]
            partner = self.people[partner_id]

            # match them
            p.partner_id = partner_id
            partner.partner_id = pid
            used.add(pid)
            used.add(partner_id)

        # 2) Births
        # We iterate over potential parents (we'll use the "F" parent as the birth driver,
        # but enforce 25-45 for BOTH parents).
        females = [p for p in self.people.values() if p.gender == "F" and p.is_alive(year)]
        self.rng.shuffle(females)

        for mom in females:
            if not self._can_have_child_this_year(mom, year):
                continue

            mom_age = mom.age_in(year)
            birth_p = self._rate_for_age(year, mom_age, "birth")

            # This is an annual probability of having a child.
            if self.rng.random() > birth_p:
                continue

            dad = self.people[mom.partner_id]
            # last name rule: child gets one of the parents' last names (random)
            allowed_last_names = [mom.last_name, dad.last_name]

            child_gender = "F" if self.rng.random() < 0.5 else "M"
            child = self.factory.create_person(year, gender=child_gender, allowed_last_names=allowed_last_names)

            self._add_person(child)
            mom.children_ids.append(child.pid)
            dad.children_ids.append(child.pid)

    # ------------ Output helpers ------------

    def to_json(self) -> str:
        payload = {
            "config": self.cfg.__dict__,
            "founders": self.founder_ids,
            "people": [p.to_dict() for p in self.people.values()],
        }
        return json.dumps(payload, indent=2)

    def _format_person_label(self, p: Person) -> str:
        dy = f"–{p.death_year}" if p.death_year is not None else ""
        return f"{p.full_name} ({p.birth_year}{dy})"

    def print_tree(self) -> None:
        # Print both founders at top, and then show descendants of founder A to avoid duplicate subtrees.
        if not self.founder_ids:
            print("(no tree generated)")
            return

        a = self.people[self.founder_ids[0]]
        b = self.people[self.founder_ids[1]]

        print("=== FAMILY TREE (descendants of Founder A) ===")
        print(self._format_person_label(a))
        print(f"  partner: {self._format_person_label(b)}")
        self._print_descendants(a.pid, prefix="", visited=set())

    def _print_descendants(self, pid: int, prefix: str, visited: set[int]) -> None:
        # prevent cycles / duplicates
        if pid in visited:
            return
        visited.add(pid)

        p = self.people[pid]
        children = [self.people[cid] for cid in p.children_ids]
        # sort children by birth year for readability
        children.sort(key=lambda x: (x.birth_year, x.pid))

        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            branch = "└── " if is_last else "├── "
            print(prefix + branch + self._format_person_label(child))

            # show partner if exists
            if child.partner_id is not None:
                partner = self.people.get(child.partner_id)
                if partner:
                    sub_prefix = prefix + ("    " if is_last else "│   ")
                    print(sub_prefix + f"partner: {self._format_person_label(partner)}")

            sub_prefix = prefix + ("    " if is_last else "│   ")
            self._print_descendants(child.pid, sub_prefix, visited)

    def stats(self) -> Dict[str, Any]:
        total = len(self.people)
        births_by_year: Dict[int, int] = {}
        deaths_by_year: Dict[int, int] = {}
        marriages = 0

        for p in self.people.values():
            births_by_year[p.birth_year] = births_by_year.get(p.birth_year, 0) + 1
            if p.death_year is not None:
                deaths_by_year[p.death_year] = deaths_by_year.get(p.death_year, 0) + 1
            if p.partner_id is not None and p.pid < p.partner_id:
                marriages += 1

        return {
            "total_people": total,
            "total_partnerships": marriages,
            "births_by_year": dict(sorted(births_by_year.items())),
            "deaths_by_year": dict(sorted(deaths_by_year.items())),
        }