import threading
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

lock = threading.Lock()

# 轉換爬取之日期及時間格式
def Date_and_Time(date, time):
    o_year = int(date[:3]) + 1911
    date = str(o_year) + date[3:]
    date_original = datetime.strptime(date, "%Y年%m月%d日")
    ad_date = date_original.strftime("%Y-%m-%d")
    time_original = datetime.strptime(time, "%H時%M分%S秒")
    iso_time = time_original.strftime("%H:%M:%S")
    return ad_date, iso_time

# 等待網頁讀取完畢
def untilLocation(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "table_next")))
        print("讀取完畢")
    except:
        print("讀取失敗")
        driver.quit()

# 爬取年份區間
def years_range(input_year):
    return list(range(1995, input_year+1))

# 爬取地震網站
def scrape_data(year, existing_data=None):
    Date, Time, Latitude, Longitude, Depth, Magnitude, Area, Intensity = [], [], [], [], [], [], [], []

    try:
        driver = webdriver.Chrome()
        url = "https://scweb.cwa.gov.tw/zh-tw/earthquake/data"
        driver.get(url)
        driver.maximize_window()
        untilLocation(driver)
        driver.find_element(By.ID, "Search").click()
        year_text = driver.find_element(By.CSS_SELECTOR, "div.datepicker-months th.datepicker-switch").text
        while year_text != str(year):
            driver.find_element(By.CSS_SELECTOR, "div.datepicker-months th.prev").click()
            year_text = driver.find_element(By.CSS_SELECTOR, "div.datepicker-months th.datepicker-switch").text

        months = driver.find_elements(By.CSS_SELECTOR, "div.datepicker-months span.month")
        for i in range(len(months)):
            if i == 0:
                months[i].click()
                sleep(3)
            else:
                driver.find_element(By.ID,"Search").click()
                print("b")
                sleep(3)
                months = driver.find_elements(By.CSS_SELECTOR,"div.datepicker-months span.month")
                months[i].click()
                print("c")
                sleep(3)
            print(f"Scraping {year} month {i + 1}")

            while True:
                try:
                    table = driver.find_element(By.ID, "table").text
                    if "沒有匹配結果" in table:
                        break
                except:
                    pass
                # 得到每日地震的網址
                links = driver.find_elements(By.CSS_SELECTOR, "td.d-lg-none>a")
                for link in links:
                    if link.get_attribute("href") == "javascript:void(0);":
                        link.click()
                        new_url = driver.current_url
                    else:
                        new_url = link.get_attribute("href")
                    # 開始爬取資料
                    r = requests.get(new_url)
                    soup = BeautifulSoup(r.text, "html.parser")
                    li_first = soup.select_one("ul.eqResultBoxRight.BulSet.BkeyinList > li")
                    date = li_first.find_next_sibling("li")
                    earthquake_date = date.text.split("發震時間：")[1].split("日")[0].strip() + "日"
                    earthquake_time = date.text.split("日")[1].strip("\n").strip(" ")
                    ddate, time = Date_and_Time(earthquake_date, earthquake_time)

                    location = date.find_next_sibling("li")
                    deep = location.find_next_sibling("li")
                    scale = deep.find_next_sibling("li")
                    latitude = location.text.split("北緯 ")[1].split("°")[0].strip(" ")
                    longitude = location.text.split("東經 ")[1].split("°")[0].strip(" ")
                    depth = deep.text.split("地震深度：")[1].split(" 公里")[0].replace("\n", "")
                    magnitude = scale.text.split("芮氏規模：\n")[1].strip("\n")
                    masonrys = soup.select("div#masonry a.eqResultLevelOpen")
                    for masonry in masonrys:
                        area = masonry.text.split("地區")[0]
                        intensity = masonry.text.split("震度")[1].split("級")[0].strip(" ")
                        # 按照順序放進list
                        with lock:
                            Date.append(ddate)
                            Time.append(time)
                            Latitude.append(latitude)
                            Longitude.append(longitude)
                            Depth.append(depth)
                            Magnitude.append(magnitude)
                            Area.append(area)
                            Intensity.append(intensity)
                # 下一頁
                next_button = driver.find_element(By.ID, "table_next")
                if "paginate_button page-item next disabled" in next_button.get_attribute("class"):
                    break
                else:
                    next_button.click()
                sleep(3)

        # 按照年份，存成新的data
        new_data = {"Date": Date, "Time": Time, "北緯": Latitude, "東經": Longitude, "深度": Depth, "芮氏規模": Magnitude, "城市": Area, "震度": Intensity}
        new_df = pd.DataFrame(new_data)
        # 假設無舊的年份的數據，則直接儲存為新年份的csv，否則將原csv檔與新data合併
        if existing_data is not None:
            update_df = pd.concat([existing_data, new_data]).drop_duplicates().reset_index(drop=True)
            update_df.to_csv(f".\data\earthquakes\earthquake_{year}年.csv", encoding="Big5", index=False)
        else:
            new_df.to_csv(f".\data\earthquakes\earthquake_{year}年.csv", encoding="Big5", index=False)
        driver.quit()
    except StaleElementReferenceException as e:
        print("捕獲到異常:", e)
    except Exception as e:
        print("發生其他異常:", e)

# 讀取指定年份的地震資料的 CSV 檔案，如果檔案存在就讀取，否則返回 None
def read_csv(year):
    if os.path.exists(f".\data\earthquakes\earthquake_{year}年.csv"):
        return pd.read_csv(f"earthquake_{year}年.csv")
    else:
        return None

# 進入點,使用threading多工同時爬取每一年份之數據
def earthquake_crawling():
    years = years_range(input(eval("請輸入年份:")))
    last_year = max(years)
    existing_data = read_csv(last_year)
    threads = []
    for year in years:
        if year == last_year:
            thread = threading.Thread(target=scrape_data, args=(year,existing_data))
        else:
            thread = threading.Thread(target=scrape_data, args=(year,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# 測試環境，進入點為main()方法
if __name__ == "__main__":
    earthquake_crawling()
