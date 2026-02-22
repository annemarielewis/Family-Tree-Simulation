#PERSON CLASS: data about each person

#Represents one human.
#Should NOT: open files, read CSVs, know about datasets

#attributes: 
# year_born
# year_died
#first_name
#last_name
#partner
# children (default empty list)

# helper methods:
#full_name() → "First Last"
#add_child(child)
#set_partner(partner)

#learning python and DS at same time, so commented extensively. In bridge.

class Person:

#constructor
    def __init__(self, year_born, year_died, first_name, last_name, gender):
        self.year_born = year_born
        self.year_died = year_died
        self.first_name = first_name
        self.last_name = last_name
        self.partner = None  #default       
        self.children = []    #empty rn
        self.gender=gender

#methods
    #name:
    def full_name(self):
        return f"{self.first_name} {self.last_name}" #returns full name to wherever called full_name function
    
   # attaching a child (another person object) to this Person instance
    def add_child(self, child):
        self.children.append(child)  # append() adds the child object to this person's children list

    def set_partner(self, partner):
        #setting self's partner to partner
        self.partner = partner
        #setting partner's partner to self
        partner.partner = self       