# main.py
from collections import Counter
from person_factory import PersonFactory
from family_tree import FamilyTree


def menu():
    print("\n=== Family Tree Menu ===")
    print("1) Total number of people")
    print("2) Total number of people by year born")
    print("3) Duplicate names")
    print("4) Who lived the longest and how old")
    print("5) Average Lifespan of Entire Tree")
    print("6) Largest Family (Most Children a Couple Had")
    print("7) Print entire family tree (ASCII). *Note: Children will display twice (once per parent) \n *for ACSII readability in console, but they’re the same individual (unique ID).")
    print("8) Quit")


#______________________
#ascii fucntion to get tree printed out in fam tree ascii structure in console: (copy and pasted this ascii formatting code--incoorporated for desires and options outside of assignment scope)
def print_tree_graph(person, prefix=""):
    """
    Prints a person and their descendants in a tree-graph style.
    """
    print(f"{prefix}{person.full_name()} ({person.year_born})")

    children = person.children
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)

        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        print(f"{prefix}{connector}", end="")
        # print child on the same line
        print(f"{child.full_name()} ({child.year_born})")

        # now print that child's children with updated prefix
        print_tree_graph_children(child, child_prefix)
        
def print_tree_graph_children(person, prefix):
    """
    Helper that prints only the descendants (so we don't repeat the person's line).
    """
    children = person.children
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)

        connector = "└── " if is_last else "├── "
        next_prefix = prefix + ("    " if is_last else "│   ")

        print(f"{prefix}{connector}{child.full_name()} ({child.year_born})")
        print_tree_graph_children(child, next_prefix)

#___________________________
# MAIN()

def main():
    # build / generate tree
    factory = PersonFactory()
    #factory.read_files()          # <-- oops, not required... in PersonFactory already
    tree = FamilyTree(factory)
    tree.generate_tree()

    if len(tree.people) > 0:
        print("Tree generated")

    # User interaction loop

    running = True

    while running == True:
        menu()
        choice = input("Choose (1-8): ")


#unique people logic using IDs... necessary due to line 27 OF FAMILY_TREE.PY
        unique_people = {}
        for p in tree.people:
            unique_people[p.person_id] = p
        unique_people_list = list(unique_people.values()) #person objects stores in list
        #print("debug: " + str(unique_people.values()))

#total num of people:
        if choice == "1":
            print("\nTotal number of individuals in the family tree:", len(unique_people_list))

# Count of how many people from each birth year:
        elif choice == "2":
            # empty list to store birth years
            birth_years = []
            
            for person in unique_people_list:
                birth_years.append(person.year_born)

            # Count how many times each year appears
            counts = Counter(birth_years) #makes dict or years and # of counts

            sub = input("Type a year (e.g. 1950) OR press Enter to show all: ").strip()

            #if they push enter:
            if sub == "":
                for year in sorted(counts):
                    print(f"{year}: {counts[year]}")

            #if they eneter a year value
            else:
                try:
                    year = int(sub)
                    print(f"People born in {year}: {counts.get(year, 0)}")

                except ValueError:
                    print("Oops! That wasn't a valid year.")

        elif choice == "3":
            # Find duplicate (full) names:
            full_names = [f"{p.first_name} {p.last_name}" for p in unique_people_list]
            name_counts = Counter(full_names)

            duplicates = {}

            for name, count in name_counts.items():
                if count > 1:
                    duplicates[name] = count

            if not duplicates:
                print("\nNo duplicate names found.")
            else:
                print("\nDuplicate names (name: count):")
                #Convert dictionary to a list of items
                duplicate_list = list(duplicates.items())
                #sort list alphabetically by name first
                duplicate_list.sort(key=lambda item: item[0])
                #Sort by count (largest first)
                duplicate_list.sort(key=lambda item: item[1], reverse=True)
                #print
                for item in duplicate_list:
                    name = item[0]
                    count = item[1] 
                    print(name + ": " + str(count))

        elif choice == "4":
            #person who lived the long
            longest_lived = max(unique_people_list, key=lambda p: p.year_died - p.year_born)
            age_at_death = longest_lived.year_died - longest_lived.year_born
            print("person who lived the longest: " + str(longest_lived.full_name()) + "who died at age " + str(age_at_death))

        elif choice == "5":
        #average lifespan
            total_years = 0
            for person in unique_people_list:
                total_years = total_years + (person.year_died - person.year_born)

            average = total_years / len(unique_people_list)
            print("Average lifespan:" + str(round(average, 2)))

        elif choice == "6":
            #whoever had the most children and how many children
            most_children = max(unique_people_list, key=lambda p: len(p.children))
            print(most_children.full_name(), "had", len(most_children.children), "children")

        elif choice == "7":
            founders = [p for p in unique_people_list if p.year_born == 1950]
            print("\n=== FAMILY TREE ===")
            for founder in founders:
                print_tree_graph(founder, "")

        else:
            print("Goodbye!")
            running = False

if __name__ == "__main__":
    main()