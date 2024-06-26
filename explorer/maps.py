import googlemaps
import json
import sys
import os
import concurrent.futures


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

### runserver
from explorer.test_data import *
from explorer.database import Coordinate, PedestrianHellSQLController, AttractionSQLController, RestaurantSQLController
import explorer.risk as risk

### run python file
# from test_data import *
# from database import Coordinate, PedestrianHellSQLController

__all__ = ["GOOGLE_MAPS_API_KEY", "Coordinates", "Direction", "Geocode"]


"""
Please replace 'YOUR_API_KEY' with your Google Maps API key from the json file in '.\data\keys\safepath.json'
In order to prevent your GOOGLE_MAPS_API_KEY from being stolen on GitHub
You may copy and paste the file to any location outside of the project on your local device
And then add the file location to the list of the json file in '.\data\keys\paths.json'
"""
from dotenv import load_dotenv

load_dotenv()

def _get_google_maps_api_paths():
    KEY_PATH = r".\data\keys\paths.json"
    try:
        with open(KEY_PATH) as file:
            data = json.load(file)
        paths = data["GOOGLE_MAPS_API_KEY"]
        return paths
    except:
        return

def _get_google_maps_api_key_from_path():
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

def _get_google_maps_api_key_from_dotenv():
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if api_key:
            return api_key
        else:
            raise ValueError("API key not found in environment variables")
    except Exception as e:
        print(f"Error: {e}")
        return None    

def _get_google_maps_api_key():
    key = _get_google_maps_api_key_from_path()
    if key:
        return key
    key = _get_google_maps_api_key_from_dotenv()
    return key

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

    DirectionAPI(origin, destination) would determine the direction from origin to
        destination. Note that this method would spend the quotas of
        the Directions API you use.

    If you want to determine direction without spending the quotas, please
        use DirectionAPI() without arguments. This is a default object which
        returns the direction from '台北101' to '台北市立動物園'. Please
        check 'constants.py' for more information.
    """
    def __init__(self, origin=None, destination=None, waypoints=None, optimize_waypoints=True):
        if origin and destination and GOOGLE_MAPS_API_KEY:
            gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            self.data = gmaps.directions(origin=origin,
                                         destination=destination,
                                         waypoints=waypoints,
                                         optimize_waypoints=optimize_waypoints, )[0]
        else:
            self.data = DIRECTIONS[0]
        self._coordinates = None
        self._traffic_accident = None
        self._earthquake = None

    @property
    def overivew_coordinates(self):
        decoded_polyline = googlemaps.convert.decode_polyline(self.data['overview_polyline']['points'])
        route_coordinates = [(point['lat'], point['lng']) for point in decoded_polyline]
        return route_coordinates

    @property
    def coordinates(self):
        if self._coordinates is None:
            self._coordinates = []
            for step in self.data['legs'][0]['steps']:
                polyline = step['polyline']['points']
                decoded_polyline = googlemaps.convert.decode_polyline(polyline)
                self._coordinates += [(point['lat'], point['lng']) for point in decoded_polyline]
        return self._coordinates

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
        try:
            for coordinate in coordinates:
                self.coordinates.append((coordinate["lat"], coordinate["lng"]))
        except:
            self.coordinates = coordinates
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
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_coord = {executor.submit(self._get_traffic_data, coord): coord for coord in self._coords}
                self._data = []
                for future in concurrent.futures.as_completed(future_to_coord):
                    data = future.result()
                    if data:
                        self._data.append(data)
        return self._data

    def _get_traffic_data(self, coord):
        return coord.traffic_accident.data

    @property
    def number(self):
        if self._number is None:
            if not self.data:
                return 0
            else:
                self._number = 0
                for data in self.data:
                    self._number += data[3]
        return self._number

    @property
    def total_fatality(self):
        if self._total_fatality is None:
            if not self.data:
                return 0
            else:
                self._total_fatality = 0
                for data in self.data:
                    self._total_fatality += data[4]
        return self._total_fatality

    @property
    def total_injury(self):
        if self._total_injury is None:
            if not self.data:
                return 0
            else:
                self._total_injury = 0
                for data in self.data:
                    self._total_injury += data[5]
        return self._total_injury

    @property
    def pedestrian_fatality(self):
        if self._pedestrian_fatality is None:
            if not self.data:
                return None
            else:
                self._pedestrian_fatality = 0
                for data in self.data:
                    self._pedestrian_fatality += data[6]
        return self._pedestrian_fatality

    @property
    def pedestrian_injury(self):
        if self._pedestrian_injury is None:
            if not self.data:
                return None
            else:
                self._pedestrian_injury = 0
                for data in self.data:
                    self._pedestrian_injury += data[7]
        return self._pedestrian_injury

class _DirectionEarthquakeData():
    def __init__(self, coordinates):
        self._coords = []
        for coordinate in coordinates:
            self._coords.append(Coordinate(coordinate))
        self._data = None
        self._number = None
        self._date = None
        self._time = None
        self._latitude = None
        self._longitude = None
        self._coordinate = None
        self._magnitude = None
        self._depth = None
        self._avg_magnitude = None
        self._avg_depth = None

    @property
    def data(self):
        if self._data is None:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_coord = {executor.submit(self._get_earthquake_data, coord): coord for coord in self._coords}
                data = []
                for future in concurrent.futures.as_completed(future_to_coord):
                    elements = future.result()
                    if elements:
                        data.extend(elements)
            if len(data) == 0:
                return None
            else:
                self._data = list(set(data))
        return self._data

    def _get_earthquake_data(self, coord):
        return coord.earthquake.data

    @property
    def number(self):
        if self._number is None:
            if not self.data:
                return 0
            else:
                self._number = len(self.data)
        return self._number

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

    @property
    def average_magnitude(self):
        if self._avg_magnitude is None:
            self._avg_magnitude = risk.average_magnitude(self.magnitude)
        return self._avg_magnitude

    @property
    def average_depth(self):
        if self._avg_depth is None:
            try:
                self._avg_depth = 0
                for depth in self.depth:
                    self._avg_depth += depth
                self._avg_depth /= len(self.depth)
            except:
                return None
        return self._avg_depth


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


class Hotspot():
    def __init__(self, name=None, area_1=None, area_2=None, coordinate=None):
        self._columns = []
        if name:
            self._name = name
            self._columns.append(("name", self._name))
        if area_1:
            self._area_1 = area_1
            self._columns.append(("area_1", self._area_1))
        if area_2:
            self._area_2 = area_2
            self._columns.append(("area_2", self._area_2))
        if coordinate:
            self._coordinate = coordinate
            self._latitude = self._coordinate[0]
            self._longitude = self._coordinate[0]
            self._columns.append(("latitude", self._latitude))
            self._columns.append(("longitude", self._longitude))

        self.controller = AttractionSQLController()
        self.data = []
        self.id = []
        self.name = []
        self.latitude = []
        self.longitude = []
        self.area_1 = []
        self.area_2 = []
        self.coordinate = []
        self.address = []
        self.image = []

        self._get_data()

    def _get_data(self):
        self.data = self.controller.get_data_from_columns(self._columns)

        for data in self.data:
            self.id.append(data[0])
            self.name.append(data[1])
            self.latitude.append(data[2])
            self.longitude.append(data[3])
            self.coordinate.append((data[2], data[3]))
            self.area_1.append(data[4])
            self.area_2.append(data[5])
            self.address.append(data[6])
            self.image.append(data[7])

class Foodspot():
    def __init__(self, name=None, area_1=None, area_2=None, coordinate=None,
                 rating=None, avg_price=None):
        self._columns = []
        if name:
            self._name = name
            self._columns.append(("name", self._name))
        if area_1:
            if area_1[0] == "臺":
                area_1 = area_1.replace("臺", "台")
            self._area_1 = area_1
            self._columns.append(("area_1", self._area_1))
        if area_2:
            self._area_2 = area_2
            self._columns.append(("area_2", self._area_2))
        if coordinate:
            self._coordinate = coordinate
            self._latitude = self._coordinate[0]
            self._longitude = self._coordinate[0]
            self._columns.append(("latitude", self._latitude))
            self._columns.append(("longitude", self._longitude))
        if rating:
            self._rating = rating
            self._columns.append(("rating", self._rating))
        if avg_price:
            self._avg_price = avg_price
            self._columns.append(("avg_price", self._avg_price))

        self.controller = RestaurantSQLController()
        self.data = []
        self.id = []
        self.name = []
        self.latitude = []
        self.longitude = []
        self.area_1 = []
        self.area_2 = []
        self.coordinate = []
        self.address = []
        self.phone = []
        self._opening_hours = []
        self.rating = []
        self.avg_price = []
        self.image = []

        self._get_data()

    def _get_data(self):
        self.data = self.controller.get_data_from_columns(self._columns)

        for data in self.data:
            self.id.append(data[0])
            self.name.append(data[1])
            self.latitude.append(data[2])
            self.longitude.append(data[3])
            self.coordinate.append((data[2], data[3]))
            self.area_1.append(data[4])
            self.area_2.append(data[5])
            self.address.append(data[6])
            self.phone.append(data[7])
            self._opening_hours.append(data[8])
            self.rating.append(data[9])
            self.avg_price.append(data[10])
            self.image.append(data[11])

    #     self._get_opening_hours()

    # def _get_opening_hours(self):
    #     for opening_hours in self._opening_hours:
    #         opening_hours =
    #         self.opening_hours.mon

class OpeningHours:
    def __init__(self, opening_hours):
        opening_hours = opening_hours.replace("'", '"')
        self.all = json.loads(opening_hours)
        try:
            self.mon = self.all[0]
            self.tue = self.all[1]
            self.wed = self.all[2]
            self.thu = self.all[3]
            self.fri = self.all[4]
            self.sat = self.all[5]
            self.sun = self.all[6]
        except:
            self.mon = None
            self.tue = None
            self.wed = None
            self.thu = None
            self.fri = None
            self.sat = None
            self.sun = None

class TrafficAccidentData():
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


def test_DirectionAPI():
    start = "台北車站"
    destination = "高雄愛河"
    waypoints = ["桃園國際機場", "板橋捷運站"]
    waypoints = None
    optimize_waypoints = True
    direction = DirectionAPI(start, destination, waypoints, optimize_waypoints)
    direction.traffic_accident.data
    direction.earthquake.data
    pass

def test_Direction():
    # direction = Direction()
    start = "台北車站"
    destination = "台灣大學"
    direction = Direction(start, destination)
    # print(direction.coordinates)
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

def test_hotspot():
    area_1 = "臺北市"
    area_2 = "信義區"
    hotspot = Hotspot(area_1=area_1, area_2=area_2)
    print(hotspot.id)
    print(hotspot.name)
    print(hotspot.latitude)
    print(hotspot.longitude)

def test_foodspot():
    area_1 = "臺北市"
    area_2 = "信義區"
    foodspot = Foodspot(area_1=area_1, area_2=area_2)
    # print(foodspot.data)
    print(foodspot.id)
    print(foodspot.name)
    print(foodspot.latitude)
    print(foodspot.longitude)

if __name__ == "__main__":
    # test_DirectionAPI()
    # test_Direction()
    # test_Geocode()
    # test_Taiwan()
    # test_hotspot()
    # test_foodspot()
    print(GOOGLE_MAPS_API_KEY)
    pass
