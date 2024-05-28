import asyncio
from django.test import TestCase
from maps import Direction


async def main():
    direction = Direction()
    print(await direction.fatality)
    print(await direction.injury)


if __name__ == "__main__":
    asyncio.run(main())