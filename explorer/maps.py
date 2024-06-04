import googlemaps
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

### runserver
# from explorer.test_data import *
# from explorer.database import Coordinate
# KEY_PATH = r"C:\Users\user\Documents\GitHub\safepath1\explorer\data\keys\paths.json"

### run python file
from test_data import *
from database import Coordinate
KEY_PATH = r".\data\keys\paths.json"

__all__ = ["GOOGLE_MAPS_API_KEY", "Coordinates", "Direction", "Geocode"]


"""
Please replace 'YOUR_API_KEY' with your Google Maps API key from the json file in '.\data\keys\safepath.json'
In order to prevent your GOOGLE_MAPS_API_KEY from being stolen on GitHub
You may copy and paste the file to any location outside of the project on your local device
And then add the file location to the list of the json file in '.\data\keys\paths.json'
"""

def _get_google_maps_api_paths():
    try:
        with open(KEY_PATH) as file:
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
        for coordinate in self.coordinates:
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
            self.data = _GoogleMap.gmaps.directions(origin, destination, )[0]
        else:
            self.data = DIRECTIONS[0]
        self._traffic_accident = None
        self._earthquake = None

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

    @property
    def traffic_accident(self):
        if self._traffic_accident is None:
            self._traffic_accident = _DirectionTrafficAccidentData(self.coordinates)
        return self._traffic_accident
    
    @property
    def earthquake(self):
        if self._earthquake is None:
            self._earthquake = _DirectionEarthquakeData(self.coordinates)
        return self._earthquake

class _DirectionTrafficAccidentData():
    def __init__(self, coordinates):
        self._coords = []
        for coordinate in coordinates:
            self._coords.append(Coordinate(coordinate))
    
    @property
    def data(self):
        data = []
        for coord in self._coords:
            _data = coord.traffic_accident.data
            if _data:
                data.append(_data)
        return data
    
    @property
    def number(self):
        total_number = 0
        for coord in self._coords:
            number = coord.traffic_accident.number
            if number:
                total_number += number
        return total_number

    @property
    def total_fatality(self):
        total_fatality = 0
        for coord in self._coords:
            fatality = coord.traffic_accident.total_fatality
            if fatality:
                total_fatality += fatality
        return total_fatality
    
    @property
    def total_injury(self):
        total_injury = 0
        for coord in self._coords:
            injury = coord.traffic_accident.total_injury
            if injury:
                total_injury += injury
        return total_injury
    
    @property
    def pedestrian_fatality(self):
        pedestrian_fatality = 0
        for coord in self._coords:
            fatality = coord.traffic_accident.pedestrian_fatality
            if fatality:
                pedestrian_fatality += fatality
        return pedestrian_fatality
    
    @property
    def pedestrian_injury(self):
        pedestrian_injury = 0
        for coord in self._coords:
            injury = coord.traffic_accident.pedestrian_injury
            if injury:
                pedestrian_injury += injury
        return pedestrian_injury

class _DirectionEarthquakeData():
    def __init__(self, coordinates):
        self._coords = []
        for coordinate in coordinates:
            self._coords.append(Coordinate(coordinate))

    @property
    def data(self):
        data = []
        for coord in self._coords:
            elements = coord.earthquake.data
            if elements:
                for element in elements:
                    data.append(element)
        if len(data) == 0:
            return None
        else:
            return list(set(data))

    @property
    def date(self):
        if self.data:
            date = []
            for data in self.data:
                date.append(data[1])
            return date
        return None

    @property
    def time(self):
        if self.data:
            time = []
            for data in self.data:
                time.append(data[2])
            return time
        return None

    @property
    def latitude(self):
        if self.data:
            latitude = []
            for data in self.data:
                latitude.append(data[3])
            return latitude
        return None

    @property
    def longitude(self):
        if self.data:
            longitude = []
            for data in self.data:
                longitude.append(data[4])
            return longitude
        return None
    
    @property
    def coordinate(self):
        if self.data:
            coordinate = []
            for data in self.data:
                coordinate.append((data[3], data[4]))
            return coordinate
        return None

    @property
    def magnitude(self):
        if self.data:
            magnitude = []
            for data in self.data:
                magnitude.append(data[5])
            return magnitude
        return None

    @property
    def depth(self):
        if self.data:
            depth = []
            for data in self.data:
                depth.append(data[6])
            return depth
        return None


class Geocode():
    def __init__(self, address=None):
        if not address:
            self.data = GEOCODE[0]
        else:
            self.data = _GoogleMap.gmaps.geocode(address)[0]
        self.postal_code = self.data["address_components"][-1]["long_name"]
        self.country = self.data["address_components"][-2]["long_name"]
        self.administrative_area_level_1 = self.data["address_components"][-3]["long_name"]
        self.administrative_area_level_2 = self.data["address_components"][-4]["long_name"]
        self.address = self.data["formatted_address"]
        self.latitude = self.data["geometry"]["location"]["lat"]
        self.longitude = self.data["geometry"]["location"]["lng"]

    @property
    def location(self):
        return (self.latitude, self.longitude)


def test():
    direction = Direction()
    # print(direction.coordinates)
    print(direction.traffic_accident.data)
    print(direction.traffic_accident.number)
    print(direction.traffic_accident.total_fatality)
    print(direction.traffic_accident.total_injury)
    print(direction.traffic_accident.pedestrian_fatality)
    print(direction.traffic_accident.pedestrian_injury)
    print(direction.earthquake.data)
    print(direction.earthquake.date)
    print(direction.earthquake.time)
    print(direction.earthquake.latitude)
    print(direction.earthquake.longitude)
    print(direction.earthquake.coordinate)
    print(direction.earthquake.magnitude)
    print(direction.earthquake.depth)
    pass


if __name__ == "__main__":
    test()
    pass
