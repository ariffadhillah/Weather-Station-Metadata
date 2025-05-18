from bs4 import BeautifulSoup
import csv
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from selenium.webdriver.support.ui import Select

import os
from bs4 import BeautifulSoup

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
]



CSV_FILENAME = "Kansas State University.csv"

FIELDNAMES = [
            "Station Name",
            "Station Type",
            "SHEF ID",
            "Normals Stn",                
            "County",
            "Nearest City",
            "Latitude",
            "Longitude",
            "Elevation",
            "Last maintenance",
            "Air Temperature (2m)",
            "Air Temperature (10m)",
            "Barometer",
            "Precipitation",
            "Soil Moisture (2in)",
            "Soil Moisture (4in)",
            "Soil Moisture (8in)",
            "Soil Moisture (16in)",
            "Soil Temperature (2in)",
            "Soil Temperature (4in)",
            "Solar Sensor",
            "WindSpeed/Direction (2m)",
            "WindSpeed/Direction (10m)",
]

def save_station_data(row, filename=CSV_FILENAME):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        
        writer.writerow(row)
        file.flush()




def setup_browser():
    """setup browser and User-Agent randomly"""
    chrome_options = Options()

    user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"user-agent={user_agent}")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")

    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()

    browser = Driver(uc=True)
    url = "http://mesonet.k-state.edu/metadata/"
    browser.uc_open_with_reconnect(url, 1)
    browser.uc_gui_click_captcha()
    browser.maximize_window()




    select_element = browser.find_element(By.ID, "station-select")
    select = Select(select_element)

    options = select.options

    start_index = None
    for i, option in enumerate(options):
        if option.text.strip() == "Hamilton":
            start_index = i
            break

    if start_index is None:
        print("❌ Option dengan text 'Hamilton' tidak ditemukan.")
        return

    print(f"✅ Mulai dari index {start_index}: {options[start_index].text.strip()}")

    # Mulai iterasi dari Hamilton
    for option in options[start_index:]:
        value = option.get_attribute("value")
        label = option.text.strip()

        if not value:
            continue  # Lewati opsi kosong

        print(f"➡️ Memilih: {label} ({value})")
        select.select_by_value(value)

        time.sleep(2)  # Tambahkan WebDriverWait jika butuh tunggu update halaman

        # Tambahkan logika untuk scraping atau ekstraksi data di sini


    # browser.refresh()
    time.sleep(2)









def main():
    browser = setup_browser()
    time.sleep(5)
    browser.quit()

if __name__ == "__main__":
    main()
