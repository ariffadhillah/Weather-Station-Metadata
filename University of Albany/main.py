import requests
import os
from bs4 import BeautifulSoup
import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# CSV_FILENAME = "University of Albany---Snow Network.csv"
# FIELDNAMES = ["Station Name", "Station ID", "Location", "County", "Latitude", "Longitude",
#               "Elevation", "Installed", "Station Number", "Climate Division", "NWS Forecast Office", "Type of Site", "Soil Type", "Obstructions within 100m", "Surroundings"]

# def save_meta_data(data, folder="meta_data"):
#     # Pastikan foldernya ada
#     os.makedirs(folder, exist_ok=True)
    
#     file_path = os.path.join(folder, CSV_FILENAME)
#     file_exists = os.path.isfile(file_path)

#     try:
#         with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)

#             # Tulis header hanya jika file belum ada
#             if not file_exists:
#                 writer.writeheader()

#             writer.writerow(data)
#             print(f"✅ Data metadata disimpan ke: {file_path}")

#     except Exception as e:
#         print(f"❌ Gagal menyimpan metadata: {e}")



def setup_browser():
    """setup browser and User-Agent randomly"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")

    # Membuat objek browser
    browser = webdriver.Chrome(options=chrome_options)

    # Arahkan ke URL
    url = "https://www.nysmesonet.org/about/sites#network=profiler&stid=prof_bell"
    browser.get(url)

    time.sleep(2)
    return browser

def get_station_info_by_label(soup, label_text):
    """Cari label di tag <strong> dan ambil sibling-nya."""
    try:
        # Temukan elemen <strong> dengan teks sesuai (misalnya: Station ID)
        strong_tag = soup.find("strong", string=label_text)
        if strong_tag:
            td_parent = strong_tag.find_parent("td")  # td yang mengandung <strong>
            td_sibling = td_parent.find_next_sibling("td")  # td berikutnya
            return td_sibling.get_text(strip=True) if td_sibling else None
        else:
            print(f"⚠️ Label '{label_text}' tidak ditemukan.")
            return None
    except Exception as e:
        print(f"❌ Error saat mengambil '{label_text}': {e}")
        return None


def download_station_image(browser,station_id):
    try:
        # Tunggu gambar muncul
        WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.col-md-6.text-center img'))
        )

        # Parse HTML setelah gambar muncul
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        # Temukan tag <img>
        img_tag = soup.select_one('div.col-md-6.text-center img')
        if img_tag and img_tag['src']:
            img_url = img_tag['src']
            if img_url.startswith("//"):
                img_url = "https:" + img_url

            # Unduh gambar
            response = requests.get(img_url)
            if response.status_code == 200:
                # Buat folder jika belum ada
                folder_name = "Image Station"
                os.makedirs(folder_name, exist_ok=True)

                # Simpan gambar ke folder
                filename = os.path.join(folder_name, f"{station_id}.jpg")
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Gambar disimpan di: {filename}")
            else:
                print(f"⚠️ Gagal mengunduh gambar, status: {response.status_code}")
        else:
            print("⚠️ Tag <img> tidak ditemukan.")
    except Exception as e:
        print(f"❌ Error saat mengunduh gambar: {e}")

def read_table(browser, timeout=10):
    """Menunggu dan membaca tabel HTML dengan class 'table table-sm'."""
    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-sm"))
        )
        soup = BeautifulSoup(browser.page_source, "html.parser")
        table = soup.find("table", class_="table-sm")

        station_id = get_station_info_by_label(table, "Station ID")
        location = get_station_info_by_label(soup, "Location")
        # county = get_station_info_by_label(soup, "County")
        # latitude = get_station_info_by_label(soup, "Latitude")
        # longitude = get_station_info_by_label(soup, "Longitude")
        # elevation = get_station_info_by_label(soup, "Elevation")
        # installed = get_station_info_by_label(soup, "Installed")
        # station_number = get_station_info_by_label(soup, "Station Number")
        # climate_division = get_station_info_by_label(soup, "Climate Division")
        # nws_forecast_office = get_station_info_by_label(soup, "NWS Forecast Office")
        # type_of_Site = get_station_info_by_label(soup, "Type of Site")
        # soil_type = get_station_info_by_label(soup, "Soil Type")
        # obstructions_within_100m = get_station_info_by_label(soup, "Obstructions within 100m")
        # surroundings = get_station_info_by_label(soup, "Surroundings")

        # Ambil Station Name dari lokasi (ambil setelah "of ")
        station_name = None
        if location:
            match = re.search(r'of\s+(.+)', location)
            if match:
                station_name = match.group(1).strip()
            else:
                # fallback: ambil 1 kata terakhir
                station_name = location.split()[-1]

        # Unduh gambar
        download_station_image(browser, station_id)

        print("Station ID:", station_id)
        print("Station Name:", station_name)
        # print("Location:", location)
        # print("County:", county)
        # print("Latitude:", latitude)
        # print("Longitude:", longitude)
        # print("Elevation:", elevation)
        # print("Installed:", installed)
        # print("Station Number:", station_number)
        # print("Climate Division:", climate_division)
        # print("NWS Forecast Office:", nws_forecast_office)

        # data_save = {
        #     'Station Name': station_name,
        #     'Station ID': station_id,
        #     'Location': location,
        #     'County': county,
        #     'Latitude': f"'{latitude}",
        #     'Longitude': f"'{longitude}",
        #     'Elevation': elevation,
        #     'Installed': installed,
        #     'Station Number': station_number,
        #     'Climate Division': f"'{climate_division}",
        #     'NWS Forecast Office': nws_forecast_office,
        #     'Type of Site' : type_of_Site,
        #     'Soil Type': soil_type,
        #     'Obstructions within 100m' : obstructions_within_100m,
        #     'Surroundings': surroundings
        # }

        # # print(data_save)
        # save_meta_data(data_save)

        # return data_save

    except Exception as e:
        print(f"❌ Gagal membaca tabel: {e}")
        return None

def select_options(browser):
    wait = WebDriverWait(browser, 20)

    # Tunggu sampai <main role="main"> muncul
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'main[role="main"]')))
    
    # Ambil elemen <main>
    main_element = browser.find_element(By.CSS_SELECTOR, 'main[role="main"]')
    
    # Cari semua <div> dengan class dropdown dalam <main>
    dropdown_containers = main_element.find_elements(By.CSS_SELECTOR, 'div.col-12.col-sm-6.col-md-5.col-lg-4.col-xl-3')
    
    if len(dropdown_containers) < 2:
        print("❌ Tidak ditemukan dua dropdown seperti yang diharapkan.")
        return

    # # Ambil elemen <select> dari masing-masing container
    # select_network = Select(dropdown_containers[0].find_element(By.TAG_NAME, 'select'))[2]
    # select_station = Select(dropdown_containers[1].find_element(By.TAG_NAME, 'select'))

    # # Loop semua network
    # for network_option in select_network.options:
    #     network_value = network_option.get_attribute("value")
    #     if not network_value:
    #         continue

    #     print(f"\n🔄 Memilih Network: {network_value}")
    #     select_network.select_by_value(network_value)

    #     # Tunggu dropdown stasiun terupdate
    #     time.sleep(2)

    #     # Perbarui elemen station_network karena bisa berubah
    #     main_element = browser.find_element(By.CSS_SELECTOR, 'main[role="main"]')
    #     dropdown_containers = main_element.find_elements(By.CSS_SELECTOR, 'div.col-12.col-sm-6.col-md-5.col-lg-4.col-xl-3')
    #     select_station = Select(dropdown_containers[1].find_element(By.TAG_NAME, 'select'))

    #     # Loop semua stasiun
    #     for station_option in select_station.options:
    #         station_value = station_option.get_attribute("value")
    #         if not station_value:
    #             continue

    #         print(f"   📍 Memilih Stasiun: {station_value}")
    #         select_station.select_by_value(station_value)
            

    #         # Tunggu isi halaman muncul
    #         time.sleep(3)

    #         # 🔽 BACA DATA TABEL DI SINI
    #         read_table(browser)


    # Ambil objek Select dari dropdown pertama (network)
    select_network = Select(dropdown_containers[0].find_element(By.TAG_NAME, 'select'))

    # Loop semua network mulai dari opsi ke-2
    for network_option in select_network.options[0:]:  # Skip option pertama (biasanya kosong atau placeholder)
        network_value = network_option.get_attribute("value")
        if not network_value:
            continue

        print(f"\n🔄 Memilih Network: {network_value}")
        select_network.select_by_value(network_value)

        # Tunggu dropdown stasiun terupdate
        time.sleep(2)

        # Perbarui elemen station karena DOM mungkin berubah
        main_element = browser.find_element(By.CSS_SELECTOR, 'main[role="main"]')
        dropdown_containers = main_element.find_elements(By.CSS_SELECTOR, 'div.col-12.col-sm-6.col-md-5.col-lg-4.col-xl-3')
        select_station = Select(dropdown_containers[1].find_element(By.TAG_NAME, 'select'))

        # Loop semua stasiun dari awal atau sesuai kebutuhan
        for station_option in select_station.options:
            station_value = station_option.get_attribute("value")
            if not station_value:
                continue

            print(f"   📍 Memilih Stasiun: {station_value}")
            select_station.select_by_value(station_value)

            # Tunggu isi halaman muncul
            time.sleep(3)

            # 🔽 BACA DATA TABEL
            read_table(browser)



def main():
    browser = setup_browser()
    try:
        select_options(browser)
    finally:
        browser.quit()


if __name__ == "__main__":
    main()
