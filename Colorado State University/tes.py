import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_station_ids(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [info.get("station") for info in data.values() if info.get("station")]
    except requests.exceptions.RequestException as e:
        print(f"❌ Terjadi kesalahan saat mengambil data: {e}")
        return []

def download_station_image_selenium(driver, station_id, save_folder="Image Station"):
    base_url = "https://coagmet.colostate.edu"
    page_url = f"{base_url}/stn_page.php?{station_id}"

    try:
        driver.get(page_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "metaData"))
        )

        meta_data_div = driver.find_element(By.ID, "metaData")
        img_elements = meta_data_div.find_elements(By.TAG_NAME, "img")

        if not img_elements:
            print(f"[{station_id}] ❌ Tidak ada gambar ditemukan dalam #metaData.")
            return

        img_src = img_elements[0].get_attribute("src")
        if not img_src:
            print(f"[{station_id}] ❌ Gambar pertama tidak memiliki src.")
            return

        # Buat full URL jika src relatif
        if img_src.startswith("/"):
            img_src = base_url + img_src

        os.makedirs(save_folder, exist_ok=True)
        ext = os.path.splitext(img_src)[-1] or ".jpeg"
        save_path = os.path.join(save_folder, f"{station_id}{ext}")

        img_data = requests.get(img_src).content
        with open(save_path, "wb") as f:
            f.write(img_data)

        print(f"[{station_id}] ✅ Gambar berhasil disimpan di: {save_path}")

    except Exception as e:
        print(f"[{station_id}] ❌ Gagal mengambil gambar: {e}")



def main():
    metadata_url = "https://coagmet.colostate.edu/data/metadata.json"
    station_ids = get_station_ids(metadata_url)

    if not station_ids:
        print("❌ Tidak ada Station ID yang ditemukan.")
        return

    # Inisialisasi satu kali driver
    options = Options()
    # options.add_argument("--headless")  # aktifkan jika ingin headless
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        for station_id in station_ids:  # coba 5 dulu
            download_station_image_selenium(driver, station_id)
            time.sleep(1)  # beri jeda agar stabil
    finally:
        driver.quit()
        print("🧹 Browser ditutup setelah semua proses selesai.")

if __name__ == "__main__":
    main()
