import pandas as pd


class attractions:
    def __init__(self,rank):

        self._rank = rank
        self._df = pd.DataFrame()
        self._read_csv_file()
        self._get_data()


    def _read_csv_file(self):
        """This method is used to read and get data from the csv files."""

        dtype_mapping = {
            "title": str,
            "address": str,
            "Longtitude": float,
            "Latitude": float,
            "area_1": str,
            "area_2": str,
            "image": str
        }
        if self._rank == 1 or self._rank == 2 or self._rank == 3:
            path = f"./data/hotspots/Taiwan_attractions_{self._rank}.csv"
            self._df = pd.read_csv(path, dtype=dtype_mapping, low_memory=False)
        else:
            message = "Invalid rank. Must be either 1,2,3."
            # raise InvalidRangeError(message)

    def _get_data(self):
        """This method is used to take the data of interest"""

        # self._dates = [datetime.strptime(str(int(d)), "%Y%m%d").strftime("%Y-%m-%d") for d in self._df["發生日期"]]
        # self._times = [datetime.strptime(str(int(t)).zfill(6), "%H%M%S").strftime("%H:%M:%S") for t in self._df["發生時間"]]
        self._title = self._df["title"]
        self._image = self._df["image"]
        self._latitudes = self._df["Latitude"]
        self._longitudes = self._df["Longtitude"]
        # self._casualties = self._df["死亡受傷人數"]
        # self._fatalities = [int(c[2]) for c in self._casualties]
        # self._injuries = [int(c[-1]) for c in self._casualties]
        self._address = self._df["address"]
        self._area_1 = self._df["area_1"]
        self._area_2 = self._df["area_2"]
        # self._area_2 = [loc[3:7] for loc in self._address]
        # # Check if the third character of the string is not one of "鄉", "鎮", "市", or "區"
        # for i in range(len(self._area_2)):
        #     if self._area_2[i][2] not in "鄉鎮市區":
        #         if self._area_2[i][1] in "鄉鎮市區":
        #             # If the condition is met, truncate the string to the first two characters
        #             self._area_2[i] = self._area_2[i][:2]
        #     else:
        #         self._area_2[i] = self._area_2[i][:3]

        self._reorganize_data()

    def _reorganize_data(self):
        """This method is used to take out the duplicated data"""

        check = 0
        longitude_check = 0
        latitude_check = 0
        self._data = []
        for i in range(len(self._title)):
            if self._title[i] == check:
                if (self._longitudes[i] == longitude_check) and (self._latitudes[i] == latitude_check):
                    continue
                else:
                    longitude_check = self._longitudes[i]
                    latitude_check = self._latitudes[i]
            else:
                check = self._title[i]
                self._data.append([
                    self._title[i],
                    self._image[i],
                    self._latitudes[i],
                    self._longitudes[i],
                    self._address[i],
                    self._area_1[i],
                    self._area_2[i],
                ])
        self.data = pd.DataFrame(self._data, columns=[
            "title",
            "image",
            "latitude",
            "longitude",
            "address",
            "area_1",
            "area_2",
        ])
        self._titles = self.data.iloc[:, 0]
        self._images = self.data.iloc[:, 1]
        self._latitudes = self.data.iloc[:, 2]
        self._longitudes = self.data.iloc[:, 3]
        self._addresies = self.data.iloc[:, 4]
        self._area_1s = self.data.iloc[:, 5]
        self._area_2s = self.data.iloc[:, 6]

    def title(self, id=None):
        if id is not None:
            return self._titles[id]
        else:
            return self._titles

    def image(self, id=None):
        if id is not None:
            return self._images[id]
        else:
            return self._images

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
    
    def address(self,id=None):
        if id is not None:
            return self._addresies[id]
        else:
            return self._addresies
    
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
if __name__ == "__main__":
    rank = 1
    attraction_data = attractions(rank)

    print("Title:", attraction_data.title(10))
    print("Image:", attraction_data.image(10))
    print("Latitude:", attraction_data.latitude(10))
    print("Longitude:", attraction_data.longitude(10))
    print("Address:", attraction_data.address(10))
    print("Area 1:", attraction_data.area_1(10))
    print("Area 2:", attraction_data.area_2(10))