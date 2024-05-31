import googlemaps
import asyncio
import json
# from explorer.test_data import *
import test_data
from _database import Coordinate


__all__ = ["GOOGLE_MAPS_API_KEY", "Coordinates", "Direction", "Geocode"]


"""
Please replace 'YOUR_API_KEY' with your Google Maps API key from the json file in '.\data\keys\safepath.json'
In order to prevent your GOOGLE_MAPS_API_KEY from being stolen on GitHub
You may copy and paste the file to any location outside of the project on your local device
And then add the file location to the list of the json file in '.\data\keys\paths.json'
"""

def _get_google_maps_api_paths():
    filepath = r"C:\Users\user\Documents\GitHub\safepath1\explorer\data\keys\paths.json"
    try:
        with open(filepath) as file:
            data = json.load(file)
        paths = data["GOOGLE_MAPS_API_KEY"]
        return paths
    except:
        return

def _get_google_maps_api_key():
    paths = _get_google_maps_api_paths()
    if not paths:
        return
    file_name = "\\safepath.json"
    for path in paths:
        try:
            with open(path+file_name) as file:
                data = json.load(file)
            key = data["GOOGLE_MAPS_API_KEY"]
            if key == "YOUR_API_KEY":
                continue
            return key
        except:
            continue
    return

GOOGLE_MAPS_API_KEY = _get_google_maps_api_key()


class Coordinates():
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.grid = []
        for coordinate in coordinates:
            coord = Coordinate(coordinate)
            self.grid.append((coord.latitude_grid, coord.longitude_grid))
        self.grid = list(set(self.grid))

class _GoogleMap():
    if GOOGLE_MAPS_API_KEY:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

class Direction():
    """Get directions between an origin point and a destination point.

    This class uses googlemaps.directions and returns data with a list of
        dictionaries. Please check 'constants.py' for more information.

    :param origin: The address or latitude/longitude value from which you wish
        to calculate directions.
    :type origin: string, dict, list, or tuple

    :param destination: The address or latitude/longitude value from which
        you wish to calculate directions. You can use a place_id as destination
        by putting 'place_id:' as a prefix in the passing parameter.
    :type destination: string, dict, list, or tuple

    Direction(origin, destination) would determine the direction from origin to
        destination. Note that this method would spend the quotas of
        the Directions API you use.

    If you want to determine direction without spending the quotas, please
        use Direction() without arguments. This is a default object which
        returns the direction from '台北101' to '台北市立動物園'. Please
        check 'constants.py' for more information.
    """
    def __init__(self, origin=None, destination=None):
        if origin and destination and GOOGLE_MAPS_API_KEY:
            self.data = _GoogleMap().gmaps.directions(origin, destination, )[0]
        else:
            self.data = test_data.DIRECTIONS[0]
        self.car_accident = _DirectionCarAccidentData(self.coordinates)
        self.earthquake = _DirectionEarthquakeData(self.coordinates)

    @property
    def overivew_coordinates(self):
        decoded_polyline = googlemaps.convert.decode_polyline(self.data['overview_polyline']['points'])
        route_coordinates = [(point['lat'], point['lng']) for point in decoded_polyline]
        return route_coordinates

    @property
    def coordinates(self):
        route_coordinates = []
        for step in self.data['legs'][0]['steps']:
            polyline = step['polyline']['points']
            decoded_polyline = googlemaps.convert.decode_polyline(polyline)
            route_coordinates += [(point['lat'], point['lng']) for point in decoded_polyline]
        return route_coordinates

    @property
    def instructions(self):
        route_instructions = []
        for step in self.data['legs'][0]['steps']:
            route_instructions.append(step['html_instructions'])
        return route_instructions

class _DirectionCarAccidentData():
    def __init__(self, coordinates):
        self.coordinates = coordinates

    @property
    async def fatality(self):
        fatality = 0
        for coordinate in self.coordinates:
            coord = Coordinate(coordinate)
            fatality += await coord.fatality
        return fatality

    @property
    async def injury(self):
        injury = 0
        for coordinate in self.coordinates:
            coord = Coordinate(coordinate)
            injury += await coord.injury
        return injury

class _DirectionEarthquakeData():
    def __init__(self, coordinates):
        self.data = []
        for coord in coordinates:
            self.data.append(Coordinate(coord))

    @property
    def magnitude(self):
        pass


class Geocode():
    def __init__(self, address=None):
        if not address:
            self.data = test_data.GEOCODE[0]
        else:
            self.data = _GoogleMap().gmaps.geocode(address)[0]
        self.postal_code = self.data["address_components"][-1]["long_name"]
        self.country = self.data["address_components"][-2]["long_name"]
        self.city = self.data["address_components"][-3]["long_name"]
        self.district = self.data["address_components"][-4]["long_name"]
        self.address = self.data["formatted_address"]

    @property
    def location(self):
        self.lat = self.data["geometry"]["location"]["lat"]
        self.lng = self.data["geometry"]["location"]["lng"]
        return (self.lat, self.lng)

async def _main():
    # geocode = Geocode("蘭嶼")
    # print(geocode.data)
    # print(geocode.city)
    # print(geocode.district)
    # print(geocode.address)
    # print(geocode.location)

    # direction = Direction()
    # print(direction.overivew_coordinates)
    # print(len(direction.coordinates))

    # coord = Coordinate(24.613, 121.852)
    # print(coord.latitude_grid)
    # print(coord.longitude_grid)
    # print(await coord.fatality)
    # print(await coord.injure)

    # coords = Coordinates(direction.coordinates)
    # print(coords.grid)

    # print(GOOGLE_MAPS_API_KEY)
    direction = Direction()
    print(await direction.car_accident.fatality)
    print(await direction.car_accident.injury)
    # direction.earthquake


if __name__ == "__main__":
    asyncio.run(_main())
