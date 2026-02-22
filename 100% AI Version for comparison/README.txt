
I was curious how I'd compare to an AI programming from the ground up. 
The program does not work due to it not understanding how the CSVs are structured despite being fed them
(or at least that's the first error that stopped it from running). However, I do like how
it separated csv file reading and data storing from person_factory into its own class. When was coding, 
I quickly wished I'd developed with more separation of factory--data.

Config → Data Loader → Samplers → PersonFactory → FamilyTree

Each one has a single job, and the later ones depend on the earlier ones.

config.py — “the rules + knobs”

What it contains: constants/settings for the simulation (years, min/max parent age for children, max children, multipliers, etc.)

Who uses it:

family_tree.py reads config values to decide:

what years to simulate

whether someone is allowed to have kids (25–45 rule)

limits like max children

tuning multipliers for rates

Why separate: You can tune behavior without touching the simulation logic.

data_loader.py — “read the CSVs and return clean data”

What it does:

Opens the CSV files

Parses them into Python structures (lists of dicts, lists of strings)

Detects column names (even if your columns vary)

Returns a “bundle” of datasets (rank probs, names, life expectancy, birth/marriage rates)

Who uses it:

main.py calls load_all(data_dir)

The returned data gets passed into:

PersonFactory (names + life expectancy)

FamilyTree (birth/marriage rates)

Why separate: Keeps file I/O and parsing out of the simulation logic.

samplers.py — “math helpers for probability + picking things”

What it contains:

weighted_choice(...) → pick an item based on weights/probabilities

clamp01(x) → keep probabilities in [0, 1]

infer_rate_scale(...) → detect if a “rate” is per-1000, per-100, or already 0–1

pick_column(...) → find the right column name even if the CSV calls it something else

lookup_best_match(...) (optional) → find nearest year if exact year missing

Who uses it:

data_loader.py uses pick_column to interpret your CSV columns

person_factory.py uses weighted_choice to pick names

family_tree.py uses clamp01 and infer_rate_scale to turn rate values into probabilities

Why separate: Probability logic is reusable and keeps other files cleaner.

person_factory.py — “create one person realistically”

What it does:

Takes the loaded datasets (from data_loader.py)

Uses samplers.py to sample:

gender (simple baseline unless you add data)

first name (from gender/name probability CSV)

last name (from last_names.csv)

death year (from life expectancy distribution)

Assigns a stable unique pid (this is the ID you want for deduping)

Who uses it:

family_tree.py calls factory.create_person(...) whenever it needs:

the founders

a spouse/partner (if you generate one)

a child

Why separate: FamilyTree shouldn’t care how names/death years are chosen—only that it gets a valid Person.



Summary: how it’s structured & why *written by AI

1. data_loader.py

Loads CSVs and normalizes them into clean in-memory tables (lists/dicts).
Why: keeps file parsing separate from simulation logic, and makes it easy to swap/extend datasets.

2. samplers.py

Implements reusable sampling utilities:

weighted choice

fallback column detection

probability lookups by year/age
Why: simulation code stays readable, and probability logic is centralized.

^both above are deisgn improvements for sure!! --Annemarie

3. person.py

Defines the Person dataclass (id, name, gender, birth/death year, partner, children).
Why: clean data model; easy to export/print.

4. person_factory.py

Creates people using:

name distributions (rank/prob + gender/name probs)

last name list

assigns a death year by sampling life expectancy
Why: one place for “how a person is generated.”

5. family_tree.py

Runs the simulation year-by-year:

partner formation (marriage/partner rates)

births (birth rates) only if parent age 25–45

deaths (using assigned death year)
Why: separation of “simulation engine” from data and person creation.

6. main.py

CLI entry:

loads datasets from data/

runs simulation

prints tree + stats

optional JSON dump
Why: one clean command to run it.