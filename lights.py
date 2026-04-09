import asyncio
from kasa import Discover
from suntime import Sun
from datetime import timedelta, datetime, date, time
from dateutil import tz
from time import sleep
from generator import Treatment, treatment_sequence_generator, write_treatment
import logging
import signal
import sys
import requests

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/info.log"),
        logging.StreamHandler(sys.stdout),
    ]
)

SLACK_URL = "INSERT URL HERE"

TIME_OF_TREATMENT = timedelta(seconds = 10)
TIME_BETWEEN_TREATMENTS = timedelta(seconds = 5)
SUN_DELAY = timedelta(minutes = 30)
TIMEZONE = tz.gettz("US/Central")

# Italy, TX
LAT = 32.184051
LONG = -96.887440

SUN = Sun(LAT, LONG)

class Lighter:
    def __init__(self):
        #self.plugs = asyncio.run(dicsover_plugs())
        self.plugs = [1, 2, 3]
        signal.signal(signal.SIGINT, self.interrupt)
        self.current = None
        self.interrupted = False

    def lights(self, light: int) -> bool:
        attempt = 0
        while True:
            try:
                for i, p in enumerate(self.plugs):                                  
                    if light - 1 == i:
                        print(f"on {i+1}")
                        #asyncio.run(p.turn_on())
                    else:
                        print(f"off {i+1}")
                        #asyncio.run(p.turn_off())
            except:
                self.sleep_until(time.now() + timedelta(seconds=10))
                if attempt == 0:
                    logging.exception("Failed to turn off or on lights.")
                    requests.post(SLACK_URL, json={'text': f"Failed to turn on or off light! Retrying..."})
                else:
                    logging.debug("Failed to turn off lights.")
            else:
                if light == 0:
                    logging.info("Turned off all lights")
                else:
                    logging.info(f"Turned on light {light}")
                if attempt != 0:
                    requests.post(SLACK_URL, json={'text': "Recovered"})
                return attempt != 0 or self.interrupted
            
            if self.interrupted:
                return True

    def run_treatments(self, start: datetime, end: datetime) -> None:
        self.lights(0)

        next_treatment_time = start
        treatment_generator = treatment_sequence_generator()
        while next_treatment_time < end and not self.interrupted:
            self.sleep_until(next_treatment_time)
            if self.interrupted:
                return
            light = next(treatment_generator)
            start_error = self.lights(light)
            on_time = datetime.now()


            self.sleep_until(on_time + TIME_OF_TREATMENT)
            end_error = self.lights(0)
            off_time = datetime.now()
            write_treatment(Treatment(
                light= light,
                start = on_time,
                end = off_time,
                error = start_error or end_error))
            next_treatment_time = off_time + TIME_BETWEEN_TREATMENTS

    def interrupt(self, signum, frame):
        logging.warning("Received SIGINT. Shutting down")
        requests.post(SLACK_URL, json={'text': "Interrupted"})
        self.interrupted = True

    def sleep_until(self, t: datetime) -> None:
        now = datetime.now()
        while now <= t and not self.interrupted:
            to_sleep = min(10, (t - now).total_seconds())
            sleep(to_sleep)
            now = datetime.now()

def run() -> None:
    l = Lighter()
    
    now = datetime.now(tz=TIMEZONE)
    now_time = datetime.now(tz=TIMEZONE).time()
    # The reason for just getting the time is that I do not fully understand how this library
    # decides what day it is. 
    start_time = (SUN.get_sunset_time(time_zone = TIMEZONE) + SUN_DELAY).time()
    end_time = (SUN.get_sunrise_time(time_zone = TIMEZONE) - SUN_DELAY).time()

    start = None
    end = None
    # since these treatments cross midnight < start time and > end time means not during
    # treatments.
    if now_time < start_time and now_time > end_time:
        start = datetime.combine(now.date(), start_time)
        end = datetime.combine(now.date() + timedelta(days=1), end_time)
    elif now_time >= start_time:
        start = now
        end = datetime.combine(now.date() + timedelta(days=1), end_time)
    elif now_time <= end_time:
        start = now
        end = datetime.combine(now.date(), end_time)
    else:
        logging.error("Couldn't create treatments because of issue determining start or end times")
        sys.exit(1)


    start = datetime.now() + timedelta(seconds=5)
    end = datetime.now() + timedelta(minutes=1)
    requests.post(SLACK_URL, json={'text': f"Starting treatments at {start}"})
    l.run_treatments(start, end)
    requests.post(SLACK_URL, json={'text': "Treatments done!"})
    print("***** DONE! *****")

async def dicsover_plugs() -> list[any]:
    found = await Discover.discover()
    alias = 'TP-LINK_Power Strip_53A7'
    strip = None
    for device in found:
        if device.alias == alias:
            strip = device
            break

    if not strip:
        raise Exception(f"failed to discover power strip with alias {alias}. {len(found)} devices found.")
    
    await strip.update()
    return strip.children

if __name__ == "__main__":
    run()
