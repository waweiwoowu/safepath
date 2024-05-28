import asyncio
from database import CarAccidentDensityModel
from maps import Coordinate, Direction




async def get_density(coordinate):
    density = CarAccidentDensityModel()
    data = await density.fetch(coordinate[0], coordinate[1])
    return data


async def main():
    direction = Direction()
    data = await get_density((25.0017, 121.5806))
    print(data)


if __name__ == "__main__":
    asyncio.run(main())
