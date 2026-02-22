from person_factory import PersonFactory
from family_tree import FamilyTree


def main():
    # Create factory
    factory = PersonFactory()

    # Create tree
    tree = FamilyTree(factory)

    # Generate tree
    tree.generate_tree()

    # Simple test output
    print("Family tree generated successfully!")
    print("Total number of people:", len(tree.people))

    # Optional: print first 10 people for sanity check
    print("\nFirst 10 people:")
    for person in tree.people[:10]:
        print(f"{person.first_name} {person.last_name}, born {person.year_born}")


if __name__ == "__main__":
    main()