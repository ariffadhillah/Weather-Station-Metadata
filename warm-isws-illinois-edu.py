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


def extract_station_data_table(soup, base_url, state_name, save_folder="image universitas utah"):
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
    


    history_tab_content = soup.find("div", id="history-tab-content")
    if not history_tab_content:
        return {}, None
    
    history_table = history_tab_content.find("table", id="history-table")
    print("history_table", history_table)
    history_rows = history_table.find_all("tr")  # jangan skip dulu

    history_data = {}
    for row in history_rows:
        history_cols = row.find_all("td")
        print(">> Kolom:", [col.get_text(strip=True) for col in history_cols])  # debug
        if len(history_cols) >= 2:
            history_measurement = history_cols[0].get_text(strip=True)
            history_sensor = history_cols[1].get_text(strip=True)
            history_data[history_measurement] = history_sensor

    

    
    sponsors_tab_content = soup.find("div", id="sponsors-tab-content")
    if not sponsors_tab_content:
        return {}, None
    
    sponsors_table = sponsors_tab_content.find("table", id="sponsors-data")
    print("sponsors_table", sponsors_table)
    sponsors_rows = sponsors_table.find_all("tr")  # jangan skip dulu
    
    sponsors_data = {}
    for row in sponsors_rows:
        sponsors_cols = row.find_all("td")
        print(">> Kolom:", [col.get_text(strip=True) for col in sponsors_cols])
        if len(sponsors_cols) >= 2:
            sponsors_measurement = sponsors_cols[0].get_text(strip=True)
            sponsors_sensor = sponsors_cols[1].get_text(strip=True)
            sponsors_data[sponsors_measurement] = sponsors_sensor

    

    # Ekstrak dan simpan gambar
    # image_tag = infographic_tab_content.find("img", id="infographicPic")
    # image_path = None
    # if image_tag and image_tag.get("src"):
    #     img_src = image_tag["src"]
    #     full_img_url = urljoin(base_url, img_src)
    #     print("Gambar URL:", full_img_url)

    #     os.makedirs(save_folder, exist_ok=True)
    #     # Bersihkan nama file dari karakter ilegal
    #     clean_state_name = ''.join(c for c in state_name if c.isalnum() or c in (' ', '_')).rstrip()
    #     filename = f"{clean_state_name} Station Instrumentation.jpg"
    #     image_path = os.path.join(save_folder, filename)

    #     try:
    #         response = requests.get(full_img_url)
    #         if response.status_code == 200:
    #             with open(image_path, "wb") as f:
    #                 f.write(response.content)
    #         else:
    #             print(f"Gagal download gambar untuk {state_name}: HTTP {response.status_code}")
    #             image_path = None
    #     except Exception as e:
    #         print(f"Gagal mengunduh gambar untuk {state_name}: {e}")
    #         image_path = None

    # # return data_infographic, image_path, history_data, sponsors_data 

    combined_data = {
        "infographic": data_infographic,
        "history": history_data,
        "sponsors": sponsors_data
    }
    return combined_data
    # return combined_data, image_path



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
        time.sleep(1)

        # Pilih state via JavaScript
        browser.execute_script(f"""
            let select = document.getElementById('station-select');
            select.value = '{state_val}';
            select.dispatchEvent(new Event('change'));
        """)
        time.sleep(3)  # Tunggu konten berubah

        # Ambil HTML baru
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # combined_data, image_file = extract_station_data_table(soup, base_url=url, state_name=state_text)
        combined_data = extract_station_data_table(soup, base_url=url, state_name=state_text)

        print("🛰️  Data Station Instrumentation:")
        combined_data_json = json.dumps(combined_data, indent=4, ensure_ascii=False)
        print(combined_data_json)

        # print("🛰️  Data Station Extremes:")
        # station_data_json = json.dumps(station_data, indent=4)
        # print(station_data_json)
        # for k, v in station_data.items():
        #     print(f"  • {k} → {v}")

        # print("🖼️  Path gambar:", image_file if image_file else "❌ Gagal ambil gambar")



# def open_to_website(browser):
#     url = "http://mesonet.k-state.edu/metadata/"
#     browser.get(url)
#     time.sleep(5)

#     # Ambil source HTML halaman
#     soup = BeautifulSoup(browser.page_source, "html.parser")

#     select_state = soup.find("div", id="station-data")

#     # Ambil semua opsi dari select
#     state_options = [
#         (opt.get("value"), opt.text.strip()) 
#         for opt in select_state.find_all("option") 
#         if opt.get("value")
#     ]

#     print(f"✅ Total state unik dalam form: {len(state_options)}")

#     wait = WebDriverWait(browser, 5)

#     for index, (state_val, state_text) in enumerate(state_options):
#         print(f"\n➡️ [{index + 1}] Memilih state: {state_text}")

#         browser.get(url)
#         wait.until(EC.presence_of_element_located((By.ID, "station-select")))
#         time.sleep(1)

#         # Pilih state via JavaScript
#         browser.execute_script(f"""
#             let select = document.getElementById('station-select');
#             select.value = '{state_val}';
#             select.dispatchEvent(new Event('Change Station'));
#         """)
#         print(f"✅ State '{state_text}' dipilih.")
#         time.sleep(2)
        
#         soup = BeautifulSoup(browser.page_source, "html.parser")

#         def extract_station_data_table(soup, base_url, save_folder="image universitas utah"):
#             infographic_tab_content = soup.find("div", id="infographic-tab-content")
#             if not infographic_tab_content:
#                 return {}, None

#             # Ekstrak data dari tabel
#             table = infographic_tab_content.find("table", id="station-data")
#             data = {}
#             if table:
#                 rows = table.find_all("tr")[1:]  # Lewati header
#                 for row in rows:
#                     cols = row.find_all("td")
#                     if len(cols) == 2:
#                         measurement = cols[0].get_text(strip=True)
#                         sensor = cols[1].get_text(strip=True)
#                         data[measurement] = sensor

#             # Ekstrak dan simpan gambar
#             image_tag = infographic_tab_content.find("img", id="infographicPic")
#             image_path = None
#             if image_tag and image_tag.get("src"):
#                 img_src = image_tag["src"]
#                 full_img_url = urljoin(base_url, img_src)
                
#                 os.makedirs(save_folder, exist_ok=True)
#                 filename = f"'{state_text}Station Instrumentation.jpg"
#                 image_path = os.path.join(save_folder, filename)

#                 try:
#                     response = requests.get(full_img_url)
#                     if response.status_code == 200:
#                         with open(image_path, "wb") as f:
#                             f.write(response.content)
#                     else:
#                         image_path = None
#                 except Exception as e:
#                     print(f"Gagal mengunduh gambar: {e}")
#                     image_path = None

#             return data, image_path

#     station_data, image_file = extract_station_data_table(soup)

#     print("Data sensor:")
#     print(station_data)
#     print("\nPath gambar:", image_file if image_file else "Gagal ambil gambar")


        # def extract_station_data_table(soup):
        #     infographic_tab_content = soup.find("div", id="infographic-tab-content")
        #     table = infographic_tab_content.find("table", id="station-data")
        #     if not table:
        #         return {}

        #     data = {}
        #     rows = table.find_all("tr")[1:]  # Lewati baris header

        #     for row in rows:
        #         cols = row.find_all("td")
        #         if len(cols) == 2:
        #             measurement = cols[0].get_text(strip=True)
        #             sensor = cols[1].get_text(strip=True)
        #             data[measurement] = sensor

        #     return data

        # station_data = extract_station_data_table(soup)
        # # Ubah ke JSON
        # station_data_json = json.dumps(station_data, indent=4)

        # print(station_data_json)

        # infographic_tab_content = soup.find("div", id="infographic-tab-content")
        # if infographic_tab_content:
        #     print("✅ Tab 'Instrumentation' ditemukan.")



        # 🔽 Tunggu hingga tab muncul dan klik tab yang diinginkan
        # try:
        #     wait.until(EC.presence_of_element_located((By.ID, "photos-tab")))
        #     tab_element_photo = browser.find_element(By.ID, "photos-tab")
        #     browser.execute_script("arguments[0].click();", tab_element_photo)
        #     print("✅ Tab 'Instrumentation' diklik.")
        # except Exception as e:
        #     print(f"❌ Gagal klik tab: {e}")

        # try:
        #     wait.until(EC.presence_of_element_located((By.ID, "infographic-tab")))
        #     tab_element_Instrumentation = browser.find_element(By.ID, "infographic-tab")
        #     browser.execute_script("arguments[0].click();", tab_element_Instrumentation)
        #     print("✅ Tab 'Instrumentation' diklik.")
        # except Exception as e:
        #     print(f"❌ Gagal klik tab: {e}")

        # try:
        #     wait.until(EC.presence_of_element_located((By.ID, "history-tab")))
        #     tab_element_history = browser.find_element(By.ID, "history-tab")
        #     browser.execute_script("arguments[0].click();", tab_element_history)
        #     print("✅ Tab 'Instrumentation' diklik.")
        # except Exception as e:
        #     print(f"❌ Gagal klik tab: {e}")

        # try:
        #     wait.until(EC.presence_of_element_located((By.ID, "sponsors-tab")))
        #     tab_element_Sponsors = browser.find_element(By.ID, "sponsors-tab")
        #     browser.execute_script("arguments[0].click();", tab_element_Sponsors)
        #     print("✅ Tab 'Instrumentation' diklik.")
        # except Exception as e:
        #     print(f"❌ Gagal klik tab: {e}")


# def open_to_website(browser):
#     url = "http://mesonet.k-state.edu/metadata/"
#     browser.get(url)
#     time.sleep(5)

#     # Ambil source HTML halaman
#     soup = BeautifulSoup(browser.page_source, "html.parser")

#     select_state = soup.find("div", id="station-data")

#     # Ambil semua opsi dari select
#     state_options = [
#         (opt.get("value"), opt.text.strip()) 
#         for opt in select_state.find_all("option") 
#         if opt.get("value")
#     ]

#     print(f"✅ Total state unik dalam form: {len(state_options)}")

#     wait = WebDriverWait(browser, 2)

#     for index, (state_val, state_text) in enumerate(state_options):
#         print(f"\n➡️ [{index + 1}] Memilih state: {state_text}")

#         browser.get(url)
#         wait.until(EC.presence_of_element_located((By.ID, "station-select")))
#         time.sleep(1)

#         # Pilih state via JavaScript
#         browser.execute_script(f"""
#             let select = document.getElementById('station-select');
#             select.value = '{state_val}';
#             select.dispatchEvent(new Event('Change Station'));
#         """)
#         print(f"✅ State '{state_text}' dipilih.")

#         time.sleep(1)

        # # Pilih product tetap
        # browser.execute_script("""
        #     let select = document.getElementById('product');
        #     select.value = 'summary';
        #     select.dispatchEvent(new Event('change'));
        # """)
        # print("✅ Product 'Current Weather Summary' dipilih.")

        time.sleep(1)

        # # Klik tombol Go
        # go_button = wait.until(EC.element_to_be_clickable((By.ID, "navgo")))
        # go_button.click()
        # print("✅ Tombol 'Go' diklik.")

        # soup = BeautifulSoup(browser.page_source, "html.parser")
        
        # tables = soup.find_all("table", attrs={"width": "800", "border": "1"})

        # for idx, table in enumerate(tables, 1):
        #     print(f"\n📄 Tabel #{idx}")

        #     rows = table.find_all("tr")
        #     for row in rows:
        #         cols = row.find(["td"])      
        #         print(cols)          
        #         # col_texts = [col.get_text(strip=True) for col in cols]
        #         # print(" | ".join(col_texts))
        #         print("-" * 50)
        # print(f"✅ Tabel #{idx} selesai diproses.")



        



        time.sleep(5)




def main():
    browser = setup_browser()
    open_to_website(browser)
    time.sleep(5)
    browser.quit()

if __name__ == "__main__":
    main()
