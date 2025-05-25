import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

index__ = 5

# def save_station_data(data, filename=f"North Carolina State University-{index__}.csv"):
#     file_exists = os.path.isfile(filename)

#     with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = list(data.keys())
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         if not file_exists:
#             writer.writeheader()
#         writer.writerow(data)

#     print(f"✅ Data berhasil disimpan ke file '{filename}'")

def fetch_url(url):
    """Ambil konten HTML dari url."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def extract_script(html, script_index=19):
    """Ambil teks script pada indeks tertentu dari konten HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    if script_index < len(scripts):
        return scripts[script_index].text.strip()
    else:
        raise IndexError(f'Script index {script_index} out of range.')

def extract_json_from_script(script, start_marker, end_marker):
    """Ekstrak substring dari script antara start_marker dan end_marker lalu parsing ke JSON."""
    start_pos = script.find(start_marker)
    end_pos = script.rfind(end_marker)
    if start_pos != -1 and end_pos != -1:
        extracted_text = script[start_pos:end_pos + len(end_marker)]
        try:
            data = json.loads(extracted_text)
            ids = [item["id"] for item in data]
            print("✅ Semua ID:", ids)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f'❌ Gagal decode JSON: {e}')
    else:
        raise ValueError('❌ Start marker atau end marker tidak ditemukan.')




def close_modal_if_exists(driver):
    """Tutup modal station_modal jika muncul."""
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "station_modal"))
        )

        close_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#station_modal .modal-close"))
        )
        driver.execute_script("arguments[0].click();", close_button)
        print("✅ Modal popup #station_modal berhasil ditutup.")
        time.sleep(1)

        # Tambahan: tunggu hingga modal hilang
        WebDriverWait(driver, 5).until_not(
            EC.presence_of_element_located((By.ID, "station_modal"))
        )
        print("✅ Modal popup sudah hilang.")
    except TimeoutException:
        print("ℹ️ Modal #station_modal tidak muncul atau sudah tertutup.")


import os
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def donload_image(driver, save_folder="Image Station"):
    """Klik tab 'Sensors' dan unduh gambar Full Station."""
    try:
        time.sleep(2)

        sensor_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab_media_link"))
        )
        sensor_tab.click()
        print("✅ Tab 'Sensors' berhasil diklik.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@id='media_header' and text()='Station Photos & Videos']"))
        )
        print("✅ Elemen 'Station Photos & Videos' berhasil dimuat.")

        time.sleep(10)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Ambil ID dari URL
        current_url = driver.current_url
        station_id = parse_qs(urlparse(current_url).query).get("id", ["unknown"])[0]

        figures = soup.find_all('figure')
        for fig in figures:
            caption = fig.find('figcaption')
            if caption and "Full Station" in caption.text:
                img_tag = fig.find('img')
                if img_tag:
                    img_url = img_tag['src']
                    print(f"✅ Gambar ditemukan: {img_url}")

                    response = requests.get(img_url)
                    if response.status_code == 200:
                        os.makedirs(save_folder, exist_ok=True)

                        # Tentukan ekstensi file dari URL (misalnya .jpg)
                        ext = os.path.splitext(img_url)[-1]
                        filename = os.path.join(save_folder, f"{station_id}{ext}")

                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Gambar berhasil disimpan sebagai: {filename}")
                    else:
                        print("❌ Gagal mengunduh gambar.")
                break
        else:
            print("❌ Tidak ditemukan gambar dengan caption 'Full Station'.")

    except Exception as e:
        print(f"❌ Gagal mengklik tab 'Sensor' atau mengunduh gambar: {e}")

      


def open_urls_with_selenium(data):
    service = Service()
    options = Options()
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(service=service, options=options)

    try:
        for i, item in enumerate(data[index__:], start=index__ + 1):
            station_id = item.get("id")
            if station_id:
                url = f"https://econet.climate.ncsu.edu/m/?id={station_id}"
                print(f"[{i}] 🌐 Membuka URL: {url}")
                driver.get(url)
                time.sleep(3)

                close_modal_if_exists(driver)

                donload_image(driver)

    finally:
        driver.quit()
        print("✅ Semua halaman telah dibuka.")


def main():
    url = 'https://econet.climate.ncsu.edu/m/?id=BHIC'
    html = fetch_url(url)
    script = extract_script(html, script_index=19)

    start_marker = '[{"id":"AURO","index":1,"list'
    end_marker = '"marker_id":"point_KRZZ"}]'

    data_id = extract_json_from_script(script, start_marker, end_marker)
    print("📦 JSON berhasil di-load, jumlah item:", len(data_id))

    # Tambahkan ini untuk membuka URL dengan Selenium
    open_urls_with_selenium(data_id)


if __name__ == '__main__':
    main()
