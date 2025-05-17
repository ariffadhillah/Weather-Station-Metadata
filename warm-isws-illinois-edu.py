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

    browser.refresh()
    time.sleep(2)

    return browser





def extract_station_data_table(soup, base_url, state_name, save_folder="Image Station Instrumentation Kansas State University"):
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

    history_data = {}
    history_tab_content = soup.find("div", id="history-tab-content")
    if history_tab_content:
        history_table = history_tab_content.find("table", id="history-table")
        # print("history_table", history_table)
        if history_table:
            history_rows = history_table.find_all("tr")  # jangan skip dulu
            for row in history_rows:
                history_cols = row.find_all("td")
                # print(">> Kolom:", [col.get_text(strip=True) for col in history_cols])  # debug
                if len(history_cols) >= 2:
                    history_measurement = history_cols[0].get_text(strip=True)
                    history_sensor = history_cols[1].get_text(strip=True)
                    history_data[history_measurement] = history_sensor


    sponsors_data = {}
    sponsors_tab_content = soup.find("div", id="sponsors-tab-content")
    if sponsors_tab_content:
        sponsors_table = sponsors_tab_content.find("table", id="sponsor-table")
        # print("sponsors_table", sponsors_table)
        if sponsors_table:
            sponsors_rows = sponsors_table.find_all("tr")  # jangan skip dulu
            for row in sponsors_rows:
                sponsors_cols = row.find_all("td")
                # print(">> Kolom:", [col_.get_text(strip=True) for col_ in sponsors_cols])
                if len(sponsors_cols) >= 2:
                    sponsors_measurement = sponsors_cols[0].get_text(strip=True)
                    sponsors_sensor = sponsors_cols[1].get_text(strip=True)
                    sponsors_data[sponsors_measurement] = sponsors_sensor



    

    # Ekstrak dan simpan gambar
    image_tag = infographic_tab_content.find("img", id="infographicPic")
    image_path = None
    if image_tag and image_tag.get("src"):
        img_src = image_tag["src"]
        full_img_url = urljoin(base_url, img_src)
        print("Gambar URL:", full_img_url)

        os.makedirs(save_folder, exist_ok=True)
        # Bersihkan nama file dari karakter ilegal
        clean_state_name = ''.join(c for c in state_name if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"{clean_state_name} Station Instrumentation.jpg"
        image_path = os.path.join(save_folder, filename)

        try:
            response = requests.get(full_img_url)
            if response.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(response.content)
            else:
                print(f"Gagal download gambar untuk {state_name}: HTTP {response.status_code}")
                image_path = None
        except Exception as e:
            print(f"Gagal mengunduh gambar untuk {state_name}: {e}")
            image_path = None

    # # return data_infographic, image_path, history_data, sponsors_data 

    meta_data = {
        "station_info": station_info,
        "infographic": data_infographic,
        "history": history_data,
        "sponsors": sponsors_data
    }
    # return meta_data
    return meta_data, image_path



def open_to_website(browser):
    url = "http://mesonet.k-state.edu/metadata/"
    # base_url = "http://mesonet.k-state.edu/metadata/"
    browser.get(url)
    time.sleep(5)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    select_element = soup.find("select", id="station-select")

    if not select_element:
        print("Gagal menemukan <select> dengan id 'station-select'")
        return

    state_options = [
        (opt.get("value"), opt.text.strip())
        for opt in select_element.find_all("option")
        if opt.get("value")
    ]

    print(f"✅ Total state unik dalam form: {len(state_options)}")

    wait = WebDriverWait(browser, 5)

    for index, (state_val, state_text) in enumerate(state_options):
        print(f"\n➡️ [{index + 1}] Memilih state: {state_text}")

        browser.get(url)
        wait.until(EC.presence_of_element_located((By.ID, "station-select")))
        time.sleep(2)

        # Pilih state via JavaScript
        browser.execute_script(f"""
            let select = document.getElementById('station-select');
            select.value = '{state_val}';
            select.dispatchEvent(new Event('change'));
        """)
        time.sleep(5)  # Tunggu konten berubah

        # Ambil HTML baru
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # image_data = []

        # for container in soup.select('.containerThumb'):
        #     img = container.find('img')
        #     overlay_text = container.select_one('.overlay .text')

        #     if img and overlay_text:
        #         direction = overlay_text.get_text(strip=True)

        #         # Nama file hasil akhir
        #         new_filename = f"{state_text}-{direction}.jpg"

        #         # Simpan data
        #         image_data.append({
        #             "direction": direction,
        #             "original_src": img['src'],
        #             "new_name": new_filename
        #         })

        # # Tampilkan hasil
        # for item in image_data:
        #     print(f"{item['direction']}: {item['original_src']} → {item['new_name']}")


        # Folder untuk menyimpan gambar
        folder_name = "Image Station Kansas State University"
        os.makedirs(folder_name, exist_ok=True)

        # Ambil semua gambar
        for container in soup.select('.containerThumb'):
            img = container.find('img')
            overlay = container.select_one('.overlay .text')

            if img and overlay:
                direction = overlay.get_text(strip=True)
                img_src = img['src']

                # Buat nama file baru
                new_filename = f"{state_text}-{direction}.jpg"
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

        # format_meta_data = extract_station_data_table(soup, base_url=url, state_name=state_text)
        format_meta_data, image_file = extract_station_data_table(soup, base_url=url, state_name=state_text)

        print("🛰️  Data Station Instrumentation:")
        # meta_data_json = json.dumps(format_meta_data, indent=4, ensure_ascii=False)
        # print(meta_data_json)
               

        data = {
            "Station Name": state_text,
            "Station Type": format_meta_data.get("station_info").get("Station Type:") if format_meta_data.get("station_info") else " ",
            "SHEF ID":  format_meta_data.get("station_info").get("SHEF ID:") if format_meta_data.get("station_info") else " ",
            "Normals Stn": format_meta_data.get('station_info').get('Normals Stn:') if format_meta_data.get("station_info") else " ",                
            "County": format_meta_data.get("station_info").get("County:") if format_meta_data.get("station_info") else " ",
            "Nearest City": format_meta_data.get("station_info").get("Nearest City:") if format_meta_data.get("station_info") else " ",
            "Latitude": f"'{format_meta_data.get('station_info').get('Latitude:')}" if format_meta_data.get("station_info") else " ",
            "Longitude": f"'{format_meta_data.get('station_info').get('Longitude:')}" if format_meta_data.get("station_info") else " ",
            "Elevation": f"'{format_meta_data.get('station_info').get('Elevation:')}" if format_meta_data.get("station_info") else " ",
            "Last maintenance": f"'{format_meta_data.get('station_info').get('Established:')}" if format_meta_data.get("station_info") else " ",
            "Air Temperature (2m)": format_meta_data.get("infographic").get("Air Temperature (2m)") if format_meta_data.get("infographic") else " ",
            "Air Temperature (10m)": format_meta_data.get("infographic").get("Air Temperature (10m)") if format_meta_data.get("infographic") else " ",
            "Barometer": format_meta_data.get("infographic").get("Barometer") if format_meta_data.get("infographic") else " ",
            "Precipitation": format_meta_data.get("infographic").get("Precipitation") if format_meta_data.get("infographic") else " ",
            "Soil Moisture (2in)": format_meta_data.get("infographic").get("Soil Moisture (2in)") if format_meta_data.get("infographic") else " ",
            "Soil Moisture (4in)": format_meta_data.get("infographic").get("Soil Moisture (4in)") if format_meta_data.get("infographic") else " ",
            "Soil Moisture (8in)": format_meta_data.get("infographic").get("Soil Moisture (8in)") if format_meta_data.get("infographic") else " ",
            "Soil Moisture (16in)": format_meta_data.get("infographic").get("Soil Moisture (16in)") if format_meta_data.get("infographic") else " ",
            "Soil Temperature (2in)": f"'{format_meta_data.get('infographic').get('Soil Temperature (2in)')}" if format_meta_data.get("infographic") else " ",
            "Soil Temperature (4in)": f"'{format_meta_data.get('infographic').get('Soil Temperature (4in)')}" if format_meta_data.get("infographic") else " ",
            "Solar Sensor": format_meta_data.get("infographic").get("Solar Sensor") if format_meta_data.get("infographic") else " ",
            "WindSpeed/Direction (2m)": format_meta_data.get("infographic").get("WindSpeed/Direction (2m)") if format_meta_data.get("infographic") else " ",
            "WindSpeed/Direction (10m)": format_meta_data.get("infographic").get("WindSpeed/Direction (10m)") if format_meta_data.get("infographic") else " ",
        }
        for key, value in data.items():
            if value:
                print(f"{key}: {value}")
            else:
                print(f"{key}: Data tidak tersedia")
                print("")
                print("")

        save_station_data(data)  # 💾 Simpan langsung
        print(f"✅ Data Station Name {state_text} berhasil diproses.")
        print("🖼️  Path gambar:", image_file if image_file else "❌ Gagal ambil gambar")

        time.sleep(2)




def main():
    browser = setup_browser()
    open_to_website(browser)
    time.sleep(5)
    browser.quit()

if __name__ == "__main__":
    main()
