import googlemaps
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

### runserver
from explorer.test_data import *
from explorer.database import Coordinate, PedestrianHellSQLController
# KEY_PATH = r"C:\Users\user\Documents\GitHub\safepath1\explorer\data\keys\paths.json"

### run python file
# from test_data import *
# from database import Coordinate, PedestrianHellSQLController
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

class DirectionAPI():
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
            gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            self.data = gmaps.directions(origin, destination, )[0]
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

class Direction():
    def __init__(self, coordinates):
        self.coordinates = []
        for coordinate in coordinates:
            self.coordinates.append((coordinate["lat"], coordinate["lng"]))
        self._traffic_accident = None
        self._earthquake = None

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
        self._data = None
        self._number = None
        self._total_fatality = None
        self._total_injury = None
        self._pedestrian_fatality = None
        self._pedestrian_injury = None

    @property
    def data(self):
        if self._data is None:
            self._data = []
            for coord in self._coords:
                data = coord.traffic_accident.data
                if data:
                    self._data.append(data)
        return self._data

    @property
    def number(self):
        if self._number is None:
            self._number = 0
            for coord in self._coords:
                number = coord.traffic_accident.number
                if number:
                    self._number += number
        return self._number

    @property
    def total_fatality(self):
        if self._total_fatality is None:
            self._total_fatality = 0
            for coord in self._coords:
                fatality = coord.traffic_accident.total_fatality
                if fatality:
                    self._total_fatality += fatality
        return self._total_fatality

    @property
    def total_injury(self):
        if self._total_injury is None:
            self._total_injury = 0
            for coord in self._coords:
                injury = coord.traffic_accident.total_injury
                if injury:
                    self._total_injury += injury
        return self._total_injury

    @property
    def pedestrian_fatality(self):
        if self._pedestrian_fatality is None:
            self._pedestrian_fatality = 0
            for coord in self._coords:
                fatality = coord.traffic_accident.pedestrian_fatality
                if fatality:
                    self._pedestrian_fatality += fatality
        return self._pedestrian_fatality

    @property
    def pedestrian_injury(self):
        if self._pedestrian_injury is None:
            self._pedestrian_injury = 0
            for coord in self._coords:
                injury = coord.traffic_accident.pedestrian_injury
                if injury:
                    self._pedestrian_injury += injury
        return self._pedestrian_injury

class _DirectionEarthquakeData():
    def __init__(self, coordinates):
        self._coords = []
        for coordinate in coordinates:
            self._coords.append(Coordinate(coordinate))
        self._data = None
        self._date = None
        self._time = None
        self._latitude = None
        self._longitude = None
        self._coordinate = None
        self._magnitude = None
        self._depth = None

    @property
    def data(self):
        if self._data is None:
            data = []
            for coord in self._coords:
                elements = coord.earthquake.data
                if elements:
                    for element in elements:
                        data.append(element)
            if len(data) == 0:
                return None
            else:
                self._data = list(set(data))
                self.number = len(self._data)
        return self._data

    @property
    def date(self):
        if self._date is None:
            if not self.data:
                return None
            else:
                self._date = []
                for data in self.data:
                    self._date.append(data[1])
        return self._date

    @property
    def time(self):
        if self._time is None:
            if not self.data:
                return None
            else:
                self._time = []
                for data in self.data:
                    self._time.append(data[2])
        return self._time

    @property
    def latitude(self):
        if self._latitude is None:
            if not self.data:
                return None
            else:
                self._latitude = []
                for data in self.data:
                    self._latitude.append(data[3])
        return self._latitude

    @property
    def longitude(self):
        if self._longitude is None:
            if not self.data:
                return None
            else:
                self._longitude = []
                for data in self.data:
                    self._longitude.append(data[4])
        return self._longitude

    @property
    def coordinate(self):
        if self._coordinate is None:
            if not self.data:
                return None
            else:
                self._coordinate = []
                for data in self.data:
                    self._coordinate.append((data[3], data[4]))
        return self._coordinate

    @property
    def magnitude(self):
        if self._magnitude is None:
            if not self.data:
                return None
            else:
                self._magnitude = []
                for data in self.data:
                    self._magnitude.append(data[5])
        return self._magnitude

    @property
    def depth(self):
        if self._depth is None:
            if not self.data:
                return None
            else:
                self._depth = []
                for data in self.data:
                    self._depth.append(data[6])
        return self._depth


class Geocode():
    def __init__(self, address=None):
        language = "zh-TW"
        # language = None
        self.data = None
        self.latitude = None
        self.longitude = None
        self.name = None
        self.formatted_address = None
        self.address = None
        self.postal_code = None
        self.country = None
        self.area_1 = None
        self.area_2 = None
        self.area_3 = None
        self.neighborhood = None
        self.route = None
        self.street_number = None
        self.place_id = None
        try:
            if address:
                gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
                self.data = gmaps.geocode(address=address, language=language)[0]
            else:
                # self.data = GEOCODE_ZH[0]
                self.data = GEOCODE_ZH_1[0]
                # self.data = GEOCODE_ZH_2[0]
                # self.data = GEOCODE_ZH_3[0]
            self._get_attributes()
        except:
            pass

    def _get_attributes(self):
        self.latitude = self.data["geometry"]["location"]["lat"]
        self.longitude = self.data["geometry"]["location"]["lng"]
        self.formatted_address = self.data["formatted_address"]
        self.address = self.formatted_address
        self.place_id = self.data["place_id"]

        for address_component in self.data["address_components"]:
            types = address_component["types"]
            if "postal_code" in types:
                self.postal_code = address_component["long_name"]
            elif "country" in types:
                self.country = address_component["long_name"]
            elif "administrative_area_level_1" in types:
                self.area_1 = address_component["long_name"]
                if "台" in self.area_1:
                    self.area_1 = self.area_1.replace("台", "臺")
            elif "administrative_area_level_2" in types:
                self.area_2 = address_component["long_name"]
                if "台" in self.area_2:
                    self.area_2 = self.area_2.replace("台", "臺")
            elif "administrative_area_level_3" in types:
                self.area_3 = address_component["long_name"]
            elif "neighborhood" in types:
                self.neighborhood = address_component["long_name"]
            elif "route" in types:
                self.route = address_component["long_name"]
            elif "street_number" in types:
                self.street_number = address_component["long_name"]

        if self.postal_code:
            if self.postal_code in self.address:
                self.address = self.address[3:]
        if self.country:
            if self.country in self.address:
                self.address = self.address[2:]

        # Format address and truncate texts not needed
        types = ["street_number", "route", "political", "postal_code"]
        is_name = True
        for t in types:
            if t in self.data["address_components"][0]["types"]:
                is_name = False
                break
        if is_name:
            self.name = self.data["address_components"][0]["long_name"]
            if len(self.address) > 7:
                if self.name in self.address:
                    self.address = self.address[:-1 * len(self.name)]
        if "台" in self.address[:6]:
            self.address = self.address[:6].replace("台", "臺") + self.address[6:]


    @property
    def coordinate(self):
        return (self.latitude, self.longitude)


class Taiwan():
    def __init__(self):
        self.traffic_accident = _TrafficAccidentData()

class _TrafficAccidentData():
    def __init__(self):
        self._controller = PedestrianHellSQLController()
        self.number = GetSQLData(self._controller, "number", 3)
        self.total_fatality = GetSQLData(self._controller, "total_fatality", 4)
        self.total_injury = GetSQLData(self._controller, "total_injury", 5)
        self.pedestrian_fatality = GetSQLData(self._controller, "pedestrian_fatality", 6)
        self.pedestrian_injury = GetSQLData(self._controller, "pedestrian_injury", 7)

class GetSQLData:
    def __init__(self, controller, column, index):
        self._controller = controller
        self._column = column
        self._index = index
        self._data = None

    def sorting(self, number_of_data=None, is_ascending=False):
        if self._data is None:
            self._data = self._controller.select_by_order(self._column, is_ascending)
        if number_of_data:
            return self._data[:number_of_data]
        else:
            return self._data

    def sum(self):
        sum_ = 0
        if self._data is None:
            self._data = self.sorting()
        for data in self._data:
            sum_ += data[self._index]
        return sum_


def test_Direction():
    # direction = Direction()
    start = "台北車站"
    destination = "台灣大學"
    direction = Direction(start, destination)
    # print(direction.coordinates)
    print("[Traffic Accident Data]")
    print("data:", direction.traffic_accident.data)
    print("number:", direction.traffic_accident.number)
    print("total_fatality:", direction.traffic_accident.total_fatality)
    print("total_injury:", direction.traffic_accident.total_injury)
    print("pedestrian_fatality:", direction.traffic_accident.pedestrian_fatality)
    print("pedestrian_injury:", direction.traffic_accident.pedestrian_injury)
    print("[Earthquake Data]")
    print("data:", direction.earthquake.data)
    print("number:", direction.earthquake.number)
    print("date:", direction.earthquake.date)
    print("time:", direction.earthquake.time)
    print("latitude:", direction.earthquake.latitude)
    print("longitude:", direction.earthquake.longitude)
    print("coordinate:", direction.earthquake.coordinate)
    print("magnitude:", direction.earthquake.magnitude)
    print("depth:", direction.earthquake.depth)
    pass

def test_Geocode():
    # address = "大稻埕碼頭"
    # address = "大稻埕碼頭_大稻埕碼頭貨櫃市集"
    # address = "陽明書屋"
    # geocode = Geocode(address)
    geocode = Geocode()
    print(geocode.data)
    print()
    print("name:", geocode.name)
    print("postal_code:", geocode.postal_code)
    print("country:", geocode.country)
    print("area_1:", geocode.area_1)
    print("area_2:", geocode.area_2)
    print("area_3:", geocode.area_3)
    print("neighborhood:", geocode.neighborhood)
    print("formatted_address:", geocode.formatted_address)
    print("address:", geocode.address)
    print("latitude:", geocode.latitude)
    print("longitude:", geocode.longitude)
    print("coordinate:", geocode.coordinate)
    print("place_id:", geocode.place_id)
    pass

def test_Taiwan():
    taiwan = Taiwan()
    number_of_data = 5
    is_ascending = False

    number = taiwan.traffic_accident.number.sorting(number_of_data, is_ascending)
    total_fatality = taiwan.traffic_accident.total_fatality.sorting(number_of_data, is_ascending)
    total_injury = taiwan.traffic_accident.total_injury.sorting(number_of_data, is_ascending)
    number_sum = taiwan.traffic_accident.number.sum()
    total_fatality_sum = taiwan.traffic_accident.total_fatality.sum()
    total_injury_sum = taiwan.traffic_accident.total_injury.sum()

    print()
    print("2022年交通事故統計")
    print()

    print("[事故次數]")
    print(f"全 國: {number_sum}次 (每月{number_sum//12}次)")
    for i in range(number_of_data):
        print(f"第{i+1}名:", end=" ")
        print(f"{number[i][1]} {number[i][2]} {number[i][3]}")

    print()
    print("[死亡人數]")
    print(f"全 國: {total_fatality_sum}人 (每月{total_fatality_sum//12}人)")
    for i in range(number_of_data):
        print(f"第{i+1}名:", end=" ")
        print(f"{total_fatality[i][1]} {total_fatality[i][2]} {total_fatality[i][4]}")

    print()
    print("[受傷人數]")
    print(f"全 國: {total_injury_sum}人 (每月{total_injury_sum//12}人)")
    for i in range(number_of_data):
        print(f"第{i+1}名:", end=" ")
        print(f"{total_injury[i][1]} {total_injury[i][2]} {total_injury[i][5]}")
    pass

if __name__ == "__main__":
    # test_Direction()
    # test_Geocode()
    test_Taiwan()
    pass
