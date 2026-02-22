# family_tree.py
from collections import deque
from person_factory import PersonFactory
import random

class FamilyTree:
    #argument (PersonFactory) passed in as parameter. 
    def __init__(self, factory: PersonFactory):
        # self.factory=attribute of this class and it's being set to equal the argument factory(aka PersonFactory) being passed in
        self.factory = factory
        #more attributes, note deriving from passed in values:
        self.people = []                 # list of everyone in the tree
        self.possible_last_names = []     # last names the descendants must use

    def generate_tree(self):
        # initialize founders (born 1950)

        # 1) Create the two founders born in 1950
        # A: founder A
        founder_a = self.factory.create_person(1950)

        # B: keep generating until differs (if we are making a genetic family tree like in organismal-bio. --> for reproduction tracing or familial relations?? Unclear! Because genetics is more code, will assume it's representing a genetic fam-tree flow-like in undergrad.)
        founder_b = self.factory.create_person(1950)
        while founder_b.gender == founder_a.gender:
            founder_b = self.factory.create_person(1950)

        founder_a.set_partner(founder_b) # ---> # This line links the two founders as partners.
# This ensures that children are correctly associated with both parents
# and allows the ASCII tree to visually represent a proper parental pair.
#
# Side Effect:
# Because both parents reference the same children, traversing the tree
# starting from each founder can cause the same descendants to appear twice
# in printed output. This does NOT mean the children are actually duplicated
# Person objects — it is a traversal/printing issue caused by shared references.
#
# It can also inflate duplicate-name counts if the same subtree is printed
# from both roots without tracking visited nodes.
#
# Therefore:
# - This partner link is necessary for correct family modeling and visualization.
# - Duplicate printing/counting must be handled separately (e.g., using a
#   visited set when printing or de-duplicating by object id when counting).
#discovered via trial and error of count seeming off in option 3 of main (with this line on) 
# or tree being off (option 7) via not representing both parents (with this line deleted). Realized 
# have to leave this line and account for not counting duplicates in main.py :)

        # 2) adding both founders to the master list
        self.people.append(founder_a)
        self.people.append(founder_b)

        # 3) Saving last names (for descendant rule)
        self.possible_last_names = [founder_a.last_name, founder_b.last_name]

        # 4) Put them in a queue to process later (partners/children in future steps)
        parent_queue = deque()
        parent_queue.append(founder_a)
        parent_queue.append(founder_b)

    # 5) Process the queue: create partners + children
        while parent_queue:
            person = parent_queue.popleft() # retrieves first person object from que and stores as person

            decade = (person.year_born // 10) * 10

            # -------------------------
            # Step 2: create a partner (maybe)
            # -------------------------
            marriage_rate = self.factory.marriage_rate_by_decade.get(decade, 0)

            if person.partner is None:
                roll = random.random()  # number between 0.0 and 1.0
                if roll < marriage_rate:
                    partner_year = random.randint(person.year_born - 10, person.year_born + 10)

                    # create partner as a "non-descendant"/opposite sex --> (if we are making a genetic family tree like in organismal-bio. --> for reproduction tracing or familial relations?? Unclear! Because genetics is more code, will assume it's representing a genetic fam-tree flow, like in undergrad)
                    partner = self.factory.create_person(partner_year)
                    while partner.gender == person.gender:
                        partner = self.factory.create_person(partner_year)

                    # link them both ways
                    person.set_partner(partner)

                    # add partner to master list + queue (partner can also have children later)
                    self.people.append(partner)
                    parent_queue.append(partner)

            # If partnered, only one of the two should generate the kids, to avoid double generation in partnerships
            if person.partner is not None:
                # skip if partner will handle it
                if id(person) > id(person.partner):
                    continue

            # -------------------------
            # Step 3: decide number of children
            # -------------------------
            birth_rate = self.factory.birth_rate_by_decade.get(decade, 0)

#min and max # of kids by a range:
            import math
            min_kids = max(0, math.floor(birth_rate - 1.5))
            max_kids = max(0, math.ceil(birth_rate + 1.5))

            if max_kids == 0:
                continue

            num_children = random.randint(min_kids, max_kids)

            if person.partner is None:
                num_children = max(0, num_children - 1)

            if num_children == 0:
                continue

            # -------------------------
            # Step 4: generate children with birth years in range
            # -------------------------
            start_year = person.year_born + 25
            end_year = person.year_born + 45

            # evenly spaced years (simple approach)
            if num_children == 1:
                child_years = [start_year]
            else:
                step = (end_year - start_year) / (num_children - 1)
                child_years = []
                for i in range(num_children):
                    y = int(round(start_year + step * i))
                    child_years.append(y)

#will stop generating children when we hit within 25 years of year 2120

            for child_year in child_years:
                if child_year > 2120:
                    continue

                parent_last_names = [person.last_name]
                if person.partner is not None:
                    parent_last_names.append(person.partner.last_name)
                    
                child = self.factory.create_person(child_year, allowed_last_names=parent_last_names)
                # enforce descendant last-name rule here:
                #this will cause a child to get one of their parents last names (m or f).

                # attach child to this person
                person.add_child(child)

                # attach child to this person's partner too (both their parents)
                if person.partner is not None:
                    person.partner.add_child(child)

                    # add to master list + queue so this child can grow up and have kids later
                self.people.append(child)
                parent_queue.append(child)
        
