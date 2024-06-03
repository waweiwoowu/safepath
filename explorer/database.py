import json
import math
import sqlite3
import pandas as pd
from datetime import datetime


DEGREE_DIFFERENCE = 0.0001

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

class InvalidCarAccidentError(Exception):
    def __init__(self, message="Invalid."):
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
        
        path = r".\data\tracking.json"
        with open(path) as file:
            data = json.load(file)
            starting_year = data["car_accident"]["starting_year"]
            ending_year = data["car_accident"]["ending_year"]
        if (type(self._year) != int or (self._year < starting_year or self._year > ending_year)):
            message = f"Invalid year. Must be an integer between {starting_year} and {ending_year} (including)."
            raise InvalidCarAccidentError(message)
        if self._month:
            if type(self._month) != int or (self._month < 1 or self._month > 12):
                message = "Invalid mouth. Must be an integer between 1 and 12 (including)."
                raise InvalidCarAccidentError(message)

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
            raise InvalidCarAccidentError(message)

    def _get_data(self):
        """This method is used to take the data of interest"""
        
        self._dates = [datetime.strptime(str(int(d)), "%Y%m%d").strftime("%Y-%m-%d") for d in self._df["發生日期"]]
        self._times = [datetime.strptime(str(int(t)).zfill(6), "%H%M%S").strftime("%H:%M:%S") for t in self._df["發生時間"]]
        self._longitudes = self._df["經度"]
        self._latitudes = self._df["緯度"]
        self._casualties = self._df["死亡受傷人數"]
        self._fatalities = [int(c[2]) for c in self._casualties]
        self._injuries = [int(c[-1]) for c in self._casualties]
        self._location = self._df["發生地點"]
        self._administrative_area_level_1 = [loc[:3] for loc in self._location]
        self._administrative_area_level_2 = [loc[3:6] for loc in self._location]
        # Check if the third character of the string is not one of "鄉", "鎮", "市", or "區"
        for i in range(len(self._administrative_area_level_2)):
            if self._administrative_area_level_2[i][2] not in "鄉鎮市區":
                # If the condition is met, truncate the string to the first two characters
                self._administrative_area_level_2[i] = self._administrative_area_level_2[i][:2]
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
                    self._administrative_area_level_1[i],
                    self._administrative_area_level_2[i],
                    self._includes_pedestrian[i]
                ])
        self.data = pd.DataFrame(self._data, columns=[
            "date",
            "time",
            "latitude",
            "longitude",
            "fatality",
            "injury",
            "administrative_area_level_1",
            "administrative_area_level_2",
            "includes_pedestrian"
        ])
        self._dates = self.data.iloc[:, 0]
        self._times = self.data.iloc[:, 1]
        self._latitudes = self.data.iloc[:, 2]
        self._longitudes = self.data.iloc[:, 3]
        self._fatalities = self.data.iloc[:, 4]
        self._injuries = self.data.iloc[:, 5]
        self._administrative_area_level_1s = self.data.iloc[:, 6]
        self._administrative_area_level_2s = self.data.iloc[:, 7]
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

    def administrative_area_level_1(self, id=None):
        if id is not None:
            return self._administrative_area_level_1s[id]
        else:
            return self._administrative_area_level_1s

    def administrative_area_level_2(self, id=None):
        if id is not None:
            return self._administrative_area_level_2s[id]
        else:
            return self._administrative_area_level_2s
    
    def includes_pedestrian(self, id=None):
        if id is not None:
            return self._includes_pedestrian[id]
        else:
            return self._includes_pedestrian
                
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
                sql = f"SELECT {column} FROM {self.table_name} where id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()[0]
            else:
                sql = f"SELECT * FROM {self.table_name} where id={id}"
                self.cursor.execute(sql)
                return self.cursor.fetchone()
        else:
            sql = "SELECT * FROM {self.table_name}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

class TrafficAccidentSQLController(SQLController):
    def __init__(self):
        self.table_name = "risk_traffic_accident"
        super().__init__(self.table_name)

    def new(self, latitude, longitude, fatality, injury):
        coordinate = Coordinate(latitude, longitude)
        self.existing_id = self.coordinate_id(coordinate.latitude_grid, 
                                              coordinate.longitude_grid)
        if self.existing_id:
            number = self.select(self.existing_id, "number") + 1
            fatality += self.select(self.existing_id, "fatality")
            injury += self.select(self.existing_id, "injury")
            sql = f"""UPDATE {self.table_name} 
                        SET number = {number}, fatality = {fatality}, injury = {injury} 
                        WHERE id = {self.existing_id}"""
            self.cursor.execute(sql)
        else:
            sql = f"""INSERT INTO {self.table_name} (latitude, longitude, number, 
                        fatality, injury) VALUES (?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (coordinate.latitude_grid, 
                                      coordinate.longitude_grid, 
                                      1, fatality, injury))
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

    def new(self, administrative_area_level_1, administrative_area_level_2, 
            fatality, injury, includes_pedestrian):
        total_fatality = fatality
        total_injury = injury
        if includes_pedestrian:
            pedestrian_fatality = fatality
            pedestrian_injury = injury
        else:
            pedestrian_fatality = pedestrian_injury = 0
            
        self.existing_id = self.administrative_area_id(administrative_area_level_1, 
                                                       administrative_area_level_2)
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
                    administrative_area_level_1, 
                    administrative_area_level_2, 
                    number, 
                    total_fatality, 
                    total_injury, 
                    pedestrian_fatality, 
                    pedestrian_injury) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            self.cursor.execute(sql, (administrative_area_level_1, 
                                      administrative_area_level_2, 
                                      1, total_fatality, total_injury,
                                      pedestrian_fatality, pedestrian_injury))
        self.conn.commit()
    
    def administrative_area_id(self, administrative_area_level_1, administrative_area_level_2):
        sql = f"""SELECT * FROM {self.table_name} 
                    WHERE administrative_area_level_1 = '{administrative_area_level_1}' 
                    AND administrative_area_level_2 = '{administrative_area_level_2}'"""
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
        self.tracking_path = r".\data\tracking.json"
        with open(self.tracking_path) as file:
            self.tracking_data = json.load(file)
            self.starting_year = self.tracking_data["car_accident"]["starting_year"]
            self.ending_year = self.tracking_data["car_accident"]["ending_year"]
            self.tracking_year = self.tracking_data["car_accident_density"]["tracking_year"]
            self.tracking_month = self.tracking_data["car_accident_density"]["tracking_month"]
            self.tracking_rank = self.tracking_data["car_accident_density"]["tracking_rank"]
    
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
            area_level_1 = self.accident.administrative_area_level_1(i)
            area_level_2 = self.accident.administrative_area_level_2(i)
            includes_pedestrian = self.accident.includes_pedestrian(i)
            self.traffic_controller.new(latitude, longitude, fatality, injury)
            self.ped_hell_controller.new(area_level_1, area_level_2, 
                                         fatality, injury, includes_pedestrian)
        self.traffic_controller.close()
        self.ped_hell_controller.close()
        
    def update_tracking_data(self):
        self.tracking_data["car_accident_density"]["tracking_year"] = self.tracking_year
        self.tracking_data["car_accident_density"]["tracking_month"] = self.tracking_month
        self.tracking_data["car_accident_density"]["tracking_rank"] = self.tracking_rank
        with open(self.tracking_path, 'w') as file:
            json.dump(self.tracking_data, file)
        

def test_CarAccident():
    accident = CarAccident(year=111, month=2, rank=2)
    # print(accident.date())
    # print(accident.time())
    # print(accident.latitude())
    # print(accident.longitude())
    # print(accident.fatality())
    # print(accident.injury())
    # print(accident.administrative_area_level_1())
    print(accident.administrative_area_level_2())
    # print(accident.includes_pedestrian())
    # print(accident.includes_pedestrian().sum())
    # data_id = 1
    # print(accident.date(data_id))
    # print(accident.time(data_id))
    # print(accident.latitude(data_id))
    # print(accident.longitude(data_id))
    # print(accident.fatality(data_id))
    # print(accident.injury(data_id))
    # print(accident.administrative_area_level_1(data_id))
    # print(accident.administrative_area_level_2(data_id))
    # for i in range(200):
    #     print(accident.administrative_area_level_2(i))

def test_SQLController():
    controller = TrafficAccidentSQLController()
    test_latitude = 24.4389
    test_longitude = 118.2497
    print(controller.coordinate_id(test_latitude, test_longitude))
    print(controller.coordinate_id(test_latitude+50, test_longitude))
    print(controller.select(50956, "total_injury"))
    # controller.new(test_latitude, test_longitude, 55, 66)
    # print(controller.select(50956))
    # controller.new(test_latitude, test_longitude, 99, 77)
    # print(controller.select(50956))
    # controller.new(test_latitude+50, test_longitude+20, 55, 123)
    controller.close()


if __name__ == "__main__":
    test_CarAccident()
    # test_SQLController()
    pass
    

