import os
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json

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




def get_sibling_text_by_label(soup, label_text):
    """
    Mencari teks sibling berdasarkan label (dalam div class='font-weight-bolder').

    Args:
        soup (BeautifulSoup): Objek soup hasil parsing HTML.
        label_text (str): Teks label yang ingin dicari, seperti 'Date of First Observation'.

    Returns:
        str atau None: Teks sibling jika ditemukan, atau None jika tidak.
    """
    label_div = soup.find("div", class_="font-weight-bolder", string=label_text)
    if label_div and label_div.parent:
        return label_div.parent.get_text(strip=True).replace(label_text, "").strip()
    return None

def get_sibling_text_by_label_from_id(soup, element_id, label_text):
    try:
        container = soup.find(id=element_id)
        if not container:
            print(f"❌ Tidak menemukan elemen dengan id '{element_id}'")
            return None

        label_element = container.find('span', string=label_text)
        if not label_element:
            print(f"❌ Tidak menemukan label '{label_text}' dalam id '{element_id}'")
            return None

        # Cari teks setelah <span>
        parent_div = label_element.find_parent()
        if not parent_div:
            return None

        # Ambil teks dari parent_div, lalu hapus label dari teks tersebut
        full_text = parent_div.get_text(separator=' ', strip=True)
        value = full_text.replace(label_text, "").strip()
        return value
    except Exception as e:
        print(f"❌ Error saat mengambil data '{label_text}' dari id '{element_id}': {e}")
        return None

# def get_sibling_text_by_label_from_id(soup, section_id, label_text):
#     section = soup.find(id=section_id)
#     if not section:
#         return None
#     label = section.find("td", string=label_text)
#     if not label:
#         return None
#     sibling = label.find_next_sibling("td")
#     return sibling.get_text(strip=True) if sibling else None


def station(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "tab_info_link"))).click()
        print("✅ Tab 'Station' diklik.")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[@id='info_header' and text()='Station Information']")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        station_data = {
            "Station Name": get_sibling_text_by_label(soup, "Station Name (ID)"),
            "City": get_sibling_text_by_label(soup, "City"),
            "County": get_sibling_text_by_label(soup, "County"),
            "State": get_sibling_text_by_label(soup, "State"),
            "Station Network": get_sibling_text_by_label(soup, "Station Network"),
            "Station Support": get_sibling_text_by_label(soup, "Station Support"),
            "River Basin": get_sibling_text_by_label(soup, "River Basin"),
            "Latitude": get_sibling_text_by_label(soup, "Latitude"),
            "Longitude": get_sibling_text_by_label(soup, "Longitude"),
            "Date of First Observation": get_sibling_text_by_label(soup, "Date of First Observation"),
            "Date of Latest Observation": get_sibling_text_by_label(soup, "Date of Latest Observation"),
            "Minute Data": get_sibling_text_by_label(soup, "Minute Data"),
            "Hourly Data": get_sibling_text_by_label(soup, "Hourly Data"),
            "Daily Data": get_sibling_text_by_label(soup, "Daily Data"),
            "Station Status": get_sibling_text_by_label(soup, "Station Status")
        }

        print(f"📍 Station Name: {station_data['Station Name']}")
        return station_data

    except Exception as e:
        print(f"❌ Gagal mengambil data station: {e}")
        return {}


def sensor(driver):
    """Klik tab 'Sensors' dan ekstrak informasi sensor."""
    try:
        time.sleep(1)

        sensor_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab_sensor_link"))
        )
        sensor_tab.click()
        print("✅ Tab 'Sensors' berhasil diklik.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@id='sensor_header' and text()='Sensor Information']"))
        )
        print("✅ Elemen 'Sensor Information' berhasil dimuat.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Daftar sensor dan ID HTML-nya
        sensor_ids = {
            "Apogee Instruments SP-510": "apogee_sp-510",
            "Apogee Instruments SQ-110": "apogee_sq-110",
            "Campbell Scientific CR1000": "cr1000",
            "Campbell Scientific 109": "cs_109-l",
            "Campbell Scientific Black Globe Thermometer": "cs_bgt",
            "METER Leaf Wetness Sensor": "decagon_lws",
            "Delta-T ML3": "delta-t_ml3",
            "Vaisala HMP155": "hmp-155",
            "RM Young 05103": "rm_young_05103",
            "Hydrological Services TB3": "tb3",
            "Vaisala WXT-520": "wxt-520"
        }

        sensor_data = {}

        for name, sensor_id in sensor_ids.items():
            sensor_data[name] = {
                "Sensor": get_sibling_text_by_label_from_id(soup, sensor_id, "Sensor:"),
                "Install Date": get_sibling_text_by_label_from_id(soup, sensor_id, "Install Date:"),
                "Measures": get_sibling_text_by_label_from_id(soup, sensor_id, "Measures:"),
                "Last Maintenance": get_sibling_text_by_label_from_id(soup, sensor_id, "Last Maintenance:"),
                "Height": get_sibling_text_by_label_from_id(soup, sensor_id, "Height:"),
                "Next Maintenance": get_sibling_text_by_label_from_id(soup, sensor_id, "Next Maintenance:")
            }

        print("✅ Data sensor berhasil diambil.")
        return sensor_data

    except Exception as e:
        print(f"❌ Gagal mengambil data sensor: {e}")
        return None


def media(driver, station_name):
    
    """Klik tab 'Media' dan simpan semua gambar dari tab tersebut."""

    try:
        time.sleep(1)  # Beri waktu DOM stabil

        sensor_tab_media = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab_media"))
        )
        sensor_tab_media.click()
        print("✅ Tab 'Media' berhasil diklik.")

        # Tunggu hingga media header muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//h1[@id='media_header' and text()='Station Photos & Videos']"
            ))
        )
        print("✅ Elemen 'Station Photos & Videos' berhasil dimuat.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        figures = soup.find_all('figure')
        print(f"📸 Menemukan {len(figures)} gambar.")

        folder = "North Carolina State University - Image"
        os.makedirs(folder, exist_ok=True)

        for fig in figures:
            img_tag = fig.find('img')
            figcaption = fig.find('figcaption')
            if img_tag and figcaption:
                img_url = img_tag['src']
                direction = figcaption.get_text(strip=True).replace(" ", "_")
                extension = os.path.splitext(img_url)[1].split('?')[0]
                filename = f"{station_name}-{direction}{extension}"
                filepath = os.path.join(folder, filename)
                response = requests.get(img_url)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Gambar disimpan: {filename}")

    except Exception as e:
        print(f"❌ Gagal mengambil media: {e}")

def close_modal_if_exists(driver):
    try:
        close_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, "modal-close")))
        close_button.click()
        print("✅ Modal ditutup.")
    except:
        pass  # Jika tidak ada modal, lanjutkan

def save_station_data(data):
    import csv
    filename = "station_data.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    print("✅ Data disimpan ke CSV.")

def run_all(driver, station_id):
    url = f"https://econet.climate.ncsu.edu/m/?id={station_id}"
    print(f"🌐 Membuka: {url}")
    driver.get(url)
    time.sleep(3)

    close_modal_if_exists(driver)

    station_data = station(driver)
    sensor_data = sensor(driver)
    media(driver)

    # if station_data.get("Station Name"):
    #     station_name = re.sub(r'[\\/*?:"<>|]', "_", station_data["Station Name"])
    #     media(driver, station_name)

    # else:
    #     print("⚠️ Station Name tidak ditemukan. Lewati media.")

    # if "Station Name" in station_data:
    #     station_name = re.sub(r'[\\/*?:"<>|]', "_", station_data["Station Name"] or "Unknown_Station")
    #     media(driver, station_name)
    #     print("DEBUG: station_data =", station_data)
    #     print("DEBUG: Station Name =", station_data.get("Station Name"))
    # else:
    #     print("⚠️ Station Name tidak ditemukan. Lewati media.")




    combined_data = {**station_data, **sensor_data}
    save_station_data(combined_data)

def open_urls_with_selenium(data):
    service = Service()
    options = Options()
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(service=service, options=options)
    try:
        for i, item in enumerate(data, start=1):
            station_id = item.get("id")
            if station_id:
                print(f"[{i}] Proses ID: {station_id}")
                run_all(driver, station_id)
    finally:
        driver.quit()
        print("✅ Semua URL telah diproses.")


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