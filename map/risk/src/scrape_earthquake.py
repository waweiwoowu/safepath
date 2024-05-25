import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import threading

from django.core.management.base import BaseCommand
from risk.models import Earthquake

class Command(BaseCommand):
    help = 'Scrape earthquake data and store it in the database'

    def __init__(self):
        super().__init__()
        self.driver = None
        self.url = "https://scweb.cwa.gov.tw/zh-tw/earthquake/data"
        self.lock = threading.Lock()

    @staticmethod
    def date_and_time(date, time):
        o_year = int(date[:3]) + 1911
        date = str(o_year) + date[3:]
        date_original = datetime.strptime(date, "%Y年%m月%d日")
        ad_date = date_original.strftime("%Y-%m-%d")
        time_original = datetime.strptime(time, "%H時%M分%S秒")
        iso_time = time_original.strftime("%H:%M:%S")
        return ad_date, iso_time

    def until_location(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "table_next")))
            self.stdout.write("讀取完畢")
        except Exception as e:
            self.stderr.write(f"讀取失敗: {e}")
            self.driver.quit()

    def load_data(self):
        try:
            self.driver = webdriver.Chrome()
            self.driver.get(self.url)
            self.driver.maximize_window()
            self.until_location()
            self.driver.find_element(By.ID, "Search").click()
            year = self.driver.find_element(By.CSS_SELECTOR, "div.datepicker-months th.datepicker-switch").text

            if year == "2024":
                month = self.driver.find_elements(By.CSS_SELECTOR, "div.datepicker-months span.month")
                for i in range(len(month)):
                    if i != 0:
                        self.driver.find_element(By.ID, "Search").click()
                        sleep(3)
                        month = self.driver.find_elements(By.CSS_SELECTOR, "div.datepicker-months span.month")
                    month[i].click()
                    sleep(3)

                    while True:
                        try:
                            table = self.driver.find_element(By.ID, "table").text
                            if "沒有匹配結果" in table:
                                return
                        except NoSuchElementException:
                            pass

                        links = self.driver.find_elements(By.CSS_SELECTOR, "td.d-lg-none>a")
                        threads = []
                        for link in links:
                            thread = threading.Thread(target=self.process_link, args=(link,))
                            thread.start()
                            threads.append(thread)

                        for thread in threads:
                            thread.join()

                        next_button = self.driver.find_element(By.ID, "table_next")
                        if "paginate_button page-item next disabled" in next_button.get_attribute("class"):
                            self.stdout.write("已到最後一頁，停止抓取。")
                            break
                        else:
                            next_button.click()
                        sleep(3)
        except StaleElementReferenceException as e:
            self.stderr.write(f"捕獲到異常: {e}")
        except Exception as e:
            self.stderr.write(f"發生其他異常: {e}")
        finally:
            self.driver.quit()

    def process_link(self, link):
        try:
            if link.get_attribute("href") == "javascript:void(0);":
                link.click()
                new_url = self.driver.current_url
            else:
                new_url = link.get_attribute("href")
            sleep(0.1)
            r = requests.get(new_url)
            soup = BeautifulSoup(r.text, "html.parser")
            self.parse_and_store_data(soup)
        except Exception as e:
            self.stderr.write(f"處理鏈接時發生錯誤: {e}")

    def parse_and_store_data(self, soup):
        li_first = soup.select_one("ul.eqResultBoxRight.BulSet.BkeyinList > li")
        date = li_first.find_next_sibling("li")
        earthquake_date = date.text.split("發震時間：")[1].split("日")[0].strip() + "日"
        earthquake_time = date.text.split("日")[1].strip("\n").strip(" ")
        ddate, time = self.date_and_time(earthquake_date, earthquake_time)

        location = date.find_next_sibling("li")
        deep = location.find_next_sibling("li")
        scale = deep.find_next_sibling("li")

        latitude = location.text.split("北緯 ")[1].split("°")[0].strip(" ")
        longitude = location.text.split("東經 ")[1].split("°")[0].strip(" ")
        depth = deep.text.split("地震深度：")[1].split(" 公里")[0].replace("\n", "")
        scale_value = scale.text.split("芮氏規模：\n")[1].strip("\n")
        masonrys = soup.select("div#masonry a.eqResultLevelOpen")
        for masonry in masonrys:
            city = masonry.text.split("地區")[0]
            level = masonry.text.split("震度")[1].split("級")[0].strip(" ")
            if "強" in level:
                level = masonry.text.split("震度")[1].split("強")[0].strip(" ")
            elif "弱" in level:
                level = masonry.text.split("震度")[1].split("弱")[0].strip(" ")
            else:
                level = masonry.text.split("震度")[1].split("級")[0].strip(" ")

            with self.lock:
                if not Earthquake.objects.filter(date=ddate, time=time, city=city).exists():
                    Earthquake.objects.create(
                        date=ddate, time=time, latitude=latitude, longitude=longitude,
                        depth=depth, scale=scale_value, city=city, level=level
                    )

    def handle(self, *args, **kwargs):
        self.load_data()
        self.stdout.write("Update finished.")
