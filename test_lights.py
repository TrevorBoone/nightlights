from lights import Lighter
from time import sleep

if __name__ == "__main__":
    l = Lighter()

    l.lights(0)
    sleep(5)
    l.lights(1)
    sleep(5)
    l.lights(2)
    sleep(5)
    l.lights(3)
    sleep(5)
    l.lights(0)