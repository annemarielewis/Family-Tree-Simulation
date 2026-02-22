from dataclasses import dataclass

@dataclass(frozen=True)
class SimConfig:
    start_year: int = 1950
    end_year: int = 2040

    # Founders
    founders_birth_year: int = 1950

    # Childbearing constraint (REQUIRED by you)
    min_parent_age_for_child: int = 25
    max_parent_age_for_child: int = 45

    # Partnering
    min_partner_age: int = 18
    max_partner_age: int = 80

    # Practical controls to avoid runaway population if birth rates are high
    max_children_per_person: int = 8

    # If your marriage rates are "annual probability of marrying",
    # this multiplier can help tune if the dataset is per-1000, per-100, etc.
    # The loader tries to infer scale, but this is a final knob.
    marriage_rate_multiplier: float = 1.0

    # Same knob for birth rates if needed.
    birth_rate_multiplier: float = 1.0