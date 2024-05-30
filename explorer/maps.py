import googlemaps
import asyncio
import json
import test_data
from database import Coordinate


__all__ = ["GOOGLE_MAPS_API_KEY", "Coordinates", "Direction", "Geocode"]


def _get_google_maps_api_paths():
    filepath = r".\data\keys\paths.json"
    with open(filepath) as file:
        data = json.load(file)
    paths = data["GOOGLE_MAPS_API_KEY"]
    return paths

def _get_google_maps_api_key():
    paths = _get_google_maps_api_paths()
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
    return None

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
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

class Direction(_GoogleMap):
    def __init__(self, origin=None, destination=None):
        if origin and destination and GOOGLE_MAPS_API_KEY:
            self.data = self.gmaps.directions(origin, destination, )[0]
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


class Geocode(_GoogleMap):
    def __init__(self, address=None):
        if not address:
            self.data = test_data.GEOCODE[0]
        else:
            self.data = self.gmaps.geocode(address)[0]
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
    # geocode = Geocode()
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

    direction = Direction()
    print(await direction.car_accident.fatality)
    print(await direction.car_accident.injury)
    # direction.earthquake


if __name__ == "__main__":
    asyncio.run(_main())
