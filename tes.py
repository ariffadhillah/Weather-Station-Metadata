# from bs4 import BeautifulSoup
# import csv
# import random
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from seleniumbase import Driver
# from selenium.webdriver.support.ui import Select

# import os
# from bs4 import BeautifulSoup

# user_agents = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
# ]



# CSV_FILENAME = "Kansas State University.csv"

# FIELDNAMES = [
#             "Station Name",
#             "Station Type",
#             "SHEF ID",
#             "Normals Stn",                
#             "County",
#             "Nearest City",
#             "Latitude",
#             "Longitude",
#             "Elevation",
#             "Last maintenance",
#             "Air Temperature (2m)",
#             "Air Temperature (10m)",
#             "Barometer",
#             "Precipitation",
#             "Soil Moisture (2in)",
#             "Soil Moisture (4in)",
#             "Soil Moisture (8in)",
#             "Soil Moisture (16in)",
#             "Soil Temperature (2in)",
#             "Soil Temperature (4in)",
#             "Solar Sensor",
#             "WindSpeed/Direction (2m)",
#             "WindSpeed/Direction (10m)",
# ]

# def save_station_data(row, filename=CSV_FILENAME):
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
#         writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
#         if not file_exists or os.stat(filename).st_size == 0:
#             writer.writeheader()
        
#         writer.writerow(row)
#         file.flush()




# def setup_browser():
#     """setup browser and User-Agent randomly"""
#     chrome_options = Options()

#     user_agent = random.choice(user_agents)
#     chrome_options.add_argument(f"user-agent={user_agent}")

#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument("--disable-infobars")
#     chrome_options.add_argument("start-maximized")
#     chrome_options.add_argument("--disable-extensions")

#     browser = webdriver.Chrome(options=chrome_options)
#     browser.maximize_window()

#     browser = Driver(uc=True)
#     url = "http://mesonet.k-state.edu/metadata/"
#     browser.uc_open_with_reconnect(url, 1)
#     browser.uc_gui_click_captcha()
#     browser.maximize_window()

#     browser.refresh()
#     time.sleep(2)

#     return browser





# def extract_station_data_table(soup):
#     infographic_tab_content = soup.find("div", id="infographic-tab-content")
#     if not infographic_tab_content:
#         return {}, None

#     # Ekstrak data dari tabel
#     table = infographic_tab_content.find("table", id="station-data")
#     data_infographic = {}
#     if table:
#         rows = table.find_all("tr")[1:]  # Lewati header
#         for row in rows:
#             cols = row.find_all("td")
#             if len(cols) == 2:
#                 measurement = cols[0].get_text(strip=True)
#                 sensor = cols[1].get_text(strip=True)
#                 data_infographic[measurement] = sensor


#     station_info = {}
#     station_info_content = soup.find("div", id="station-info")
#     if station_info_content:
#         station_table = station_info_content.find("table", id="leftTable")
#         if station_table:
#             station_rows = station_table.find_all("tr")  
#             for row_stat in station_rows:
#                 station_cols = row_stat.find_all("td")
#                 if len(station_cols) >= 2:
#                     station_history_measurement = station_cols[0].get_text(strip=True)
#                     station_history_sensor = station_cols[1].get_text(strip=True)
#                     station_info[station_history_measurement] = station_history_sensor


#     meta_data = {
#         "station_info": station_info,
#         "infographic": data_infographic
#     }
#     # return meta_data
#     return meta_data





# def open_to_website(browser):
#     url = "http://mesonet.k-state.edu/metadata/"
#     browser.get(url)
#     time.sleep(5)

#     # soup = BeautifulSoup(browser.page_source, "html.parser")
#     # select_element = soup.find("select", id="station-select")

#     # if not select_element:
#     #     print("Gagal menemukan <select> dengan id 'station-select'")
#     #     return

#     # state_options = [
#     #     (opt.get("value"), opt.text.strip())
#     #     for opt in select_element.find_all("option")
#     #     if opt.get("value")
#     # ]

#     # print(f"✅ Total state unik dalam form: {len(state_options)}")

#     # wait = WebDriverWait(browser, 5)

#     # for index, (state_val, state_text) in enumerate(state_options):
#     #     print(f"\n➡️ [{index + 1}] Memilih state: {state_text}")

#     #     browser.get(url)
#     #     wait.until(EC.presence_of_element_located((By.ID, "station-select")))

#     #     try:
#     #         select_element = Select(browser.find_element(By.ID, "station-select"))
#     #         select_element.select_by_value(state_val)
#     #     except Exception as e:
#     #         print(f"❌ Gagal memilih state {state_text}: {e}")
#     #         continue
#     #     time.sleep(3)

#     # Temukan elemen <select> berdasarkan ID
#     select_element = browser.find_element(By.ID, "station-select")

#     # Buat objek Select
#     select = Select(select_element)

#     # Ambil semua opsi
#     options = select.options

#     print(f"Total opsi: {len(options)}")

#     # Lewati index 0 jika itu placeholder seperti "Choose station..."
#     for i, option in enumerate(options):
#         value = option.get_attribute("value")
#         state_text = option.text.strip()

#         if not value:
#             continue  # Lewati jika <option value=""> (biasanya placeholder)

#         print(f"➡️ [{i}] Memilih: {state_text}")

#         # Pilih option berdasarkan value
#         select.select_by_value(value)

#         # Tunggu sedikit agar halaman update (kalau ada aksi setelah pilih)
#         time.sleep(2)


#         soup = BeautifulSoup(browser.page_source, "html.parser")
#         format_meta_data = extract_station_data_table(soup)
  
#         data = {
#             "Station Name": state_text,
#             "Station Type": format_meta_data.get("station_info").get("Station Type:") if format_meta_data.get("station_info") else " ",
#             "SHEF ID":  format_meta_data.get("station_info").get("SHEF ID:") if format_meta_data.get("station_info") else " ",
#             "Normals Stn": format_meta_data.get('station_info').get('Normals Stn:') if format_meta_data.get("station_info") else " ",                
#             "County": format_meta_data.get("station_info").get("County:") if format_meta_data.get("station_info") else " ",
#             "Nearest City": format_meta_data.get("station_info").get("Nearest City:") if format_meta_data.get("station_info") else " ",
#             "Latitude": f"'{format_meta_data.get('station_info').get('Latitude:')}" if format_meta_data.get("station_info") else " ",
#             "Longitude": f"'{format_meta_data.get('station_info').get('Longitude:')}" if format_meta_data.get("station_info") else " ",
#             "Elevation": f"'{format_meta_data.get('station_info').get('Elevation:')}" if format_meta_data.get("station_info") else " ",
#             "Last maintenance": f"'{format_meta_data.get('station_info').get('Established:')}" if format_meta_data.get("station_info") else " ",
#             "Air Temperature (2m)": format_meta_data.get("infographic").get("Air Temperature (2m)") if format_meta_data.get("infographic") else " ",
#             "Air Temperature (10m)": format_meta_data.get("infographic").get("Air Temperature (10m)") if format_meta_data.get("infographic") else " ",
#             "Barometer": format_meta_data.get("infographic").get("Barometer") if format_meta_data.get("infographic") else " ",
#             "Precipitation": format_meta_data.get("infographic").get("Precipitation") if format_meta_data.get("infographic") else " ",
#             "Soil Moisture (2in)": format_meta_data.get("infographic").get("Soil Moisture (2in)") if format_meta_data.get("infographic") else " ",
#             "Soil Moisture (4in)": format_meta_data.get("infographic").get("Soil Moisture (4in)") if format_meta_data.get("infographic") else " ",
#             "Soil Moisture (8in)": format_meta_data.get("infographic").get("Soil Moisture (8in)") if format_meta_data.get("infographic") else " ",
#             "Soil Moisture (16in)": format_meta_data.get("infographic").get("Soil Moisture (16in)") if format_meta_data.get("infographic") else " ",
#             "Soil Temperature (2in)": f"'{format_meta_data.get('infographic').get('Soil Temperature (2in)')}" if format_meta_data.get("infographic") else " ",
#             "Soil Temperature (4in)": f"'{format_meta_data.get('infographic').get('Soil Temperature (4in)')}" if format_meta_data.get("infographic") else " ",
#             "Solar Sensor": format_meta_data.get("infographic").get("Solar Sensor") if format_meta_data.get("infographic") else " ",
#             "WindSpeed/Direction (2m)": format_meta_data.get("infographic").get("WindSpeed/Direction (2m)") if format_meta_data.get("infographic") else " ",
#             "WindSpeed/Direction (10m)": format_meta_data.get("infographic").get("WindSpeed/Direction (10m)") if format_meta_data.get("infographic") else " ",
#         }

#         save_station_data(data) 
#         print(f"✅ Data Station Name {state_text} berhasil diproses.")
#         time.sleep(2)


# def main():
#     browser = setup_browser()
#     open_to_website(browser)
#     time.sleep(5)
#     browser.quit()

# if __name__ == "__main__":
#     main()




import os
import csv
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

# Constants
base_url = "http://mesonet.k-state.edu/metadata/"
base_url_img = "http://mesonet.k-state.edu/metadata/"
CSV_FILENAME = "Kansas State University-Oskaloosa 1SE----.csv"
FOLDER_IMAGE = "Image Station Instrumentation Kansas State University"

FIELDNAMES = [
    "Station Name", "Station Type", "SHEF ID", "Normals Stn", "County", "Nearest City",
    "Latitude", "Longitude", "Elevation", "Last maintenance",
    "Air Temperature (2m)", "Air Temperature (10m)", "Barometer", "Precipitation",
    "Soil Moisture (2in)", "Soil Moisture (4in)", "Soil Moisture (8in)", "Soil Moisture (16in)",
    "Soil Temperature (2in)", "Soil Temperature (4in)", "Solar Sensor",
    "WindSpeed/Direction (2m)", "WindSpeed/Direction (10m)"
]

# Membuat folder penyimpanan gambar
os.makedirs(FOLDER_IMAGE, exist_ok=True)

# Fungsi menyimpan baris ke CSV
def save_station_data(row):
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not file_exists or os.stat(CSV_FILENAME).st_size == 0:
            writer.writeheader()
        writer.writerow(row)

# Setup Selenium Chrome tanpa headless
def setup_browser():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # HAPUS agar browser terbuka
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Ekstrak data dan gambar stasiun
def extract_station_data_table(soup, state_name):
    station_info = {}
    infographic_data = {}
    image_path = None

    info_div = soup.find("div", id="station-info")
    table = info_div.find("table", id="leftTable") if info_div else None
    if table:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 2:
                station_info[tds[0].get_text(strip=True)] = tds[1].get_text(strip=True)

    infographic_div = soup.find("div", id="infographic-tab-content")
    if infographic_div:
        table = infographic_div.find("table", id="station-data")
        if table:
            for tr in table.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) == 2:
                    infographic_data[tds[0].get_text(strip=True)] = tds[1].get_text(strip=True)

        img_tag = infographic_div.find("img", id="infographicPic")
        if img_tag and img_tag.get("src"):
            img_url = urljoin(base_url_img, img_tag["src"])
            filename = f"{state_name.replace('/', '-').replace(' ', '_')}.jpg"
            image_path = os.path.join(FOLDER_IMAGE, filename)
            try:
                r = requests.get(img_url, timeout=10)
                if r.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(r.content)
                    print(f"🖼️ Gambar disimpan: {image_path}")
                else:
                    print(f"❌ Gagal unduh gambar ({r.status_code}): {img_url}")
            except Exception as e:
                print(f"❌ Exception saat unduh gambar: {e}")

    return {"station_info": station_info, "infographic": infographic_data}, image_path

# Fungsi utama membuka dan scraping data
def open_to_website():
    driver = setup_browser()
    driver.get(base_url)
    time.sleep(3)

    select_element = driver.find_element(By.ID, "station-select")
    select = Select(select_element)
    options = select.options

    for option in options:
        value = option.get_attribute("value")
        state_text = option.text.strip()
        if not value:
            continue

        print(f"\n➡️ Memproses: {state_text}")
        select.select_by_value(value)
        time.sleep(2)  # tambahkan delay agar data benar-benar termuat

        soup = BeautifulSoup(driver.page_source, "html.parser")
        meta_data, img_path = extract_station_data_table(soup, state_text)

        station = meta_data.get("station_info", {})
        info = meta_data.get("infographic", {})

        row = {
            "Station Name": state_text,
            "Station Type": station.get("Station Type:", ""),
            "SHEF ID": station.get("SHEF ID:", ""),
            "Normals Stn": station.get("Normals Stn:", ""),
            "County": station.get("County:", ""),
            "Nearest City": station.get("Nearest City:", ""),
            "Latitude": f"'{station.get('Latitude:', '')}",
            "Longitude": f"'{station.get('Longitude:', '')}",
            "Elevation": f"'{station.get('Elevation:', '')}",
            "Last maintenance": f"'{station.get('Established:', '')}",
            "Air Temperature (2m)": info.get("Air Temperature (2m)", ""),
            "Air Temperature (10m)": info.get("Air Temperature (10m)", ""),
            "Barometer": info.get("Barometer", ""),
            "Precipitation": info.get("Precipitation", ""),
            "Soil Moisture (2in)": info.get("Soil Moisture (2in)", ""),
            "Soil Moisture (4in)": info.get("Soil Moisture (4in)", ""),
            "Soil Moisture (8in)": info.get("Soil Moisture (8in)", ""),
            "Soil Moisture (16in)": info.get("Soil Moisture (16in)", ""),
            "Soil Temperature (2in)": f"'{info.get('Soil Temperature (2in)', '')}",
            "Soil Temperature (4in)": f"'{info.get('Soil Temperature (4in)', '')}",
            "Solar Sensor": info.get("Solar Radiation", ""),
            "WindSpeed/Direction (2m)": info.get("Wind Speed/Direction (2m)", ""),
            "WindSpeed/Direction (10m)": info.get("Wind Speed/Direction (10m)", "")
        }

        save_station_data(row)
        print(f"✅ Data berhasil disimpan untuk: {state_text}")

    driver.quit()

# Jalankan program utama
if __name__ == "__main__":
    open_to_website()
