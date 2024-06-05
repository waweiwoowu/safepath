import json
import math
import sqlite3
import pandas as pd
from datetime import datetime
# import explorer.risk
import risk

DEGREE_DIFFERENCE = 0.0001
TRACKING_JSON_PATH = r".\data\tracking.json"

def rounding(degree, difference=DEGREE_DIFFERENCE):
    """This method is used to determine rounded values of degrees of latitudes
        or longitudes based on degrees of latitude difference and longitude
        difference, respectively. By default, both latitude and longitude are
        calculated by a constant 'DEGREE_DIFFERENCE' in a value of 0.0001."""

    power = math.log10(difference)
    if power > 0:
        return round(float(degree) / difference) * difference
    else:
        decimal_place = math.ceil(abs(power))
        return round(round(float(degree) / difference) * difference, decimal_place)

class InvalidCoordinateError(Exception):
    def __init__(self, message="""Invalid coordinate. Must provide either a single
                                 iterable or separate latitude and longitude values."""):
        self.message = message
        super().__init__(self.message)

class Coordinate:
    def __init__(self, *coordinate) -> None:
        """This class is mainly used to determine rounded values of coordinates
            in specific degree difference

        :param *coordinate: The latitude value and the longitude value.
        :type *coordinate: two float numbers or a tuple (25.2525, 123.456)."""

        if len(coordinate) == 1:
            if len(coordinate[0]) != 2:
                message = "Invalid coordinate format. Must provide latitude and longitude values."
                raise InvalidCoordinateError(message)
            self.latitude = coordinate[0][0]
            self.longitude = coordinate[0][1]
        elif len(coordinate) == 2:
            self.latitude = coordinate[0]
            self.longitude = coordinate[1]
        else:
            raise InvalidCoordinateError()

        if abs(self.latitude) > 90:
            message = "Invalid latitude value. Must between -90 and 90 degrees."
            raise InvalidCoordinateError(message)
        if abs(self.longitude) > 180:
            message = "Invalid latitude value. Must between -180 and 180 degrees."
            raise InvalidCoordinateError(message)

        self.latitude_grid = rounding(self.latitude)
        self.longitude_grid = rounding(self.longitude)
        self._traffic_accident = None
        self._earthquake = None

    @property
    def traffic_accident(self):
        if self._traffic_accident is None:
            self._traffic_accident = TrafficAccidentData(self.latitude_grid, self.longitude_grid)
        return self._traffic_accident

    @property
    def earthquake(self):
        if self._earthquake is None:
            self._earthquake = EarthquakeData(self.latitude_grid, self.longitude_grid)
        return self._earthquake

class TrafficAccidentData():
    def __init__(self, latitude, longitude):
        controller = TrafficAccidentSQLController()
        self.data = controller.select_from_coordinate(latitude, longitude)
        self.id = None
        self.number = None
        self.total_fatality = None
        self.total_injury = None
        self.pedestrian_fatality = None
        self.pedestrian_injury = None

        if self.data:
            self.data = self.data[0]
            self.id = self.data[0]
            self.number = self.data[3]
            self.total_fatality = self.data[4]
            self.total_injury = self.data[5]
            self.pedestrian_fatality = self.data[6]
            self.pedestrian_injury = self.data[7]

class EarthquakeData():
    def __init__(self, latitude, longitude):
        self.latitude = rounding(latitude, difference=0.01)
        self.longitude = rounding(longitude, difference=0.01)
        controller = EarthquakeSQLController()
        self.data = controller.select_from_coordinate(self.latitude, self.longitude)

        self.id = []
        self.date = []
        self.time = []
        self.magnitude = []
        self.depth = []
        if self.data:
            for data in self.data:
                self.id.append(data[0])
                self.date.append(data[1])
                self.time.append(data[2])
                self.magnitude.append(data[5])
                self.depth.append(data[6])

def check_if_month_is_valid(month):
    if month is not None:
        if type(month) != int or (month < 1 or month > 12):
            message = "Invalid mouth. Must be an integer between 1 and 12 (including)."
            raise InvalidRangeError(message)

class InvalidRangeError(Exception):
    def __init__(self, message="Invalid range."):
        self.message = message
        super().__init__(self.message)

class CarAccident:
    def __init__(self, year, month=None, rank=2):
        """This class is used to get data from car accident csv files.

        :param year: The year value of Republic of China.
        :type year: int

        :param month: The month value.
        :type month: int

        :param rank: The type of rank value of a car accident. There are three
            types of car accidents: A1, A2, and A3. Currently, A3-type data is
            not supported.
        :type rank: int or string"""

        self._year = year
        self._month = month
        self._rank = rank
        self._is_arg_valid()
        self._df = pd.DataFrame()
        self._read_csv_file()
        self._get_data()

    def _is_arg_valid(self):
        """This method is used to determine if the auguments are valid."""

        with open(TRACKING_JSON_PATH) as file:
            data = json.load(file)
            starting_year = data["csv"]["car_accident"]["starting_year"]
            ending_year = data["csv"]["car_accident"]["ending_year"]
        if (type(self._year) != int or (self._year < starting_year or self._year > ending_year)):
            message = f"Invalid year. Must be an integer between {starting_year} and {ending_year} (including)."
            raise InvalidRangeError(message)
        check_if_month_is_valid(self._month)

    def _read_csv_file(self):
        """This method is used to read and get data from the csv files."""

        dtype_mapping = {
            "發生日期": str,
            "發生時間": str,
            "經度": float,
            "緯度": float,
            "死亡受傷人數": str,
            "發生地點": str,
            "事故類型": str
        }
        if self._rank == 1 or self._rank == '1' or self._rank == "A1" or self._rank == "a1":
            path = f"./data/accidents/{self._year}/{self._year}年度A1交通事故資料.csv"
            self._df = pd.read_csv(path)
            self._df = self._df[:-2]
            # if self._month:
            #     self._df['發生日期'] = self._df['發生日期'].astype(int)
            #     if self._month > 9:
            #         self._df = self._df[self._df['發生日期'].astype(str).str[4:6] == str(self._month)]
            #     else:
            #         self._df = self._df[self._df['發生日期'].astype(str).str[4:6] == f"0{self._month}"]
            #     self._df['發生日期'] = self._df['發生日期'].astype(float)
            #     self._df = self._df.reset_index(drop=True)
        elif self._rank == 2 or self._rank == '2' or self._rank == "A2" or self._rank == "a2":
            if not self._month:
                for m in range(1, 13):
                    path = f"./data/accidents/{self._year}/{self._year}年度A2交通事故資料_{m}.csv"
                    monthly_data = pd.read_csv(path, dtype=dtype_mapping, low_memory=False)
                    monthly_data = monthly_data[:-2]
                    self._df = pd.concat([self._df, monthly_data], ignore_index=True)
            else:
                path = f"./data/accidents/{self._year}/{self._year}年度A2交通事故資料_{self._month}.csv"
                self._df = pd.read_csv(path, dtype=dtype_mapping, low_memory=False)
                self._df = self._df[:-2]
        else:
            message = "Invalid rank. Must be either 1, '1', 'A1', 'a1', or 2, '2', 'A2', 'a2'."
            raise InvalidRangeError(message)

    def _get_data(self):
        """This method is used to take the data of interest"""

        self._dates = [datetime.strptime(str(int(d)), "%Y%m%d").strftime("%Y-%m-%d") for d in self._df["發生日期"]]
        self._times = [datetime.strptime(str(int(t)).zfill(6), "%H%M%S").strftime("%H:%M:%S") for t in self._df["發生時間"]]
        self._latitudes = self._df["緯度"]
        self._longitudes = self._df["經度"]
        self._casualties = self._df["死亡受傷人數"]
        self._fatalities = [int(c[2]) for c in self._casualties]
        self._injuries = [int(c[-1]) for c in self._casualties]
        self._location = self._df["發生地點"]
        self._area_1 = [loc[:3] for loc in self._location]
        self._area_2 = [loc[3:7] for loc in self._location]
        # Check if the third character of the string is not one of "鄉", "鎮", "市", or "區"
        for i in range(len(self._area_2)):
            if self._area_2[i][2] not in "鄉鎮市區":
                if self._area_2[i][1] in "鄉鎮市區":
                    # If the condition is met, truncate the string to the first two characters
                    self._area_2[i] = self._area_2[i][:2]
            else:
                self._area_2[i] = self._area_2[i][:3]
        self._includes_pedestrian = self._df["事故類型及型態大類別名稱"].str.contains('人')

        self._reorganize_data()

    def _reorganize_data(self):
        """This method is used to take out the duplicated data"""

        check = 0
        longitude_check = 0
        latitude_check = 0
        self._data = []
        for i in range(len(self._dates)):
            if self._times[i] == check:
                if (self._longitudes[i] == longitude_check) and (self._latitudes[i] == latitude_check):
                    continue
                else:
                    longitude_check = self._longitudes[i]
                    latitude_check = self._latitudes[i]
            else:
                check = self._times[i]
                self._data.append([
                    self._dates[i],
                    self._times[i],
                    self._latitudes[i],
                    self._longitudes[i],
                    self._fatalities[i],
                    self._injuries[i],
                    self._area_1[i],
                    self._area_2[i],
                    self._includes_pedestrian[i]
                ])
        self.data = pd.DataFrame(self._data, columns=[
            "date",
            "time",
            "latitude",
            "longitude",
            "fatality",
            "injury",
            "area_1",
            "area_2",
            "includes_pedestrian"
        ])
        self._dates = self.data.iloc[:, 0]
        self._times = self.data.iloc[:, 1]
        self._latitudes = self.data.iloc[:, 2]
        self._longitudes = self.data.iloc[:, 3]
        self._fatalities = self.data.iloc[:, 4]
        self._injuries = self.data.iloc[:, 5]
        self._area_1s = self.data.iloc[:, 6]
        self._area_2s = self.data.iloc[:, 7]
        self._includes_pedestrian = self.data.iloc[:, 8]

    def date(self, id=None):
        if id is not None:
            return self._dates[id]
        else:
            return self._dates

    def time(self, id=None):
        if id is not None:
            return self._times[id]
        else:
            return self._times

    def latitude(self, id=None):
        if id is not None:
            return self._latitudes[id]
        else:
            return self._latitudes

    def longitude(self, id=None):
        if id is not None:
            return self._longitudes[id]
        else:
            return self._longitudes

    def fatality(self, id=None):
        if id is not None:
            return int(self._fatalities[id])
        else:
            return self._fatalities

    def injury(self, id=None):
        if id is not None:
            return int(self._injuries[id])
        else:
            return self._injuries

    def area_1(self, id=None):
        if id is not None:
            return self._area_1s[id]
        else:
            return self._area_1s

    def area_2(self, id=None):
        if id is not None:
            return self._area_2s[id]
        else:
            return self._area_2s

    def includes_pedestrian(self, id=None):
        if id is not None:
            return self._includes_pedestrian[id]
        else:
            return self._includes_pedestrian

class Earthquake:
    def __init__(self, year, starting_month=None, ending_month=None):
        self._year = year
        self._starting_momth = starting_month
        self._ending_month = ending_month
        self._get_range()
        self._read_csv_file()
        self._get_data()

    def _get_range(self):
        with open(TRACKING_JSON_PATH) as file:
            tracking_data = json.load(file)
            starting_year = tracking_data["csv"]["earthquake"]["starting_year"]
        ending_year = datetime.now().year
        if (type(self._year) != int or (self._year < starting_year or self._year > ending_year)):
            message = f"Invalid year. Must be an integer between {starting_year} and {ending_year} (including)."
            raise InvalidRangeError(message)
        check_if_month_is_valid(self._starting_momth)
        check_if_month_is_valid(self._ending_month)

        # Initialize starting month
        if not self._starting_momth:
            self._starting_momth = 1
        # Initialize ending month
        if self._year == datetime.now().year:
            if self._starting_momth >= datetime.now().month:
                message = "Invalid range. Cannot find data in this range."
                raise InvalidRangeError(message)
            if not self._ending_month:
                self._ending_month = datetime.now().month - 1
                if self._ending_month == 0:
                    message = "Invalid range. Cannot find data in this range."
                    raise InvalidRangeError(message)
        else:
            if not self._ending_month:
                self._ending_month = 12
        if self._starting_momth > self._ending_month:
            message = "Invalid range. Parameter 'starting_month' must be equal to or smaller than 'ending_month'."
            raise InvalidRangeError(message)

    def _read_csv_file(self):
        path = f".\data\earthquakes\earthquake_{self._year}年.csv"
        dtype_mapping = {
            "Date": str,
            "Time": str,
            "北緯": float,
            "東經": float,
            "芮氏規模": float,
            "深度": float,
            "城市": str,
            "震度": str
        }
        self._df = pd.read_csv(path, engine='python', encoding="big5", dtype=dtype_mapping)


    def _get_data(self):
        self._dates = [datetime.strptime(d, "%Y-%m-%d") for d in self._df["Date"]]
        self.starting_index = self.ending_index = 0
        starting_flag = True
        for date in self._dates:
            if starting_flag:
                if date.month == self._starting_momth:
                    starting_flag = False
                else:
                    self.starting_index += 1
            if date.month == self._ending_month + 1:
                break
            self.ending_index += 1
        self.size = self.ending_index - self.starting_index

        self._dates = self._df["Date"][self.starting_index: self.ending_index]
        self._times = self._df["Time"][self.starting_index: self.ending_index]
        for i in range(self.starting_index, self.ending_index):
            self._dates[i] = datetime.strptime(self._dates[i], "%Y-%m-%d").date()
            self._times[i] = datetime.strptime(self._times[i], "%H:%M:%S").time()
        self._latitudes = self._df["北緯"][self.starting_index: self.ending_index]
        self._longitudes = self._df["東經"][self.starting_index: self.ending_index]
        self._magnitudes = self._df["芮氏規模"][self.starting_index: self.ending_index]
        self._depths = self._df["深度"][self.starting_index: self.ending_index]
        self._areas = self._df["城市"][self.starting_index: self.ending_index]
        self._intensities = self._df["震度"][self.starting_index: self.ending_index]
        for i in range(self.starting_index, self.ending_index):
            if len(self._intensities[i]) != 1:
                self._intensities[i] = self._intensities[i].replace(" ", "")
            else:
                self._intensities[i] += "級"

    def date(self, id=None):
        if id is None:
            return self._dates
        else:
            return self._dates[id]

    def time(self, id=None):
        if id is None:
            return self._times
        else:
            return self._times[id]

    def latitude(self, id=None):
        if id is None:
            return self._latitudes
        else:
            return self._latitudes[id]

    def longitude(self, id=None):
        if id is None:
            return self._longitudes
        else:
            return self._longitudes[id]

    def magnitude(self, id=None):
        if id is None:
            return self._magnitudes
        else:
            return self._magnitudes[id]

    def depth(self, id=None):
        if id is None:
            return self._depths
        else:
            return self._depths[id]

    def area(self, id=None):
        if id is None:
            return self._areas
        else:
            return self._areas[id]

    def intensity(self, id=None):
        if id is None:
            return self._intensities
        else:
            return self._intensities[id]

class SQLController:
    """This class is used to control 'db.sqlites' by using sqlite3 module."""

    PATH = r"..\.\db.sqlite3"
    def __init__(self, table_name):
        self.table_name = table_name
        self.conn = sqlite3.connect(SQLController.PATH)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def select(self, id=None, column=None):
        if id:
            if column:
                sql = f"SELECT {column} FROM {self.table_name} WHERE id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()[0]
            else:
                sql = f"SELECT * FROM {self.table_name} WHERE id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()
        else:
            if column:
                sql = f"SELECT {column} FROM {self.table_name}"
            else:
                sql = f"SELECT * FROM {self.table_name}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def select_from_coordinate(self, latitude, longitude):
        sql = f"""SELECT * FROM {self.table_name}
                WHERE latitude={latitude} AND longitude={longitude}"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if data:
            return data
        else:
            return None

class TrafficAccidentSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_traffic_accident"
        super().__init__(self.table_name)

    def new(self, latitude, longitude, fatality, injury, includes_pedestrian):
        coordinate = Coordinate(latitude, longitude)
        self.existing_id = self.coordinate_id(coordinate.latitude_grid,
                                              coordinate.longitude_grid)
        total_fatality = fatality
        total_injury = injury
        if includes_pedestrian:
            pedestrian_fatality = fatality
            pedestrian_injury = injury
        else:
            pedestrian_fatality = pedestrian_injury = 0

        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            total_fatality += self.select(self.existing_id, "total_fatality")
            total_injury += self.select(self.existing_id, "total_injury")
            pedestrian_fatality += self.select(self.existing_id, "pedestrian_fatality")
            pedestrian_injury += self.select(self.existing_id, "pedestrian_injury")
            sql = f"""UPDATE {self.table_name}
                        SET number = {number},
                        total_fatality = {total_fatality},
                        total_injury = {total_injury},
                        pedestrian_fatality = {pedestrian_fatality},
                        pedestrian_injury = {pedestrian_injury}
                        WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (latitude, longitude, number,
                        total_fatality, total_injury, pedestrian_fatality,
                        pedestrian_injury) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (coordinate.latitude_grid,
                                      coordinate.longitude_grid,
                                      1, total_fatality, total_injury,
                                      pedestrian_fatality, pedestrian_injury))
        self.conn.commit()

    def coordinate_id(self, latitude, longitude):
        sql = f"""SELECT * FROM {self.table_name}
                    WHERE latitude = {latitude} AND longitude = {longitude}"""
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class PedestrianHellSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_pedestrian_hell"
        super().__init__(self.table_name)

    def new(self, area_1, area_2,
            fatality, injury, includes_pedestrian):
        total_fatality = fatality
        total_injury = injury
        if includes_pedestrian:
            pedestrian_fatality = fatality
            pedestrian_injury = injury
        else:
            pedestrian_fatality = pedestrian_injury = 0

        self.existing_id = self.administrative_area_id(area_1,
                                                       area_2)
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            total_fatality += self.select(self.existing_id, "total_fatality")
            total_injury += self.select(self.existing_id, "total_injury")
            pedestrian_fatality += self.select(self.existing_id, "pedestrian_fatality")
            pedestrian_injury += self.select(self.existing_id, "pedestrian_injury")
            sql = f"""UPDATE {self.table_name}
                    SET number = {number},
                    total_fatality = {total_fatality},
                    total_injury = {total_injury},
                    pedestrian_fatality = {pedestrian_fatality},
                    pedestrian_injury = {pedestrian_injury} WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (
                    area_1,
                    area_2,
                    number,
                    total_fatality,
                    total_injury,
                    pedestrian_fatality,
                    pedestrian_injury) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (area_1,
                                      area_2,
                                      1, total_fatality, total_injury,
                                      pedestrian_fatality, pedestrian_injury))
        self.conn.commit()

    def administrative_area_id(self, area_1, area_2):
        sql = f"""SELECT * FROM {self.table_name}
                    WHERE area_1 = '{area_1}'
                    AND area_2 = '{area_2}'"""
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class EarthquakeSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_earthquake"
        super().__init__(self.table_name)

    def new(self, date, time, latitude, longitude, magnitude, depth):
        sql = f"""INSERT INTO {self.table_name} (
                date, time, latitude, longitude,
                magnitude, depth) VALUES (?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(sql, (date, str(time), latitude, longitude, magnitude, depth))
        self.conn.commit()

class EarthquakeIntensitySQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_earthquake_intensity"
        super().__init__(self.table_name)

    def new(self, area, intensity):
        self.existing_id = self.area_id(area)
        if self.existing_id:
            number = self.select(self.existing_id, "number")
            avg_pga = self.select(self.existing_id, "pga")
            total_pga = avg_pga * number + risk.intensity_to_pga(intensity)
            number += 1
            avg_pga = total_pga / number
            avg_intensity = risk.pga_to_intensity(avg_pga)
            sql = f"""UPDATE {self.table_name} SET number = {number},
                    intensity = '{avg_intensity}', pga = {avg_pga}
                    WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (area, number, intensity,
                    pga) VALUES (?, ?, ?, ?)"""
            pga = risk.intensity_to_pga(intensity)
            self.cursor.execute(sql, (area, 1, intensity, pga))
        self.conn.commit()

    def area_id(self, area):
        sql = f"SELECT * FROM {self.table_name} WHERE area = '{area}'"
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        if data:
            return data[0]
        else:
            return None

class UpdateTrafficAccidentData:
    def __init__(self):
        self.get_tracking_data()
        self.determine_range()
        self.update_data()
        self.update_tracking_data()

    def get_tracking_data(self):
        with open(TRACKING_JSON_PATH) as file:
            self.tracking_data = json.load(file)
            self.starting_year = self.tracking_data["csv"]["car_accident"]["starting_year"]
            self.ending_year = self.tracking_data["csv"]["car_accident"]["ending_year"]
            self.tracking_year = self.tracking_data["sqlite3"]["traffic_accident"]["tracking_year"]
            self.tracking_month = self.tracking_data["sqlite3"]["traffic_accident"]["tracking_month"]
            self.tracking_rank = self.tracking_data["sqlite3"]["traffic_accident"]["tracking_rank"]

    def initialize_range(self):
        if not self.tracking_year:
            self.tracking_year = self.starting_year
        if not self.tracking_month:
            self.tracking_month = 0
        if not self.tracking_rank:
            self.tracking_rank = 1

    def determine_range(self):
        self.initialize_range()
        if self.tracking_rank == 1:
            if self.tracking_month == 0:
                self.tracking_month = 12
            elif self.tracking_month == 12:
                self.tracking_rank = 2
                self.tracking_month = 0
        if self.tracking_rank == 2:
            if self.tracking_month == 12:
                self.tracking_year += 1
                self.tracking_rank = 1
            else:
                self.tracking_month += 1

    def update_data(self):
        self.accident = CarAccident(year=self.tracking_year,
                                    month=self.tracking_month,
                                    rank=self.tracking_rank)
        self.traffic_controller = TrafficAccidentSQLController()
        self.ped_hell_controller = PedestrianHellSQLController()
        self.number_of_data = len(self.accident.data)
        for i in range(self.number_of_data):
            latitude = self.accident.latitude(i)
            longitude = self.accident.longitude(i)
            fatality = self.accident.fatality(i)
            injury = self.accident.injury(i)
            area_1 = self.accident.area_1(i)
            area_2 = self.accident.area_2(i)
            includes_pedestrian = self.accident.includes_pedestrian(i)
            self.traffic_controller.new(latitude, longitude,
                                        fatality, injury, includes_pedestrian)
            self.ped_hell_controller.new(area_1, area_2,
                                         fatality, injury, includes_pedestrian)
        self.traffic_controller.close()
        self.ped_hell_controller.close()

    def update_tracking_data(self):
        self.tracking_data["sqlite3"]["traffic_accident"]["tracking_year"] = self.tracking_year
        self.tracking_data["sqlite3"]["traffic_accident"]["tracking_month"] = self.tracking_month
        self.tracking_data["sqlite3"]["traffic_accident"]["tracking_rank"] = self.tracking_rank
        with open(TRACKING_JSON_PATH, 'w') as file:
            json.dump(self.tracking_data, file)

class UpdateEarthquakeData:
    def __init__(self):
        self.get_tracking_data()
        self.update_data()

    def get_tracking_data(self):
        with open(TRACKING_JSON_PATH) as file:
            self.tracking_data = json.load(file)
            starting_year = self.tracking_data["csv"]["earthquake"]["starting_year"]
            self.tracking_year = self.tracking_data["sqlite3"]["earthquake"]["tracking_year"]
            self.starting_month = self.tracking_data["sqlite3"]["earthquake"]["tracking_month"]

        if not self.tracking_year:
            self.tracking_year = starting_year
        if not self.starting_month:
            self.starting_month = 0
        elif self.starting_month == 12:
            self.starting_month = 0
            self.tracking_year += 1

        if self.tracking_year == datetime.now().year:
            self.starting_month += 1
            self.ending_month = datetime.now().month - 1
        else:
            self.ending_month = 12

    def update_data(self):
        try:
            if self.tracking_year == datetime.now().year:
                self.earthquake = Earthquake(year=self.tracking_year,
                                             starting_month=self.starting_month,
                                             ending_month=self.ending_month)
            else:
                self.earthquake = Earthquake(self.tracking_year)
        except:
            return
        self.earthquake_controller = EarthquakeSQLController()
        self.earthquake_intensity_controller = EarthquakeIntensitySQLController()
        self.number_of_data = self.earthquake.size
        check_date = check_time = 0
        for index in range(self.earthquake.starting_index, self.earthquake.ending_index):
            date = self.earthquake.date(index)
            time = self.earthquake.time(index)
            latitude = self.earthquake.latitude(index)
            longitude = self.earthquake.longitude(index)
            magnitude = self.earthquake.magnitude(index)
            depth = self.earthquake.depth(index)
            area = self.earthquake.area(index)
            intensity = self.earthquake.intensity(index)

            self.earthquake_intensity_controller.new(area, intensity)
            if check_date == date and check_time == time:
                continue
            else:
                self.earthquake_controller.new(date, time, latitude, longitude, magnitude, depth)
                check_date = date
                check_time = time

        self.earthquake_controller.close()
        self.earthquake_intensity_controller.close()
        self.update_tracking_data()

    def update_tracking_data(self):
        self.tracking_data["sqlite3"]["earthquake"]["tracking_year"] = self.tracking_year
        self.tracking_data["sqlite3"]["earthquake"]["tracking_month"] = self.ending_month
        with open(TRACKING_JSON_PATH, 'w') as file:
            json.dump(self.tracking_data, file)


def test_Coordinate():
    coordinate = (23.05, 120.19)
    coord = Coordinate(coordinate)
    print(coord.earthquake.data)
    print(coord.earthquake.magnitude)
    # coordinate = (23.6865, 120.4114)
    # coord = Coordinate(coordinate)
    # print(coord.traffic_accident.data)
    # print(coord.traffic_accident.id)
    pass

def test_CarAccident():
    accident = CarAccident(year=111, month=2, rank=2)
    # print(accident.date())
    # print(accident.time())
    # print(accident.latitude())
    # print(accident.longitude())
    # print(accident.fatality())
    # print(accident.injury())
    # print(accident.area_1())
    # print(accident.area_2())
    # print(accident.includes_pedestrian())
    # print(accident.includes_pedestrian().sum())
    # data_id = 1
    # print(accident.date(data_id))
    # print(accident.time(data_id))
    # print(accident.latitude(data_id))
    # print(accident.longitude(data_id))
    # print(accident.fatality(data_id))
    # print(accident.injury(data_id))
    # print(accident.area_1(data_id))
    # print(accident.area_2(data_id))
    pass

def test_TrafficAccident():
    controller = TrafficAccidentSQLController()
    test_latitude = 24.4389
    test_longitude = 118.2497
    print(controller.coordinate_id(test_latitude, test_longitude))
    print(controller.coordinate_id(test_latitude+50, test_longitude))
    print(controller.select(50956, "total_injury"))
    pass

def test_Earthquake():
    year = 2024
    starting_momth = 2
    ending_month = None
    earthquke = Earthquake(year, starting_momth, ending_month)
    # print(earthquke.date())
    print(earthquke.time())
    # print(earthquke.area())
    # controller = EarthquakeIntensitySQLController()
    # area = "地球"
    # intensity = "5弱"
    # controller.new(area, intensity)
    pass

if __name__ == "__main__":
    # test_Coordinate()
    test_CarAccident()
    # test_TrafficAccident()
    # test_Earthquake()
    pass


