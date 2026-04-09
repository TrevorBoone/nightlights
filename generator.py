from suntime import Sun
from datetime import timedelta, datetime, date, time
from dateutil import tz
import random
from dataclasses import dataclass, asdict
import csv

from argparse import ArgumentParser

################
#              #
#  Constants   #
#              #
################


## normally most of these constants would be command line arguments but for ease of use
## they are just constants that the user of the program can change themselves.
START_DATE = date(2026, 4, 1)
END_DATE = date(2026, 4, 1)




############################
#                          #
#  Creating the schedule   #
#                          #
############################

def create_ordering(last_treatment):
    treatments = [0, 1, 2, 3]

    for i in range(4):
        j = random.randint(i, 3)
        swap(treatments, i, j)

    if treatments[0] != 0 and treatments[0] == last_treatment:
        swap(treatments, random.randint(1,3))

    return treatments

def treatment_sequence_generator():
    last_treatment = 0
    while True:
        ordering = create_ordering(last_treatment)
        for o in ordering:
            yield o


@dataclass
class Treatment:
    # 0 is no lights on
    light: int
    start: datetime
    end: datetime
    ## whether or not it had an issue or needed to be manually started.
    error: bool

    ## this makes it so it this class in a concise way for debugging.
    def __repr__(self) -> str: 
        return f"{self.light}, {self.start}, {self.end}"


######################
#                    #
#  Other Functions   #
#                    #
######################

'''
Swap the i-th and j-th elements in an array (n.b. array indexes start at 0 in python).
'''
def swap(array, i, j):
    if i == j:
        return
    array[i], array[j] = array[j], array[i]

'''
Write the treatments as a csv to the file specified.
'''
def write_treatment(treatment, filename = "logs/test.csv") -> None:
    with open(filename, "a") as f:
        writer = csv.writer(f)
        writer.writerow([
            treatment.light,
            treatment.start.isoformat(),
            treatment.end.isoformat(),
            treatment.error
            ])

'''
Reads the csv file and returns the contents of the file as list[Treatment]
'''
def read(filename = "logs/test.csv") -> list[Treatment]:
    treatments = []
    with open(filename) as f:
        r = csv.reader(f)
        for row in r:
            start = datetime.fromisoformat(row[1])
            end = datetime.fromisoformat(row[2])
            treatments.append(Treatment(int(row[0]), start, end))
    return treatments
            

###########################
#                         #
#  Running the program   #
#                         #
###########################

if __name__ == "__main__":
    TIME_OF_TREATMENT = timedelta(seconds = 10)
    TIME_BETWEEN_TREATMENTS = timedelta(seconds = 10)
    treatments = create_day(datetime.now() + timedelta(seconds=20), datetime.now() + timedelta(minutes = 1))
    print(treatments)
    write(treatments)
    treatments = read()
    print(treatments)
    