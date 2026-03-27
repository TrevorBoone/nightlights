import asyncio
from kasa import Discover
from datetime import datetime
from time import sleep
from generator import Treatment, read

def sleep_until(t: datetime):
    now = datetime.now()
    if now > t:
        return
    
    sleep( (t - now).total_seconds() )

# TODO change this to be more robust
async def test():
    plugs = await initialize()

    async def lights(light: int):
        for i, p in enumerate(plugs):
            if light - 1 == i:
                await p.turn_on()
            else:
                await p.turn_off()

    await lights(0)
    

    with open("test.csv") as f:
        treatments = read()
        print("\n".join(treatments))
        for t in treatments:
            now = datetime.now()
            if t.end < now:
                continue

            sleep_until(t.start)

            print(f"light: {t.light}")
            await lights(t.light)

            sleep_until(t.end)
            await lights(0)

            


# TODO figure out actual class name
async def initialize() -> list[any]:
    ## TODO change this to discover by alias or something to be robust across networks
    strip = await Discover.discover_single("10.0.0.69")
    await strip.update()
    return strip.children

if __name__ == "__main__":
    asyncio.run(test())
