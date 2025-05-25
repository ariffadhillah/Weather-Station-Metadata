import requests
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time



# def get_station_ids(url):
#     """
#     Mengambil dan mengembalikan daftar ID stasiun dari metadata JSON.
#     """
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()

#         station_ids = []
#         for station_id, info in data.items():
#             station = info.get("station")
#             if station:
#                 station_ids.append(station)
#         return station_ids

#     except requests.exceptions.RequestException as e:
#         print(f"Terjadi kesalahan saat mengambil data: {e}")
#         return []


def get_station_ids(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [info.get("station") for info in data.values() if info.get("station")]
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengambil data: {e}")
        return []

def download_station_image_selenium(station_id, save_folder="Image Station-new"):
    base_url = "https://coagmet.colostate.edu"
    page_url = f"{base_url}/stn_page.php?{station_id}"

    options = Options()
    options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(page_url)

        # Tunggu sampai #metaData muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "metaData"))
        )

        meta_data_div = driver.find_element(By.ID, "metaData")

        # Cari semua img di dalam metaData
        img_elements = meta_data_div.find_elements(By.TAG_NAME, "img")

        if not img_elements:
            print(f"[{station_id}] Tidak ada gambar ditemukan dalam #metaData.")
            return

        # Ambil gambar pertama
        img_src = img_elements[0].get_attribute("src")

        if not img_src:
            print(f"[{station_id}] Gambar pertama tidak memiliki src.")
            return

        # Download dan simpan
        os.makedirs(save_folder, exist_ok=True)
        ext = os.path.splitext(img_src)[-1] or ".jpeg"
        save_path = os.path.join(save_folder, f"{station_id}{ext}")

        img_data = requests.get(img_src).content
        with open(save_path, "wb") as f:
            f.write(img_data)

        print(f"[{station_id}] Gambar berhasil disimpan: {save_path}")

    except Exception as e:
        print(f"[{station_id}] Gagal mengambil gambar: {e}")
    finally:
        driver.quit()


def main():
    metadata_url = "https://coagmet.colostate.edu/data/nw/metadata.json"
    station_ids = get_station_ids(metadata_url)

    for station_id in station_ids[3:]:
        download_station_image_selenium(station_id)



if __name__ == "__main__":
    main()
