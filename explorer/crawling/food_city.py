from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
class CrawlingFoods():
    def __init__(self, city):
        self.driver = webdriver.Chrome()
        self.city = city
        self.get_urls_from_page()
        self.crawling_pages()
        self.driver.quit()
        
    def get_urls_from_page(self):
        self.urls = []
        for i in range(1, 8):
            if i == 1:
                url = f"https://ifoodie.tw/explore/{self.city}/list?sortby=popular"
            else:
                url = f"https://ifoodie.tw/explore/{self.city}/list?sortby=popular&page={i}"
        
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                soup = BeautifulSoup(r.text, 'html.parser')
                hrefs = soup.find_all('a', class_='jsx-320828271 title-text')
                for h in hrefs:
                    self.urls.append(f'https://ifoodie.tw{h.get("href")}')
               

    def crawling_pages(self):
        self.data = []
        for url in self.urls:
            self.data.append(self.get_json_from_web(url))

    def get_json_from_web(self, url):
        self.driver.get(url)
        # 使用显式等待，等待 <script id="__NEXT_DATA__"> 出现
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//script[@id='__NEXT_DATA__']"))
        )
        # 获取 <script id="__NEXT_DATA__"> 中的内容
        script_element = self.driver.find_element(By.XPATH, "//script[@id='__NEXT_DATA__']")
        script_content = script_element.get_attribute("innerHTML")
        # 解析 JSON 数据
        return json.loads(script_content)

    def write_to_csv(self):
        # 转换数据为 DataFrame
        df = pd.DataFrame([self.extract_data(Restaurant(data)) for data in self.data])
        
        dtype_mapping = {
            "name": str,
            "Longtitude": float,
            "Latitude": float,
            "area_1": str,
            "area_2": str,
            "address": str,
            "phone":str,
            "opening_hours_all":list,
            "rating":float,
            "avg_price":int
        }

        # 将数据写入 CSV 文件
        df.to_csv(f"{self.city}.csv", index=False, dtype=dtype_mapping ,encoding='utf-8-sig')

    def extract_data(self, restaurant):
        # 提取 Restaurant 对象的数据为字典
        return {
            "name": restaurant.name,
            "latitude": restaurant.latitude,
            "longitude": restaurant.longitude,
            "area_1": restaurant.area_1,
            "area_2": restaurant.area_2,
            "address": restaurant.address,
            "phone": restaurant.phone,
            "opening_hours_all": restaurant.opening_hours.all,
            "rating": restaurant.rating,
            "avg_price": restaurant.avg_price
        }

class Restaurant:
    def __init__(self, json_data):
        data = json_data["props"]["initialState"]["restaurants"]["restaurantInfo"]
        self.name = data.get("name")
        self.latitude = data.get("lat")
        self.longitude = data.get("lng")
        self.area_1 = data.get("city")
        self.area_2 = data.get("adminName")
        self.address = data.get("address")
        self.phone = str(data.get("phone"))  # 将 phone 转换为字符串
        self.opening_hours = Week(data.get("openingHoursList"))
        self.rating = data.get("rating")
        self.avg_price = data.get("avgPrice")

class Week:
    def __init__(self, weeks):
        # 使用 try-except 处理可能的索引错误
        try:
            self.all = weeks
            self.mon = weeks[0] if len(weeks) > 0 else ""
            self.tue = weeks[1] if len(weeks) > 1 else ""
            self.wed = weeks[2] if len(weeks) > 2 else ""
            self.thu = weeks[3] if len(weeks) > 3 else ""
            self.fri = weeks[4] if len(weeks) > 4 else ""
            self.sat = weeks[5] if len(weeks) > 5 else ""
            self.sun = weeks[6] if len(weeks) > 6 else ""
        except IndexError:
            self.all = []
            self.mon = ""
            self.tue = ""
            self.wed = ""
            self.thu = ""
            self.fri = ""
            self.sat = ""
            self.sun = ""

if __name__ == "__main__":
    city = "台北市"  # 示例城市
    food = CrawlingFoods(city)
    food.write_to_csv()