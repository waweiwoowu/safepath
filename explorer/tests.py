from django.test import TestCase
from maps import Direction
import asyncio


async def main():
    # origin = "Place A"
    # destination = "Place B"
    # direction = Direction(origin, destination)
    
    # Direction() without arguments is a template Direction object where origin = "台北101" and destination = "台北市立動物園"
    direction = Direction()
    print(await direction.fatality)
    print(await direction.injury)


if __name__ == "__main__":
    asyncio.run(main())