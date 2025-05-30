import requests
import json
from bs4 import BeautifulSoup
import csv
import random
import time
import pandas as pd
from random import uniform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from selenium.webdriver.support.ui import Select

import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
]

# URL untuk mengunduh gambar
base_url = "http://mesonet.k-state.edu/metadata/"
base_url_img = "http://mesonet.k-state.edu"



CSV_FILENAME = "Kansas State University-Rocky Ford.csv"

FIELDNAMES = [
            "Station Name",
            "Station Type",
            "SHEF ID",
            "Normals Stn"
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

    browser.refresh()
    time.sleep(2)

    return browser





def extract_station_data_table(soup):
# def extract_station_data_table(soup, state_name):
    infographic_tab_content = soup.find("div", id="infographic-tab-content")
    if not infographic_tab_content:
        return {}, None

    # Ekstrak data dari tabel
    table = infographic_tab_content.find("table", id="station-data")
    data_infographic = {}
    if table:
        rows = table.find_all("tr")[1:]  # Lewati header
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                measurement = cols[0].get_text(strip=True)
                sensor = cols[1].get_text(strip=True)
                data_infographic[measurement] = sensor

    # infographic_tab_content = soup.find("div", id="infographic-tab-content")
    # if not infographic_tab_content:
    #     return {}, None
        
    station_info = {}
    station_info_content = soup.find("div", id="station-info")
    if station_info_content:
        station_table = station_info_content.find("table", id="leftTable")
        # print("history_table", history_table)
        if station_table:
            station_rows = station_table.find_all("tr")  # jangan skip dulu
            for row_stat in station_rows:
                station_cols = row_stat.find_all("td")
                # print(">> Kolom:", [col.get_text(strip=True) for col in history_cols])  # debug
                if len(station_cols) >= 2:
                    station_history_measurement = station_cols[0].get_text(strip=True)
                    station_history_sensor = station_cols[1].get_text(strip=True)
                    station_info[station_history_measurement] = station_history_sensor



    meta_data = {
        "station_info": station_info
    }
    return meta_data



def open_to_website(browser):
    url = "http://mesonet.k-state.edu/metadata/"
    # base_url = "http://mesonet.k-state.edu/metadata/"
    browser.get(url)
    time.sleep(5)
    select_element = browser.find_element(By.ID, "station-select")
    select = Select(select_element)

    options = select.options

    start_index = None
    for i, option in enumerate(options):
        if option.text.strip() == "Ashland 8S":
            start_index = i
            break

    if start_index is None:
        print(f"❌ Option dengan text {option} tidak ditemukan.")
        return

    print(f"✅ Mulai dari index {start_index}: {options[start_index].text.strip()}")

    # Mulai iterasi dari Hamilton
    for option in options[start_index:]:
        value = option.get_attribute("value")

        
        state_text = option.text.strip()

        if not value:
            continue  # Lewati opsi kosong

        print(f"➡️ Memilih: {state_text} ({value})")
        select.select_by_value(value)

        time.sleep(2)  # Tambahkan WebDriverWait jika butuh tunggu update halaman

        # Ambil HTML baru
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # format_meta_data = extract_station_data_table(soup, state_name=state_text)
        format_meta_data = extract_station_data_table(soup)
        # image_file = extract_station_data_table(soup, base_url=url, state_name=state_text)

        print("🛰️  Data Station Instrumentation:")
        # meta_data_json = json.dumps(format_meta_data, indent=4, ensure_ascii=False)
        # print(meta_data_json)
        
        normals_Stn = format_meta_data.get('station_info').get('Normals Stn:') if format_meta_data.get("station_info") else " "
               

        data = {
            "Station Name": state_text,
            "Station Type": format_meta_data.get("station_info").get("Station Type:") if format_meta_data.get("station_info") else " ",
            "SHEF ID":  format_meta_data.get("station_info").get("SHEF ID:") if format_meta_data.get("station_info") else " ",
            "Normals Stn": normals_Stn
        }



        # # Folder untuk menyimpan gambar
        # folder_name = "ID------Image Station Kansas State University"
        # os.makedirs(folder_name, exist_ok=True)

        # # Ambil semua gambar
        # for container in soup.select('.containerThumb'):
        #     img = container.find('img')
        #     overlay = container.select_one('.overlay .text')

        #     if img and overlay:
        #         direction = overlay.get_text(strip=True)
        #         print(direction)
        #         img_src = img['src']

        #         # Buat nama file baru
        #         new_filename = f"{normals_Stn}.jpg"
        #         filepath = os.path.join(folder_name, new_filename)

        #         # Gabungkan dengan base URL jika perlu
        #         full_url = img_src
        #         if img_src.startswith("/"):
        #             full_url = base_url_img + img_src

        #         # Unduh dan simpan gambar
        #         try:
        #             response = requests.get(full_url)
        #             response.raise_for_status()
        #             with open(filepath, "wb") as f:
        #                 f.write(response.content)
        #             print(f"✅ Gambar '{new_filename}' berhasil disimpan.")
        #         except Exception as e:
        #             print(f"❌ Gagal menyimpan {new_filename}: {e}")

        # Folder untuk menyimpan gambar
        folder_name = "ID------Image Station Kansas State University"
        os.makedirs(folder_name, exist_ok=True)

        # Ambil hanya gambar pertama
        for container in soup.select('.containerThumb'):
            img = container.find('img')
            overlay = container.select_one('.overlay .text')

            if img and overlay:
                direction = overlay.get_text(strip=True)
                print(direction)
                img_src = img['src']

                # Buat nama file baru
                new_filename = f"{normals_Stn}.jpg"
                filepath = os.path.join(folder_name, new_filename)

                # Gabungkan dengan base URL jika perlu
                full_url = img_src
                if img_src.startswith("/"):
                    full_url = base_url_img + img_src

                # Unduh dan simpan gambar
                try:
                    response = requests.get(full_url)
                    response.raise_for_status()
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Gambar '{new_filename}' berhasil disimpan.")
                except Exception as e:
                    print(f"❌ Gagal menyimpan {new_filename}: {e}")

                break  # <--- Tambahkan ini agar hanya gambar pertama yang disimpan


        save_station_data(data)  # 💾 Simpan langsung
        print(f"✅ Data Station Name {state_text} berhasil diproses.")
        # print("🖼️  Path gambar:", image_file if image_file else "❌ Gagal ambil gambar")

        time.sleep(2)




def main():
    browser = setup_browser()
    open_to_website(browser)
    time.sleep(5)
    browser.quit()

if __name__ == "__main__":
    main()
