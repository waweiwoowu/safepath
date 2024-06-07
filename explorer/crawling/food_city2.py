import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
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
        # 使用顯式等待，等待 <script id="__NEXT_DATA__"> 出現
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//script[@id='__NEXT_DATA__']"))
        )
        # 獲取 <script id="__NEXT_DATA__"> 中的內容
        script_element = self.driver.find_element(By.XPATH, "//script[@id='__NEXT_DATA__']")
        script_content = script_element.get_attribute("innerHTML")
        # 解析 JSON 數據
        json_data = json.loads(script_content)
        return json_data, url  # 返回JSON數據和URL

    def write_to_csv(self):
        # 轉換數據為 DataFrame
        df = pd.DataFrame([self.extract_data(Restaurant(data), url) for data, url in self.data])
        
        # 將數據寫入 CSV 文件
        df.to_csv(f"./data/food/{self.city}.csv", index=False, encoding='utf-8-sig')

    def extract_data(self, restaurant, url):
        # 提取 Restaurant 對象的數據為字典
        image_path = self.download_image(url, restaurant.name)
        return {
            "name": restaurant.name,
            "latitude": restaurant.latitude,
            "longitude": restaurant.longitude,
            "area_1": restaurant.area_1,
            "area_2": restaurant.area_2,
            "address": restaurant.address,
            "phone": self.format_phone_number(restaurant.phone),  # 使用格式化函數
            "opening_hours_all": restaurant.opening_hours.all,
            "rating": restaurant.rating,
            "avg_price": restaurant.avg_price,
            "image": image_path
        }

    def download_image(self, url, title):
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            soup = BeautifulSoup(r.text, 'html.parser')
            image_url = soup.find('img', itemprop='image').get('src')
            valid_filename = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_')).rstrip()
            image_filename = valid_filename + '.jpg'
            
            # 設定資料夾路徑
            folder_path = r"../static/images/hotspots/food_image"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # 下載圖片
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # 設定圖片檔案路徑
                image_path = os.path.join(folder_path, image_filename)
                # 將圖片寫入檔案
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                # 回傳圖片路徑
                return image_path
            else:
                print("無法下載圖片")
                return None
        else:
            print("無法訪問網址")
            return None
    
    def format_phone_number(self, phone):
        phone = str(phone)
        if phone.startswith("0"):  # 區域號碼
            if len(phone) == 10:  # 假設區域碼和號碼總長度為10
                return f"{phone[:2]}-{phone[2:]}"
            else:
                return f"{phone[:3]}-{phone[3:]}"
        else:
            return phone

class Restaurant:
    def __init__(self, json_data):
        data = json_data["props"]["initialState"]["restaurants"]["restaurantInfo"]
        self.name = data.get("name")
        self.latitude = data.get("lat")
        self.longitude = data.get("lng")
        self.area_1 = data.get("city")
        self.area_2 = data.get("adminName")
        self.address = data.get("address")
        self.phone = str(data.get("phone"))  # 將 phone 轉換為字符串
        self.opening_hours = Week(data.get("openingHoursList"))
        self.rating = data.get("rating")
        self.avg_price = data.get("avgPrice")

class Week:
    def __init__(self, weeks):
        # 使用 try-except 處理可能的索引錯誤
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
    # city = "台北市"
    # city = "新北市"
    # city = "桃園市"
    # city = "台中市"
    # city = "台南市"
    # city = "高雄市"
    # city = "新竹縣"
    # city = "彰化縣"
    # city = "雲林縣"
    # city = "嘉義縣"
    # city = "屏東縣"
    # city = "宜蘭縣"
    # city = "花蓮縣"
    # city = "台東縣"
    # city = "澎湖縣"
    # city = "金門縣"
    # city = "基隆市"
    city = "新竹市"
    # city = "嘉義市"
    food = CrawlingFoods(city)
    food.write_to_csv()

