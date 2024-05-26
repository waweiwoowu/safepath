import os
import sys
import django
import math
from pathlib import Path
from asgiref.sync import sync_to_async
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Construct the project path relative to this script
current_dir = Path(__file__).resolve().parent
project_path = current_dir.parent

# Add the project path to the Python path
sys.path.append(str(project_path))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safepath.settings')

# Initialize Django
django.setup()

# Now import the Django models
from explorer.models import Earthquake

DEGREE_DIFFERENCE = 0.01

def rounding(degree):
    power = math.log10(DEGREE_DIFFERENCE)
    if power > 0:
        decimal_place = 0
    else:
        decimal_place = math.ceil(abs(power))
    return round(round(degree / DEGREE_DIFFERENCE) * DEGREE_DIFFERENCE, decimal_place)

class Coordinate:
    def __init__(self, latitude=0, longitude=0) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.latitude_rounding = rounding(self.latitude)
        self.longitude_rounding = rounding(self.longitude)

    @property
    def is_existing(self):
        pass

# Define an async function to fetch Earthquake data
async def fetch_earthquakes():
    earthquakes = await sync_to_async(lambda: list(Earthquake.objects.all()))()
    return earthquakes

async def main():
    coord = Coordinate(25.2525, 123.456)
    print(coord.latitude_rounding)
    print(coord.longitude_rounding)

    earthquakes = await fetch_earthquakes()
    print(earthquakes)

if __name__ == "__main__":
    asyncio.run(main())
