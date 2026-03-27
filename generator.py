from suntime import Sun
from datetime import timedelta, datetime, date, time
from dateutil import tz
import random
from dataclasses import dataclass, asdict
import csv

TIME_OF_TREATMENT = timedelta(minutes = 10)
TIME_BETWEEN_TREATMENTS = timedelta(minutes = 10)
SUN_DELAY = timedelta(minutes = 30)
TIMEZONE = tz.gettz("US/Central")


OFF = 0
AMBER = 1
OTHER_COLOR = 2
COLOR_3 = 3

LAT = 40.42128973283434
LONG = -86.90005225247548

SUN = Sun(LAT, LONG)

def create_schedule(first_day: date, last_day:date):
    current = first_day
    treatments = []
    while current <= last_day:
        curr_datetime = datetime.combine(current, time(hour=12, tzinfo=TIMEZONE))
        start = SUN.get_sunset_time(curr_datetime, time_zone = TIMEZONE) + SUN_DELAY
        end = SUN.get_sunrise_time(curr_datetime, time_zone = TIMEZONE) - SUN_DELAY
        start = start.replace(second = 0, microsecond = 0)
        end = end.replace(second = 0, microsecond = 0)
        new_treatments = create_day(start, end)
        print("\n".join([t.debug_str() for t in new_treatments]))
        treatments.extend(new_treatments)
        current = current + timedelta(days = 1)
    
    return treatments


@dataclass
class Treatment:
    # 0 is off
    light: int
    start: datetime
    end: datetime

    def __repr__(self) -> str: 
        return f"{self.light}, {self.start}, {self.end}"

def create_day(start: datetime, end:datetime):
    current = start
    last_treatment = 0
    treatments = []
    while current < end:
        ordering = create_ordering(last_treatment)
        for light_index in ordering:
            treatments.append(Treatment(light=light_index, start = current, end = current + TIME_OF_TREATMENT))
            current = current + TIME_OF_TREATMENT + TIME_BETWEEN_TREATMENTS
    return treatments

def swap(array, i, j):
    if i == j:
        return
    array[i], array[j] = array[j], array[i]

def create_ordering(last_treatment):
    treatments = [0, 1, 2, 3]

    for i in range(4):
        j = random.randint(i, 3)
        swap(treatments, i, j)

    if treatments[0] != 0 and treatments[0] == last_treatment:
        swap(treatments, random.randint(1,3))

    return treatments
    
def write(treatments, filename = "test.csv"):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        for t in treatments:
            writer.writerow([t.light, t.start.isoformat(), t.end.isoformat()])

def read(filename = "test.csv"):
    treatments = []
    with open(filename) as f:
        r = csv.reader(f)
        for row in r:
            start = datetime.fromisoformat(row[1])
            end = datetime.fromisoformat(row[2])
            treatments.append(Treatment(int(row[0]), start, end))
    return treatments
            

if __name__ == "__main__":
    TIME_OF_TREATMENT = timedelta(seconds = 10)
    TIME_BETWEEN_TREATMENTS = timedelta(seconds = 10)
    treatments = create_day(datetime.now() + timedelta(seconds=20), datetime.now() + timedelta(minutes = 1))
    print(treatments)
    write(treatments)
    treatments = read()
    print(treatments)
    