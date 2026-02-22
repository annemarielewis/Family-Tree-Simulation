
#PERSON FACTORY CLASS: its job is, “read external data and use it to create people.”

#loads the CSVs, stores the lookup tables, then uses to generate attributes, imports pythons csv model
import os
import csv
import random
from person import Person

class PersonFactory:
    def __init__(self): #CONSTRUCTOR SYNTAX
        #(self means “this specific instance of the class”)

        self.next_id = 1   # ID counter

        self.life_expectancy_by_decade = {} 
        self.birth_rate_by_decade = {}
        self.marriage_rate_by_decade = {}
        self.last_name_ranks = []
        self.rank_to_probability = {}

        # weighted sampling lists/dicts
        # first names nested dictionary:
        # { decade: { gender: { name: frequency } } }
        self.first_names = {} 
        self.last_names = []
        self.last_name_weights = []

        self.read_files()


#EXTRACT INFO+DEMOGRAPHIC STATS FROM CSV FILES:

    def read_files(self): #FILE READER | self =“the object that is calling this method”
        # 1) life_expectancy.csv  -> dict -> life_expectancy
 # -------------------------------
 #life expectancy file
        # Open the file safely. "with" ensures the file is automatically closed after this block.
        with open("life_expectancy.csv") as f: # file store as f
    
            # skip the first line of the file (the header row: "decade,life_expectancy")
            next(f)
    
            # loop through each remaining line in the file (each data row)
            for line in f:

                # remove whitespace and newline characters from the line
                clean_line = line.strip()

                # split the cleaned line into parts wherever there is a comma
                parts = clean_line.split(",")

                # get the first value (decade) from the list
                decade_str = parts[0]

                # get the second value (life expectancy) from the list
                life_str = parts[1]

                # convert the decade string to an integer
                decade = int(decade_str)
                # convert the life expectancy string to a float
                life_exp = float(life_str)
                # store this pair inside the dictionary: (key = decade (integer), value = life expectancy (float))
                self.life_expectancy_by_decade[decade] = life_exp

 # -------------------------------
    # first_names.csv

        # base_dir = os.path.dirname(__file__)
        # csv_path = os.path.join(base_dir, "first_names.csv")

        # if not os.path.exists(csv_path):
        #  raise FileNotFoundError(f"Could not find first_names.csv at: {csv_path}")

        # with open(csv_path, encoding="utf-8") as f:
        #     next(f)

        #     for line in f:
        #         clean_line = line.strip()
        #         parts = clean_line.split(",")

        #         decade_str = parts[0]      # decade as string (with s on end)
        #         gender = parts[1].strip().lower()          # sex 
        #         name = parts[2]            # first name
        #         frequency_str = parts[3]   # frequencey as string

        #         decade = int(decade_str.replace("s", ""))
        #         frequency = float(frequency_str)

        #         # If decade not yet in dictionary, create it
        #         if decade not in self.first_names:
        #             self.first_names[decade] = {}

        #         # If gender not yet in that decade, create it
        #         if gender not in self.first_names[decade]:
        #             self.first_names[decade][gender] = {}

        #         # store name and frequency
        #         self.first_names[decade][gender][name] = frequency

        #         # print("Loaded decades:", sorted(self.first_names.keys())[:5], "...", sorted(self.first_names.keys())[-5:])
        #         # print("Min decade:", min(self.first_names.keys()))
        #         # print("Max decade:", max(self.first_names.keys()))
        #         # print("Count decades:", len(self.first_names))

        # first_names.csv
        base_dir = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, "first_names.csv")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Could not find first_names.csv at: {csv_path}")

        self.first_names = {}

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Debug: show the column names it detected
            print("first_names.csv columns:", reader.fieldnames)

            for row in reader:
                # Adjust these keys to match your real header names:
                decade_str = row["decade"].strip()      # e.g. "1950s"
                gender = row["gender"].strip().lower()  # "male"/"female"
                name = row["name"].strip()
                frequency = float(row["frequency"])

                decade = int(decade_str.replace("s", ""))

                self.first_names.setdefault(decade, {}).setdefault(gender, {})[name] = frequency

        print("Loaded decades:", sorted(self.first_names.keys())[:5], "...", sorted(self.first_names.keys())[-5:])

#data will be stored like: 
#self.first_names = {
    #decade: {
        #"male": {
            #"name": frequency,
       # },
        #"female": {
          #"name": frequency,
        #}
    #}
#}

# -------------------------------
# birth_and_marriage_rates.csv (using csv reader now because need to speed up my process!)
# -------------------------------
        with open("birth_and_marriage_rates.csv") as f:
            reader = csv.reader(f)

            next(reader)  # skip header row

            for row in reader:
                decade_str = row[0]
                birth_str = row[1]
                marriage_str = row[2]

                decade = int(decade_str.replace("s", ""))

                self.birth_rate_by_decade[decade] = float(birth_str)
                self.marriage_rate_by_decade[decade] = float(marriage_str)


        #rank to probability file:
        with open("rank_to_probability.csv") as f:
            reader = csv.reader(f)
            row = next(reader)          # first row is the list of probs
            probs = []
            for x in row:
                number = float(x)
                probs.append(number)

            rank = 1
            for prob in probs:
                self.rank_to_probability[rank] = prob
                rank = rank + 1
            
        # -------------------------------
        # last_names.csv
        # -------------------------------
        with open("last_names.csv") as f:
            reader = csv.reader(f)
            next(reader)  # skip header

            for row in reader:
                decade_str = row[0]          
                rank = int(row[1])          
                last_name = row[2]

                # convert rank to probability weight
                weight = self.rank_to_probability[rank]  #dictionary made in rank to prb logic above ^

                self.last_names.append(last_name) 
                self.last_name_weights.append(weight)
                            
#_____________________________
#Creating a person Method
#_____________________________

    def create_person(self, year_born, allowed_last_names=None):
        # decide gender randomly
        gender = random.choice(["male", "female"])

        # get decade from year
        decade = (year_born // 10) * 10


        # choose random first name using nested dictionary
        name_dict = self.first_names[decade][gender]
        names = list(name_dict.keys())
        weights = list(name_dict.values())
        first_name = random.choices(names, weights=weights, k=1)[0]

        # choose last name using weighted sampling (first generation) OR one of two of parent's last names
        if allowed_last_names is None:
            last_name = random.choices(self.last_names, weights=self.last_name_weights,k=1)[0]
        else:
        # descendant → choose from parents' surnames
            last_name = random.choice(allowed_last_names)
       
        # 5️compute year died
        base_life = self.life_expectancy_by_decade[decade]

        life_length = random.uniform(base_life - 10, base_life + 10)

        year_died = int(year_born + life_length)

        person_id=self.next_id

        self.next_id += 1
        
        # 6️return a Person object
        return Person(year_born, year_died, first_name, last_name, gender, person_id)