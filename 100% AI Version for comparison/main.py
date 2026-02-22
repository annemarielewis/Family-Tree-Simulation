from __future__ import annotations
import argparse
import random
from pathlib import Path

from config import SimConfig
from data_loader import load_all
from person_factory import PersonFactory
from family_tree import FamilyTree

def main():
    parser = argparse.ArgumentParser(description="Family Tree Simulator (1950-2040)")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory containing the CSV files")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible runs")
    parser.add_argument("--json-out", type=str, default="", help="Optional output JSON file path")
    parser.add_argument("--birth-mult", type=float, default=1.0, help="Multiplier to tune birth probability scale")
    parser.add_argument("--marriage-mult", type=float, default=1.0, help="Multiplier to tune marriage probability scale")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    data_dir = Path(args.data_dir)

    data = load_all(data_dir)

    cfg = SimConfig(
        birth_rate_multiplier=args.birth_mult,
        marriage_rate_multiplier=args.marriage_mult,
    )

    factory = PersonFactory(
        rng=rng,
        rank_to_prob=data.rank_to_prob,
        last_names=data.last_names,
        gender_name_prob=data.gender_name_prob,
        life_expectancy=data.life_expectancy,
    )

    tree = FamilyTree(
        cfg=cfg,
        rng=rng,
        factory=factory,
        birth_marriage_rows=data.birth_marriage,
    )

    tree.generate()
    tree.print_tree()

    s = tree.stats()
    print("\n=== STATS ===")
    print(f"Total people: {s['total_people']}")
    print(f"Total partnerships: {s['total_partnerships']}")
    # show a small summary window
    births = s["births_by_year"]
    if births:
        first_year = min(births.keys())
        last_year = max(births.keys())
        print(f"Birth years range: {first_year}..{last_year}")
        print("Births (sample):")
        for y in list(births.keys())[:10]:
            print(f"  {y}: {births[y]}")

    if args.json_out:
        Path(args.json_out).write_text(tree.to_json(), encoding="utf-8")
        print(f"\nWrote JSON to: {args.json_out}")

if __name__ == "__main__":
    main()