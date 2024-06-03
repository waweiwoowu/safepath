import pandas as pd
from datetime import datetime


class Earthquake:
    def __init__(self, year):
        self._year = year
        self._df = pd.read_csv(f".\data\earthquakes\earthquake_{self._year}年.csv", engine='python', encoding="big5")
        self._get_data()
        self._reorganize_data()
        
    def _get_data(self):
        self._dates = [datetime.strptime(d, "%Y-%m-%d") for d in self._df["Date"]]
        if self._year == datetime.now().year:
            self.size = 0
            for date in self._dates:
                if date.month == datetime.now().month:
                    self._dates = self._dates[:self.size]
                    break
                self.size += 1
        else:
            self.size = len(self._df)
        
        self._times = [datetime.strptime(t, "%H:%M:%S").time() for t in self._df["Time"]][:self.size]
        self._latitudes = self._df["北緯"][:self.size]
        self._longitudes = self._df["東經"][:self.size]
        self._magnitudes = self._df["芮氏規模"][:self.size]
        self._depths = self._df["深度"][:self.size]
        self._cities = self._df["城市"][:self.size]
        self._intensities = self._df["震度"][:self.size]
        for i in range(self.size):
            if len(self._intensities[i]) != 1:
                self._intensities[i] = self._intensities[i].replace(" ", "")
            else:
                self._intensities[i] += "級"
                
    def _reorganize_data(self):
        data = []
        for i in range(self.size):
            data.append([
                self._dates[i],
                self._times[i],
                self._latitudes[i],
                self._longitudes[i],
                self._magnitudes[i],
                self._depths[i],
                self._cities[i],
                self._intensities[i]
            ])
        self.data = pd.DataFrame(data, columns=[
            "date",
            "time",
            "latitude",
            "longitude",
            "magnitude",
            "depth",
            "city",
            "intensity"
        ])

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
        
    def city(self, id=None):
        if id is None:
            return self._cities
        else:
            return self._cities[id]

    def intensity(self, id=None):
        if id is None:
            return self._intensities
        else:
            return self._intensities[id]
        

if __name__ == "__main__":
    year = 2024
    earthquake = Earthquake(year)
    # data = earthquake.data
    # print(data)
    # for in_id in range(len(earthquake.date())):
        # print(earthquake.date(in_id))
        # print(earthquake.time(in_id))
        # print(earthquake.latitude(in_id))
        # print(earthquake.longitude(in_id))
        # print(earthquake.depth(in_id))
        # print(earthquake.magnitude(in_id))
        # print(earthquake.area(in_id))
        # print(earthquake.intensity(in_id))
    