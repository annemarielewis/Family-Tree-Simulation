~Family Tree Generator~

Overview: This program generates a simulated multi-generation family tree beginning in 1950 using 
statistically representative demographic data. The model incorporates: First name frequencies by 
decade and gender, Last name probability distributions, Marriage rates by decade, Birth rates by 
decade, and Life expectancy by decade. All demographic data is read from CSV files and processed 
at runtime. Each generated person is probabilistically constructed based on historical trends, 
allowing the tree to grow across generations while remaining statistically grounded.

This project was developed as part of an active learning process. You may notice extensive comments 
and annotations throughout the code. These reflect my 
learning thought process and experimentation during development and are not representative 
of how I would comment code in a production or professional setting.
_____________________

MAIN.PY & PROGRAM FUNCTIONALITY-->
_____________________

Main.py

Provides a simple interactive interface after generating the tree.

=== Family Tree Menu ===
1. Total number of people
2. Total number of people by year born
3. Duplicate names
4. Who lived the longest and how old
5. Average Lifespan of Entire Tree
6. Largest Family (Most Children a Couple Had)
7. Print entire family tree (ASCII)
8. Quit

Option Details:

1. Total number of people
Displays the total number of unique individuals in the family tree.

2. Total number of people by year born

Displays the number of people born in each year.

The user may optionally enter a specific year to view only that year’s count.

3. Duplicate names
Displays any duplicate full names (first + last) found in the tree and how many times each appears.

4. Who lived the longest and how old
Identifies the individual with the greatest lifespan and displays their age at death.

5. Average Lifespan of Entire Tree
Calculates and displays the average lifespan across all individuals in the tree.

6. Largest Family (Most Children a Couple Had)
Displays the individual who had the most children and the total number of children they had.

7. Print Entire Family Tree (ASCII Format)
Prints the complete family tree in a structured ASCII format in the console.

Note:
Children will display twice (once under each parent) for ASCII readability in the console.
However, both entries refer to the same individual, tracked internally using a unique object ID.

8. Quit
Exits the program.
_________________________________

CLASSES AND STRUCTURE -->

_________________________________

person.py = person class: 
Defines the Person class, representing an individual in the family tree.

#constructor
    def __init__(self, year_born, year_died, first_name, last_name, gender)

| Attribute    | Type   | Description                        |
| ------------ | ------ | ---------------------------------- |
| `year_born`  | int    | Year of birth                      |
| `year_died`  | int    | Year of death                      |
| `first_name` | string | First name                         |
| `last_name`  | string | Last name                          |
| `gender`     | string | Gender (`"male"` / `"female"`)     |
| `partner`    | Person | Partner reference (default `None`) |
| `children`   | list   | List of child `Person` objects     |

methods:
full_name() → Returns "First Last"

add_child(child) → Adds a child to the person

set_partner(partner) → Sets bidirectional partner relationship

_____________________

person_factory.py class 
The PersonFactory class reads external demographic data from CSV files and 
uses that data to construct Person objects when called in the Person class 
for construction.

It acts as a data-driven generator for individuals.

#constructor: 
def __init__(self)

attributes:
| Attribute                 | Type             | Purpose                    |
| ------------------------- | ---------------- | -------------------------- |
| life_expectancy_by_decade | dict[int, float] | life expectancy lookup     |
| birth_rate_by_decade      | dict[int, float] | birth rate lookup          |
| marriage_rate_by_decade   | dict[int, float] | marriage rate lookup       |
| last_name_ranks           | list[int]        | rank storage (optional)    |
| rank_to_probability       | dict[int, float] | rank → probability mapping |
| first_names               | nested dict      | name frequency lookup      |
| last_names                | list[str]        | surname options            |
| last_name_weights         | list[float]      | surname probabilities      |
| sex_gender                | string           | to keep track of for reproduction, assuming this is representing a genetic family tree?|

methods:
create_person(year_born, allowed_last_names=None)
^This method:
Determines gender randomly, Selects a first name based on decade and gender frequency,
Selects a last name (either weighted random or inherited from parents),
Calculates lifespan using decade life expectancy, Returns a fully constructed Person object

output: return Person(year_born, year_died, first_name, last_name) <--passes into Person class to construct a person
^ this data are the attributes the Person class needs to be passed into its constructor in order to make the person! Woohoo!
_________________________________

family_tree.py

The FamilyTree class constructs and manages the generational structure, constructing the family tree by taking in PersonFactory instance as the argument-object

constructor: def __init__(self, factory: PersonFactory):

attributes:

| Attribute Name             | Type            | Description                                                                                                                                   |
| -------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `self.factory`             | `PersonFactory` | The factory object used to create `Person` instances and access demographic data (names, birth rates, marriage rates, life expectancy, etc.). |
| `self.people`              | `list[Person]`  | A master list containing every `Person` object generated in the family tree.                                                                  |
| `self.possible_last_names` | `list[str]`     | Stores last names of parents as possible last names                                                        |

methods: generateTree()
^ This method:
Creates two founders (born 1950), Iteratively generates partners and children,
Uses demographic probabilities to simulate realistic growth, Builds the family 
tree generation-by-generation

utilizes methods from Person class: Person.set_partner(), Person.add_child()

_________________________________

factory_test.py -- used during development to test functionality of person_factory.py:
CSV loading
Name selection
Life expectancy calculation
Person creation logic

_________________________________

family_tree_test.py -- used during development to test functionality of family_tree.py:
Tree generation logic
Partner creation
Child generation
Structural integrity of the tree
_________________________________