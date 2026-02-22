This program generates a random family tree from the year 1950 with statistically representative 
data on first/last names, marriage rates, birthrate, and lifespan.

*Note: There are many comments/annotations in my code because this was a process of learning.
notes show my learning thought process and are not a reflection of the amount I comment professioanlly.
_____________________

person.py is the person class: creates a person

#constructor
    def __init__(self, year_born, year_died, first_name, last_name, gender)

^attributes: 
year_born (int)
year_died (int)
first_name (string)
last_name (string)
partner (object)
children (default empty list, for object(s) to go into upon construction)

methods:
full_name() → "First Last"
add_child(child)
set_partner(partner)

_____________________

person_factory.py class reads external data/stats from CSV files and and uses it to create people
by passing the data into the Person class for construction.

#constructor: 
def __init__(self):

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
create_person()

output: return Person(year_born, year_died, first_name, last_name) <--passes into Person class to construct a person
^ this data are the attributes the Person class needs to be passed into its constructor in order to make the person! Woohoo!
_________________________________

family_tree.py

purpose is to construct the family tree taking in PersonFactpry as an object

constructor: def __init__(self, factory: PersonFactory):

attributes:

| Attribute Name             | Type            | Description                                                                                                                                   |
| -------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `self.factory`             | `PersonFactory` | The factory object used to create `Person` instances and access demographic data (names, birth rates, marriage rates, life expectancy, etc.). |
| `self.people`              | `list[Person]`  | A master list containing every `Person` object generated in the family tree.                                                                  |
| `self.possible_last_names` | `list[str]`     | Stores last names of parents as possible last names                                                        |

methods: generateTree()

utilizes methods from person class: set_partner(), add_child()
_________________________________

Main.py




_________________________________

factory_test.py -- used to test functionality of person_factory.py while constructing

_________________________________

family_tree_test.py -- used to test functionality of family_tree.py while constructing

_________________________________