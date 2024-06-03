# from django.test import TestCase
from maps import Direction
from asgiref.sync import sync_to_async
import asyncio
# from database import CarAccidentTest
from database import CarAccidentTest


async def main():
    # origin = "Place A"
    # destination = "Place B"
    # direction = Direction(origin, destination)

    # Direction() without arguments is a template Direction object where origin = "台北101" and destination = "台北市立動物園"
    # direction = Direction()
    # print(direction.data)
    # print(direction.coordinates)
    # print(direction.instructions)
    # print(await direction.fatality)
    # print(await direction.injury)
    pass



if __name__ == "__main__":
    # asyncio.run(main())
    accident = CarAccidentTest(year=111, month=12, rank=2)
    print(accident.get.longitude(123))