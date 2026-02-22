from person_factory import PersonFactory

factory = PersonFactory()
factory.read_files()  


# TESTS for file reading

# check how many decades were loaded for life expectancy
print("Number of decades loaded for life expectancy:",
      len(factory.life_expectancy_by_decade))

# check life expectancy value for 1950
print("Life expectancy for 1950:",
      factory.life_expectancy_by_decade.get(1950))

# check birth rate for 1950
print("Birth rate for 1950:",
      factory.birth_rate_by_decade.get(1950))

# check marriage rate for 1950
print("Marriage rate for 1950:",
      factory.marriage_rate_by_decade.get(1950))


# check first few decades loaded in first_names
print("First three decades loaded in first_names:",
      list(factory.first_names.keys())[:3])

# check available genders stored for 1950
print("Available genders stored for 1950:",
      list(factory.first_names[1950].keys()))

# check first three last names loaded
print("First three last names loaded:",
      factory.last_names[:3])

# check first three last-name probabilities
print("First three last-name probability weights:",
      factory.last_name_weights[:3])

# check total of last-name probabilities
print("Sum of all last-name probability weights:",
      sum(factory.last_name_weights))


# TEST for creating a person
def main():
    p = factory.create_person(1950)
    print("Created person:", p.full_name())
    print("Born:", p.year_born)
    print("Died:", p.year_died)

#Only run main() if this if this file is being executed directly:
if __name__ == "__main__":
    main()