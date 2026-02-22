# main.py
from collections import Counter
from person_factory import PersonFactory
from family_tree import FamilyTree


def menu():
    print("\n=== Family Tree Menu ===")
    print("1) Total number of people")
    print("2) Total number of people by year born")
    print("3) Duplicate names")
    print("4) Quit")


def main():
    # Build / generate tree
    factory = PersonFactory()
    factory.read_files()          # <-- required in your current design
    tree = FamilyTree(factory)
    tree.generate_tree()

    print("\n✅ Family tree generated!")
    print("Total people:", len(tree.people))

    # User interaction loop
    while True:
        menu()
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            print("\nTotal number of people in the tree:", len(tree.people))

        elif choice == "2":
            # Count by birth year
            counts = Counter(p.year_born for p in tree.people)

            sub = input("Type a year (e.g. 1950) OR press Enter to show all: ").strip()
            if sub == "":
                for year in sorted(counts):
                    print(f"{year}: {counts[year]}")
            else:
                try:
                    year = int(sub)
                    print(f"People born in {year}: {counts.get(year, 0)}")
                except ValueError:
                    print("That wasn't a valid year.")

        elif choice == "3":
            # Duplicate full names
            full_names = [f"{p.first_name} {p.last_name}" for p in tree.people]
            name_counts = Counter(full_names)

            duplicates = {name: cnt for name, cnt in name_counts.items() if cnt > 1}

            if not duplicates:
                print("\nNo duplicate names found.")
            else:
                print("\nDuplicate names (name: count):")
                for name, cnt in sorted(duplicates.items(), key=lambda x: (-x[1], x[0])):
                    print(f"{name}: {cnt}")

        elif choice == "4":
            print("Bye! 👋")
            break

        else:
            print("Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()