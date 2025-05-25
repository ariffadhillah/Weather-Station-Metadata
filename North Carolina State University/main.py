# import requests
# from bs4 import BeautifulSoup
# import json

# def fetch_url(url):
#     """Ambil konten HTML dari url."""
#     response = requests.get(url)
#     response.raise_for_status()  # agar error jika gagal
#     return response.content



# def extract_script(html, script_index=19):
#     """Ambil teks script pada indeks tertentu dari konten HTML."""
#     soup = BeautifulSoup(html, 'html.parser')
#     scripts = soup.find_all('script')
#     if script_index < len(scripts):
#         return scripts[script_index].text.strip()
#     else:
#         raise IndexError(f'Script index {script_index} out of range.')




# def extract_json_from_script(script, start_marker, end_marker):
#     """Ekstrak substring dari script antara start_marker dan end_marker lalu parsing ke JSON."""
#     start_pos = script.find(start_marker)
#     end_pos = script.rfind(end_marker)
#     if start_pos != -1 and end_pos != -1:
#         extracted_text = script[start_pos:end_pos + len(end_marker)]
#         try:
#             data = json.loads(extracted_text)
#             ids = [item["id"] for item in data]

#             print("Semua ID:", ids)
#             # print("JSON berhasil di-load, jumlah item:", len(data))
#             return data
#         except json.JSONDecodeError as e:
#             raise ValueError(f'Gagal decode JSON: {e}')
#     else:
#         raise ValueError('Start marker atau end marker tidak ditemukan.')


# def main():
#     url = 'https://econet.climate.ncsu.edu/m/?id=BHIC'
#     html = fetch_url(url)
#     script = extract_script(html, script_index=19)

#     start_marker = '[{"id":"AURO","index":1,"list'
#     end_marker = '"marker_id":"point_KRZZ"}]'

#     data_id = extract_json_from_script(script, start_marker, end_marker)
#     # print(data)
#     print("JSON berhasil di-load, jumlah item:", len(data_id))

# if __name__ == '__main__':
#     main()



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

index__ = 157

def save_station_data(data, filename=f"North Carolina State University-{index__}.csv"):
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(data.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

    print(f"✅ Data berhasil disimpan ke file '{filename}'")

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

# def get_sibling_text_by_label_from_id(soup, element_id, label_text):
#     try:
#         container = soup.find(id=element_id)
#         if not container:
#             print(f"❌ Tidak menemukan elemen dengan id '{element_id}'")
#             return None

#         label_element = container.find('span', string=label_text)
#         if not label_element:
#             print(f"❌ Tidak menemukan label '{label_text}' dalam id '{element_id}'")
#             return None

#         # Cari teks setelah <span>
#         parent_div = label_element.find_parent()
#         if not parent_div:
#             return None

#         # Ambil teks dari parent_div, lalu hapus label dari teks tersebut
#         full_text = parent_div.get_text(separator=' ', strip=True)
#         value = full_text.replace(label_text, "").strip()
#         return value
#     except Exception as e:
#         print(f"❌ Error saat mengambil data '{label_text}' dari id '{element_id}': {e}")
#         return None


def get_sibling_text_by_label_from_id_index(soup, element_id, label_text, index=0):
    try:
        containers = soup.find_all(id=element_id)
        if len(containers) <= index:
            print(f"❌ Tidak menemukan elemen ke-{index+1} dengan id '{element_id}'")
            return None

        container = containers[index]

        label_element = container.find('span', string=label_text)
        if not label_element:
            print(f"❌ Tidak menemukan label '{label_text}' dalam elemen ke-{index+1} dari id '{element_id}'")
            return None

        parent_div = label_element.find_parent()
        if not parent_div:
            return None

        full_text = parent_div.get_text(separator=' ', strip=True)
        value = full_text.replace(label_text, "").strip()
        return value
    except Exception as e:
        print(f"❌ Error saat mengambil data '{label_text}' dari elemen ke-{index+1} dengan id '{element_id}': {e}")
        return None


# def get_text_by_label_from_container(container, label_text):
#     """
#     Dari sebuah container BeautifulSoup, cari teks berdasarkan label dalam <span>.
#     Misal: <span>Install Date:</span> Sep 16, 2020 → kembalikan "Sep 16, 2020"
#     """
#     divs = container.find_all("div", recursive=True)
#     for div in divs:
#         span = div.find("span")
#         if span and span.get_text(strip=True) == label_text:
#             full_text = div.get_text(separator=' ', strip=True)
#             return full_text.replace(label_text, "").strip()
#     return None


# def get_all_by_id_and_label(soup, element_id, label_text):
#     """
#     Ambil semua elemen dengan ID yang sama (jika duplikat),
#     lalu ambil nilai berdasarkan label.
#     """
#     containers = soup.find_all(id=element_id)
#     results = []

#     for i, container in enumerate(containers, start=1):
#         value = get_text_by_label_from_container(container, label_text)
#         results.append((i, value))

#     return results




# Fungsi untuk mengambil nama stasiun
# def get_station_name_from_soup(soup):
    
#     station_name = get_sibling_text_by_label(soup, "Station Name (ID)")
#     if station_name:
#         print(f"📅 Station Name: {station_name}")
#     else:
#         print("❌ Tidak menemukan informasi 'Station Name (ID)'.")
#     return station_name



# def media(driver, station_name):
#     """Klik tab 'Media' dan simpan semua gambar dari tab tersebut."""
#     try:
        
#         time.sleep(1)  # Beri waktu DOM stabil

#         sensor_tab = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "tab_media"))
#         )
#         sensor_tab.click()
#         print("✅ Tab 'Media' berhasil diklik.")

#         # Tunggu hingga media header muncul
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((
#                 By.XPATH, "//h1[@id='media_header' and text()='Station Photos & Videos']"
#             ))
#         )
#         print("✅ Elemen 'Station Photos & Videos' berhasil dimuat.")

#         # Parse HTML dan cari semua gambar
#         sensor_html = driver.page_source
#         soup = BeautifulSoup(sensor_html, 'html.parser')

#         figures = soup.find_all('figure')
#         print(f"📸 Menemukan {len(figures)} gambar.")

#         # Folder untuk menyimpan gambar
#         os.makedirs("North Carolina State University - Image", exist_ok=True)

#         for fig in figures:
#             img_tag = fig.find('img')
#             figcaption = fig.find('figcaption')

#             if img_tag and figcaption:
#                 img_url = img_tag['src']
#                 direction = figcaption.get_text(strip=True).replace(" ", "_")  # e.g., Northwest
#                 extension = os.path.splitext(img_url)[1].split('?')[0]  # e.g., .jpg

#                 filename = f"{station_name}-{direction}{extension}"
#                 filepath = os.path.join("North Carolina State University - Image", filename)

#                 # Download image
#                 response = requests.get(img_url)
#                 with open(filepath, 'wb') as f:
#                     f.write(response.content)
#                 print(f"✅ Gambar disimpan: {filename}")

#     except Exception as e:
#         print(f"❌ Gagal menyimpan gambar media: {e}")


def station(driver):
    try:
        time.sleep(2)
        station_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab_info_link"))
        )
        station_tab.click()
        print("✅ Tab 'Station' berhasil diklik.")

        # Tunggu hingga label 'Date of First Observation' muncul di HTML
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//h1[@id='info_header' and text()='Station Information']"
            ))
        )
        print("✅ Elemen 'Station Information' berhasil dimuat.")

        time.sleep(5)

        # Parse HTML setelah elemen benar-benar muncul
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')



        station_name = get_sibling_text_by_label(soup, "Station Name (ID)")
        if station_name:
            print(f"📅 Stations Name: {station_name}")
        else:
            print(f"❌ Tidak menemukan informasi '{station_name}'.")
            
        # station_name = get_station_name_from_soup(soup)

        # # Kirim station_name ke fungsi media
        # if station_name:
        #     media(driver, station_name)
        # else:
        #     print("⚠️ Station Name tidak ditemukan. Lewati media.")

        city_name = get_sibling_text_by_label(soup, "City")
        if city_name:
            print(f"📅 City: {city_name}")
        else:
            print(f"❌ Tidak menemukan informasi '{city_name}'.")

        county = get_sibling_text_by_label(soup, "County")
        if county:
            print(f"📅 County: {county}")
        else:
            print(f"❌ Tidak menemukan informasi '{county}'.")

        state = get_sibling_text_by_label(soup, "State")
        if state:
            print(f"📅 State: {state}")
        else:
            print(f"❌ Tidak menemukan informasi '{state}'.")

        station_network = get_sibling_text_by_label(soup, "Station Network")
        if station_network:
            print(f"📅 Station Network: {station_network}")
        else:
            print(f"❌ Tidak menemukan informasi '{station_network}'.")

        station_Support = get_sibling_text_by_label(soup, "Station Support")
        if station_Support:
            print(f"📅 Station Support: {station_Support}")
        else:
            print(f"❌ Tidak menemukan informasi '{station_Support}'.")


        river_Basin = get_sibling_text_by_label(soup, "River Basin")
        if river_Basin:
            print(f"📅 River Basin: {river_Basin}")
        else:
            print(f"❌ Tidak menemukan informasi '{river_Basin}'.")


        latitude = get_sibling_text_by_label(soup, "Latitude")
        if latitude:
            print(f"📅 Latitude: {latitude}")
        else:
            print(f"❌ Tidak menemukan informasi '{latitude}'.")

        longitude = get_sibling_text_by_label(soup, "Longitude")
        if longitude:
            print(f"📅 Longitude: {longitude}")
        else:
            print(f"❌ Tidak menemukan informasi '{longitude}'.")

        elevation = get_sibling_text_by_label(soup, "Elevation")
        if elevation:
            print(f"📅 Elevation: {elevation}")
        else:
            print(f"❌ Tidak menemukan informasi '{elevation}'.")

        nws_Office = get_sibling_text_by_label(soup, "NWS Office")
        if nws_Office:
            print(f"📅 NWS Office: {nws_Office}")
        else:
            print(f"❌ Tidak menemukan informasi '{nws_Office}'.")


        climate_Division = get_sibling_text_by_label(soup, "Climate Division")
        if climate_Division:
            print(f"📅 Climate Division: {climate_Division}")
        else:
            print(f"❌ Tidak menemukan informasi '{climate_Division}'.")

        soil_Type = get_sibling_text_by_label(soup, "Soil Type")
        if soil_Type:
            print(f"📅 Soil Type: {soil_Type}")
        else:
            print(f"❌ Tidak menemukan informasi '{soil_Type}'.")


        date_of_First_Observation = get_sibling_text_by_label(soup, "Date of First Observation")
        if date_of_First_Observation:
            print(f"📅 Date of First Observation: {date_of_First_Observation}")
        else:
            print(f"❌ Tidak menemukan informasi '{date_of_First_Observation}'.")

        date_of_Latest_Observation = get_sibling_text_by_label(soup, "Date of Latest Observation")
        if date_of_Latest_Observation:
            print(f"📅 Date of Latest Observation: {date_of_Latest_Observation}")
        else:
            print(f"❌ Tidak menemukan informasi '{date_of_Latest_Observation}'.")


        minute_Data = get_sibling_text_by_label(soup, "Minute Data")
        if minute_Data:
            print(f"📅 Minute Data: {minute_Data}")
        else:
            print(f"❌ Tidak menemukan informasi '{minute_Data}'.")

        hourly_Data = get_sibling_text_by_label(soup, "Hourly Data")
        if hourly_Data:
            print(f"📅 Hourly Data: {hourly_Data}")
        else:
            print(f"❌ Tidak menemukan informasi '{hourly_Data}'.")

        daily_Data = get_sibling_text_by_label(soup, "Daily Data")
        if daily_Data:
            print(f"📅 Daily Data: {daily_Data}")
        else:
            print(f"❌ Tidak menemukan informasi '{daily_Data}'.")
 
        station_Status = get_sibling_text_by_label(soup, "Station Status")
        if station_Status:
            print(f"📅 Station Status: {station_Status}")
        else:
            print(f"❌ Tidak menemukan informasi '{station_Status}'.")
        time.sleep(3)
        data_station = {
            "Station Name": station_name,
            "City": city_name,
            "County": county,
            "State": state,
            "Station Network": station_network,
            "Station Support": station_Support,
            "River Basin": river_Basin,
            "Latitude": latitude,
            "Longitude": longitude,
            "Date of First Observation": date_of_First_Observation,
            "Date of Latest Observation": date_of_Latest_Observation,
            "Minute Data": minute_Data,
            "Hourly Data": hourly_Data,
            "Daily Data": daily_Data,
            "Station Status": station_Status

        }
        
        return data_station


    except Exception as e:
        print(f"❌ Gagal mengakses tab 'Station': {e}")
        return None



def sensor(driver):
    """Klik tab 'Sensors'."""
    try:
        time.sleep(2)  # Beri waktu DOM stabil

        sensor_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab_sensor_link"))
        )
        sensor_tab.click()
        print("✅ Tab 'Sensors' berhasil diklik.")

        # Tunggu hingga label 'Date of First Observation' muncul di HTML
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//h1[@id='sensor_header' and text()='Sensor Information']"
            ))
        )
        print("✅ Elemen 'Sensor Information' berhasil dimuat.")

        time.sleep(10)
        # Scroll ke bagian bawah agar seluruh sensor termuat
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)


        sensor_html = driver.page_source
        soup = BeautifulSoup(sensor_html, 'html.parser')

        sensor_name_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id_index(soup, "apogee_sp-510", "Sensor:", index=0) or ''
        install_date_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id_index(soup, "apogee_sp-510", "Install Date:", index=0) or ''
        measures_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id_index(soup, "apogee_sp-510", "Measures:", index=0) or ''
        last_maintenance_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id_index(soup, "apogee_sp-510", "Last Maintenance:", index=0) or ''
        height_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id_index(soup, "apogee_sp-510", "Height:", index=0) or ''
        next_Maintenance_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id_index(soup, "apogee_sp-510", "Next Maintenance:", index=0) or ''


        sensor_name_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Sensor:", index=0) or ''
        install_date_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Install Date:", index=0) or ''
        measures_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Measures:", index=0) or ''
        last_maintenance_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Last Maintenance:", index=0) or ''
        height_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Height:", index=0) or ''
        next_Maintenance_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Next Maintenance:", index=0) or ''

        sensor_name_Apogee_Instruments_SQ_110_2 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Sensor:", index=1) or ''
        install_date_Apogee_Instruments_SQ_110_2 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Install Date:", index=1) or ''
        measures_Apogee_Instruments_SQ_110_2 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Measures:", index=1) or ''
        last_maintenance_Apogee_Instruments_SQ_110_2 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Last Maintenance:", index=1) or ''
        height_Apogee_Instruments_SQ_110_2 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Height:", index=1) or ''
        next_Maintenance_Apogee_Instruments_SQ_110_2 = get_sibling_text_by_label_from_id_index(soup, "apogee_sq-110", "Next Maintenance:", index=1) or ''


        sensor_name_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id_index(soup, "cr1000", "Sensor:", index=0) or ''
        install_date_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id_index(soup, "cr1000", "Install Date:", index=0) or ''
        measures_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id_index(soup, "cr1000", "Measures:", index=0) or ''
        last_maintenance_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id_index(soup, "cr1000", "Last Maintenance:", index=0) or ''
        height_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id_index(soup, "cr1000", "Height:", index=0) or ''
        next_Maintenance_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id_index(soup, "cr1000", "Next Maintenance:", index=0) or ''

        sensor_name_Campbell_Scientific_CR1000X = get_sibling_text_by_label_from_id_index(soup, "cr1000x", "Sensor:", index=0) or ''
        install_date_Campbell_Scientific_CR1000X = get_sibling_text_by_label_from_id_index(soup, "cr1000x", "Install Date:", index=0) or ''
        measures_Campbell_Scientific_CR1000X = get_sibling_text_by_label_from_id_index(soup, "cr1000x", "Measures:", index=0) or ''
        last_maintenance_Campbell_Scientific_CR1000X = get_sibling_text_by_label_from_id_index(soup, "cr1000x", "Last Maintenance:", index=0) or ''
        height_Campbell_Scientific_CR1000X = get_sibling_text_by_label_from_id_index(soup, "cr1000x", "Height:", index=0) or ''
        next_Maintenance_Campbell_Scientific_CR1000X = get_sibling_text_by_label_from_id_index(soup, "cr1000x", "Next Maintenance:", index=0) or ''


        sensor_name_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Sensor:", index=0) or ''
        install_date_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Install Date:", index=0) or ''
        measures_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Measures:", index=0) or ''
        last_maintenance_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Last Maintenance:", index=0) or ''
        height_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Height:", index=0) or ''
        depth_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Depth:", index=0) or ''
        next_Maintenance_Campbell_Scientific_109 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Next Maintenance:", index=0) or ''


        sensor_name_Campbell_Scientific_109_2 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Sensor:", index=1) or ''
        install_date_Campbell_Scientific_109_2 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Install Date:", index=1) or ''            
        measures_Campbell_Scientific_109_2 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Measures:", index=1) or ''
        last_maintenance_Campbell_Scientific_109_2 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Last Maintenance:", index=1) or ''
        height_Campbell_Scientific_109_2 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Height:", index=1) or ''
        next_Maintenance_Campbell_Scientific_109_2 = get_sibling_text_by_label_from_id_index(soup, "cs_109-l", "Next Maintenance:", index=1) or ''
        



        sensor_name_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id_index(soup, "cs_bgt", "Sensor:", index=0) or ''
        install_date_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id_index(soup, "cs_bgt", "Install Date:", index=0) or ''
        measures_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id_index(soup, "cs_bgt", "Measures:", index=0) or ''
        last_maintenance_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id_index(soup, "cs_bgt", "Last Maintenance:", index=0) or ''
        height_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id_index(soup, "cs_bgt", "Height:", index=0) or ''
        next_Maintenance_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id_index(soup, "cs_bgt", "Next Maintenance:", index=0) or ''

        sensor_name_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id_index(soup, "decagon_lws", "Sensor:", index=0) or ''
        install_date_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id_index(soup, "decagon_lws", "Install Date:", index=0) or ''
        measures_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id_index(soup, "decagon_lws", "Measures:", index=0) or ''
        last_maintenance_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id_index(soup, "decagon_lws", "Last Maintenance:", index=0) or ''
        height_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id_index(soup, "decagon_lws", "Height:", index=0) or ''
        next_Maintenance_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id_index(soup, "decagon_lws", "Next Maintenance:", index=0) or ''

        sensor_name_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Sensor:", index=0) or ''
        install_date_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Install Date:", index=0) or ''
        measures_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Measures:", index=0) or ''
        last_maintenance_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Last Maintenance:", index=0) or ''
        height_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Height:", index=0) or ''
        next_Maintenance_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Next Maintenance:", index=0) or ''
        depth_Delta_T_ML3 = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml3", "Depth:", index=0) or ''

        sensor_name_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Sensor:", index=0) or ''
        install_date_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Install Date:", index=0) or ''
        measures_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Measures:", index=0) or ''
        last_maintenance_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Last Maintenance:", index=0) or ''
        height_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Height:", index=0) or ''
        next_Maintenance_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Next Maintenance:", index=0) or ''
        depth_Delta_TML2x = get_sibling_text_by_label_from_id_index(soup, "delta-t_ml2x", "Depth:", index=0) or ''

        sensor_name_Vaisala_HMP155 = get_sibling_text_by_label_from_id_index(soup, "hmp-155", "Sensor:", index=0) or ''
        install_date_Vaisala_HMP155 = get_sibling_text_by_label_from_id_index(soup, "hmp-155", "Install Date:", index=0) or ''
        measures_Vaisala_HMP155 = get_sibling_text_by_label_from_id_index(soup, "hmp-155", "Measures:", index=0) or ''
        last_maintenance_Vaisala_HMP155 = get_sibling_text_by_label_from_id_index(soup, "hmp-155", "Last Maintenance:", index=0) or ''
        height_Vaisala_HMP155 = get_sibling_text_by_label_from_id_index(soup, "hmp-155", "Height:", index=0) or ''
        next_Maintenance_Vaisala_HMP155 = get_sibling_text_by_label_from_id_index(soup, "hmp-155", "Next Maintenance:", index=0) or ''

        sensor_name_RM_Young_05103 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Sensor:", index=0) or ''
        install_date_RM_Young_05103 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Install Date:", index=0) or ''
        measures_RM_Young_05103 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Measures:", index=0) or ''
        last_maintenance_RM_Young_05103 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Last Maintenance:", index=0) or ''
        height_RM_Young_05103 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Height:", index=0) or ''
        next_Maintenance_RM_Young_05103 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Next Maintenance:", index=0) or ''

        sensor_name_RM_Young_05103_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Sensor:", index=1) or '' 
        install_date_RM_Young_05103_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Install Date:", index=1) or '' 
        measures_RM_Young_05103_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Measures:", index=1) or '' 
        last_maintenance_RM_Young_05103_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Last Maintenance:", index=1) or '' 
        height_RM_Young_05103_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Height:", index=1) or '' 
        next_Maintenance_RM_Young_05103_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103", "Next Maintenance:", index=1) or '' 

        sensor_name_RM_Young_05103_Alpine = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Sensor:", index=0) or '' 
        install_date_RM_Young_05103_Alpine = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Install Date:", index=0) or '' 
        measures_RM_Young_05103_Alpine = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Measures:", index=0) or '' 
        last_maintenance_RM_Young_05103_Alpine = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Last Maintenance:", index=0) or '' 
        height_RM_Young_05103_Alpine = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Height:", index=0) or '' 
        next_Maintenance_RM_Young_05103_Alpine = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Next Maintenance:", index=0) or '' 

        sensor_name_RM_Young_05103_Alpine_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Sensor:", index=1) or '' 
        install_date_RM_Young_05103_Alpine_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Install Date:", index=1) or '' 
        measures_RM_Young_05103_Alpine_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Measures:", index=1) or '' 
        last_maintenance_RM_Young_05103_Alpine_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Last Maintenance:", index=1) or '' 
        height_RM_Young_05103_Alpine_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Height:", index=1) or '' 
        next_Maintenance_RM_Young_05103_Alpine_2 = get_sibling_text_by_label_from_id_index(soup, "rm_young_05103-45", "Next Maintenance:", index=1) or '' 

        sensor_name_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id_index(soup, "tb3", "Sensor:", index=0) or ''
        install_date_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id_index(soup, "tb3", "Install Date:", index=0) or ''
        measures_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id_index(soup, "tb3", "Measures:", index=0) or ''
        last_maintenance_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id_index(soup, "tb3", "Last Maintenance:", index=0) or ''
        height_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id_index(soup, "tb3", "Height:", index=0) or ''
        next_Maintenance_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id_index(soup, "tb3", "Next Maintenance:", index=0) or ''

        sensor_name_Vaisala_WXT_520 = get_sibling_text_by_label_from_id_index(soup, "wxt-520", "Sensor:", index=0) or ''
        install_date_Vaisala_WXT_520 = get_sibling_text_by_label_from_id_index(soup, "wxt-520", "Install Date:", index=0) or ''
        measures_Vaisala_WXT_520 = get_sibling_text_by_label_from_id_index(soup, "wxt-520", "Measures:", index=0) or ''
        last_maintenance_Vaisala_WXT_520 = get_sibling_text_by_label_from_id_index(soup, "wxt-520", "Last Maintenance:", index=0) or ''
        height_Vaisala_WXT_520 = get_sibling_text_by_label_from_id_index(soup, "wxt-520", "Height:", index=0) or ''
        next_Maintenance_Vaisala_WXT_520 = get_sibling_text_by_label_from_id_index(soup, "wxt-520", "Next Maintenance:", index=0) or ''

        sensor_name_Vaisala_WXT_536 = get_sibling_text_by_label_from_id_index(soup, "wxt-536", "Sensor:", index=0) or ''
        install_date_Vaisala_WXT_536 = get_sibling_text_by_label_from_id_index(soup, "wxt-536", "Install Date:", index=0) or ''
        measures_Vaisala_WXT_536 = get_sibling_text_by_label_from_id_index(soup, "wxt-536", "Measures:", index=0) or ''
        last_maintenance_Vaisala_WXT_536 = get_sibling_text_by_label_from_id_index(soup, "wxt-536", "Last Maintenance:", index=0) or ''
        height_Vaisala_WXT_536 = get_sibling_text_by_label_from_id_index(soup, "wxt-536", "Height:", index=0) or ''
        next_Maintenance_Vaisala_WXT_536 = get_sibling_text_by_label_from_id_index(soup, "wxt-536", "Next Maintenance:", index=0) or ''

        sensor_name_Campbell_Scientific_HygroVue10 = get_sibling_text_by_label_from_id_index(soup, "hygrovue10", "Sensor:", index=0) or ''
        install_date_Campbell_Scientific_HygroVue10 = get_sibling_text_by_label_from_id_index(soup, "hygrovue10", "Install Date:", index=0) or ''
        measures_Campbell_Scientific_HygroVue10 = get_sibling_text_by_label_from_id_index(soup, "hygrovue10", "Measures:", index=0) or ''
        last_maintenance_Campbell_Scientific_HygroVue10 = get_sibling_text_by_label_from_id_index(soup, "hygrovue10", "Last Maintenance:", index=0) or ''
        height_Campbell_Scientific_HygroVue10 = get_sibling_text_by_label_from_id_index(soup, "hygrovue10", "Height:", index=0) or ''
        next_Maintenance_Campbell_Scientific_HygroVue10 = get_sibling_text_by_label_from_id_index(soup, "hygrovue10", "Next Maintenance:", index=0) or ''

        sensor_name_Texas_Electronics_525 = get_sibling_text_by_label_from_id_index(soup, "te-525", "Sensor:", index=0) or ''
        install_date_Texas_Electronics_525 = get_sibling_text_by_label_from_id_index(soup, "te-525", "Install Date:", index=0) or ''
        measures_Texas_Electronics_525 = get_sibling_text_by_label_from_id_index(soup, "te-525", "Measures:", index=0) or ''
        last_maintenance_Texas_Electronics_525 = get_sibling_text_by_label_from_id_index(soup, "te-525", "Last Maintenance:", index=0) or ''
        height_Texas_Electronics_525 = get_sibling_text_by_label_from_id_index(soup, "te-525", "Height:", index=0) or ''
        next_Maintenance_Texas_Electronics_525 = get_sibling_text_by_label_from_id_index(soup, "te-525", "Next Maintenance:", index=0) or ''

# https://econet.climate.ncsu.edu/m/?id=FRYI

        time.sleep(3)
        data_sensor = {
            "Apogee Instruments SP 510 Sensor": sensor_name_Apogee_Instruments_SP_510,
            "Apogee Instruments SP 510 Install Date": install_date_Apogee_Instruments_SP_510,
            "Apogee Instruments SP 510 Measures": measures_Apogee_Instruments_SP_510,
            "Apogee Instruments SP 510 Last Maintenance": last_maintenance_Apogee_Instruments_SP_510,
            "Apogee Instruments SP 510 Height": height_Apogee_Instruments_SP_510,
            "Apogee Instruments SP 510 Next Maintenance": next_Maintenance_Apogee_Instruments_SP_510,
            
            "Apogee Instruments SQ 110 Sensor": sensor_name_Apogee_Instruments_SQ_110,
            "Apogee Instruments SQ 110 Install Date": install_date_Apogee_Instruments_SQ_110,
            "Apogee Instruments SQ 110 Measures": measures_Apogee_Instruments_SQ_110,
            "Apogee Instruments SQ 110 Last Maintenance": last_maintenance_Apogee_Instruments_SQ_110,
            "Apogee Instruments SQ 110 Height": height_Apogee_Instruments_SQ_110,
            "Apogee Instruments SQ 110 Next Maintenance": next_Maintenance_Apogee_Instruments_SQ_110,
            
            "Apogee Instruments SQ 110 Sensor Get Second": sensor_name_Apogee_Instruments_SQ_110_2,
            "Apogee Instruments SQ 110 Install Date Get Second": install_date_Apogee_Instruments_SQ_110_2,
            "Apogee Instruments SQ 110 Measures Get Second": measures_Apogee_Instruments_SQ_110_2,
            "Apogee Instruments SQ 110 Last Maintenance Get Second": last_maintenance_Apogee_Instruments_SQ_110_2,
            "Apogee Instruments SQ 110 Height Get Second": height_Apogee_Instruments_SQ_110_2,
            "Apogee Instruments SQ 110 Next Maintenance Get Second": next_Maintenance_Apogee_Instruments_SQ_110_2,
            
            "Campbell Scientific CR1000 Sensor": sensor_name_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Install Date": install_date_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Measures": measures_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Last Maintenance": last_maintenance_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Height": height_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Next Maintenance": next_Maintenance_Campbell_Scientific_CR1000,
            
            "Campbell Scientific CR1000X Sensor": sensor_name_Campbell_Scientific_CR1000X,
            "Campbell Scientific CR1000X Install Date": install_date_Campbell_Scientific_CR1000X,
            "Campbell Scientific CR1000X Measures": measures_Campbell_Scientific_CR1000X,
            "Campbell Scientific CR1000X Last Maintenance": last_maintenance_Campbell_Scientific_CR1000X,
            "Campbell Scientific CR1000X Height": height_Campbell_Scientific_CR1000X,
            "Campbell Scientific CR1000X Next Maintenance": next_Maintenance_Campbell_Scientific_CR1000X,
            
            "Campbell Scientific 109 Sensor": sensor_name_Campbell_Scientific_109,
            "Campbell Scientific 109 Install Date": install_date_Campbell_Scientific_109,
            "Campbell Scientific 109 Measures": measures_Campbell_Scientific_109,
            "Campbell Scientific 109 Last Maintenance": last_maintenance_Campbell_Scientific_109,
            "Campbell Scientific 109 Height": height_Campbell_Scientific_109,
            "Campbell Scientific 109 Depth": depth_Campbell_Scientific_109,
            "Campbell Scientific 109 Next Maintenance": next_Maintenance_Campbell_Scientific_109,
            
            "Campbell Scientific 109 Sensor Get Second": sensor_name_Campbell_Scientific_109_2,
            "Campbell Scientific 109 Install Date Get Second": install_date_Campbell_Scientific_109_2,
            "Campbell Scientific 109 Measures Get Second": measures_Campbell_Scientific_109_2,
            "Campbell Scientific 109 Last Maintenance Get Second": last_maintenance_Campbell_Scientific_109_2,
            "Campbell Scientific 109 Height Get Second": height_Campbell_Scientific_109_2,
            "Campbell Scientific 109 Next Maintenance Get Second": next_Maintenance_Campbell_Scientific_109_2,
            
            "Campbell Scientific Black Globe Thermometer Sensor": sensor_name_Campbell_Scientific_Black_Globe_Thermometer,
            "Campbell Scientific Black Globe Thermometer Install Date": install_date_Campbell_Scientific_Black_Globe_Thermometer,
            "Campbell Scientific Black Globe Thermometer Measures": measures_Campbell_Scientific_Black_Globe_Thermometer,
            "Campbell Scientific Black Globe Thermometer Last Maintenance": last_maintenance_Campbell_Scientific_Black_Globe_Thermometer,
            "Campbell Scientific Black Globe Thermometer Height": height_Campbell_Scientific_Black_Globe_Thermometer,
            "Campbell Scientific Black Globe Thermometer Next Maintenance": next_Maintenance_Campbell_Scientific_Black_Globe_Thermometer,
            
            "METER Leaf Wetness Senso Sensor": sensor_name_METER_Leaf_Wetness_Senso,
            "METER Leaf Wetness Senso Install Date": install_date_METER_Leaf_Wetness_Senso,
            "METER Leaf Wetness Senso Measures": measures_METER_Leaf_Wetness_Senso,
            "METER Leaf Wetness Senso Last Maintenance": last_maintenance_METER_Leaf_Wetness_Senso,
            "METER Leaf Wetness Senso Height": height_METER_Leaf_Wetness_Senso,
            "METER Leaf Wetness Senso Next Maintenance": next_Maintenance_METER_Leaf_Wetness_Senso,
            
            "Delta-T ML3 Sensor": sensor_name_Delta_T_ML3,
            "Delta-T ML3 Install Date": install_date_Delta_T_ML3,
            "Delta-T ML3 Measures": measures_Delta_T_ML3,
            "Delta-T ML3 Last Maintenance": last_maintenance_Delta_T_ML3,
            "Delta-T ML3 Height": height_Delta_T_ML3,
            "Delta-T ML3 Next Maintenance": next_Maintenance_Delta_T_ML3,
            "Delta-T ML3 Depth": depth_Delta_T_ML3,
            
            "Delta-T ML2x Sensor": sensor_name_Delta_TML2x,
            "Delta-T ML2x Install Date": install_date_Delta_TML2x,
            "Delta-T ML2x Measures": measures_Delta_TML2x,
            "Delta-T ML2x Last Maintenance": last_maintenance_Delta_TML2x,
            "Delta-T ML2x Height": height_Delta_TML2x,
            "Delta-T ML2x Next Maintenance": next_Maintenance_Delta_TML2x,
            "Delta-T ML2x Depth": depth_Delta_TML2x,
            
            "Vaisala HMP155 Sensor": sensor_name_Vaisala_HMP155,
            "Vaisala HMP155 Install Date": install_date_Vaisala_HMP155,
            "Vaisala HMP155 Measures": measures_Vaisala_HMP155,
            "Vaisala HMP155 Last Maintenance": last_maintenance_Vaisala_HMP155,
            "Vaisala HMP155 Height": height_Vaisala_HMP155,
            "Vaisala HMP155 Next Maintenance": next_Maintenance_Vaisala_HMP155,
            
            "RM Young 05103 Sensor": sensor_name_RM_Young_05103,
            "RM Young 05103 Install Date": install_date_RM_Young_05103,
            "RM Young 05103 Measures": measures_RM_Young_05103,
            "RM Young 05103 Last Maintenance": last_maintenance_RM_Young_05103,
            "RM Young 05103 Height": height_RM_Young_05103,
            "RM Young 05103 Next Maintenance": next_Maintenance_RM_Young_05103,
            
            "RM Young 05103 Sensor Get Second": sensor_name_RM_Young_05103_2,
            "RM Young 05103 Install Date Get Second": install_date_RM_Young_05103_2,
            "RM Young 05103 Measures Get Second": measures_RM_Young_05103_2,
            "RM Young 05103 Last Maintenance Get Second": last_maintenance_RM_Young_05103_2,
            "RM Young 05103 Height Get Second": height_RM_Young_05103_2,
            "RM Young 05103 Next Maintenance Get Second": next_Maintenance_RM_Young_05103_2,
            
            "RM Young 05103 (Alpine) Sensor": sensor_name_RM_Young_05103_Alpine,
            "RM Young 05103 (Alpine) Install Date": install_date_RM_Young_05103_Alpine,
            "RM Young 05103 (Alpine) Measures": measures_RM_Young_05103_Alpine,
            "RM Young 05103 (Alpine) Last Maintenance": last_maintenance_RM_Young_05103_Alpine,
            "RM Young 05103 (Alpine) Height": height_RM_Young_05103_Alpine,
            "RM Young 05103 (Alpine) Next Maintenance": next_Maintenance_RM_Young_05103_Alpine,
            
            "RM Young 05103 (Alpine) Sensor Get Second": sensor_name_RM_Young_05103_Alpine_2,
            "RM Young 05103 (Alpine) Install Date Get Second": install_date_RM_Young_05103_Alpine_2,
            "RM Young 05103 (Alpine) Measures Get Second": measures_RM_Young_05103_Alpine_2,
            "RM Young 05103 (Alpine) Last Maintenance Get Second": last_maintenance_RM_Young_05103_Alpine_2,
            "RM Young 05103 (Alpine) Height Get Second": height_RM_Young_05103_Alpine_2,
            "RM Young 05103 (Alpine) Next Maintenance Get Second": next_Maintenance_RM_Young_05103_Alpine_2,
            
            "Hydrological Services TB3 Sensor": sensor_name_Hydrological_Services_TB3,
            "Hydrological Services TB3 Install Date": install_date_Hydrological_Services_TB3,
            "Hydrological Services TB3 Measures": measures_Hydrological_Services_TB3,
            "Hydrological Services TB3 Last Maintenance": last_maintenance_Hydrological_Services_TB3,
            "Hydrological Services TB3 Height": height_Hydrological_Services_TB3,
            "Hydrological Services TB3 Next Maintenance": next_Maintenance_Hydrological_Services_TB3,
            
            "Vaisala WXT-520 Sensor": sensor_name_Vaisala_WXT_520,
            "Vaisala WXT-520 Install Date": install_date_Vaisala_WXT_520,
            "Vaisala WXT-520 Measures": measures_Vaisala_WXT_520,
            "Vaisala WXT-520 Last Maintenance": last_maintenance_Vaisala_WXT_520,
            "Vaisala WXT-520 Height": height_Vaisala_WXT_520,
            "Vaisala WXT-520 Next Maintenance": next_Maintenance_Vaisala_WXT_520,
            
            "Vaisala WXT-536 Sensor": sensor_name_Vaisala_WXT_536,
            "Vaisala WXT-536 Install Date": install_date_Vaisala_WXT_536,
            "Vaisala WXT-536 Measures": measures_Vaisala_WXT_536,
            "Vaisala WXT-536 Last Maintenance": last_maintenance_Vaisala_WXT_536,
            "Vaisala WXT-536 Height": height_Vaisala_WXT_536,
            "Vaisala WXT-536 Next Maintenance": next_Maintenance_Vaisala_WXT_536,
            
            "Campbell Scientific HygroVue10 Sensor": sensor_name_Campbell_Scientific_HygroVue10,
            "Campbell Scientific HygroVue10 Install Date": install_date_Campbell_Scientific_HygroVue10,
            "Campbell Scientific HygroVue10 Measures": measures_Campbell_Scientific_HygroVue10,
            "Campbell Scientific HygroVue10 Last Maintenance": last_maintenance_Campbell_Scientific_HygroVue10,
            "Campbell Scientific HygroVue10 Height": height_Campbell_Scientific_HygroVue10,
            "Campbell Scientific HygroVue10 Next Maintenance": next_Maintenance_Campbell_Scientific_HygroVue10,
            
            "Texas Electronics 525 Sensor": sensor_name_Texas_Electronics_525,
            "Texas Electronics 525 Install Date": install_date_Texas_Electronics_525,
            "Texas Electronics 525 Measures": measures_Texas_Electronics_525,
            "Texas Electronics 525 Last Maintenance": last_maintenance_Texas_Electronics_525,
            "Texas Electronics 525 Height": height_Texas_Electronics_525,
            "Texas Electronics 525 Next Maintenance": next_Maintenance_Texas_Electronics_525,


        }
        time.sleep(2)
        return data_sensor
    
    except Exception as e:
        print(f"❌ Gagal mengklik tab 'Sensor': {e}")
        return None
    
        # open_urls_with_selenium(driver)
        
# if not sensor(driver):
#     open_urls_with_selenium(driver)


# def open_urls_with_selenium(data):
#     """Buka setiap URL berdasarkan ID menggunakan Selenium."""
#     service = Service()  # Sesuaikan path jika perlu
#     options = Options()
#     options.add_argument('--start-maximized')
#     # options.add_argument('--headless')  # Aktifkan jika tidak ingin membuka browser

#     driver = webdriver.Chrome(service=service, options=options)

#     try:
#         for i, item in enumerate(data, start=1):
#             station_id = item.get("id")
#             if station_id:
#                 url = f"https://econet.climate.ncsu.edu/m/?id={station_id}"
#                 print(f"[{i}] 🌐 Membuka URL: {url}")
#                 driver.get(url)
#                 time.sleep(3)

#                 close_modal_if_exists(driver)
#                 # station(driver)
#                 # sensor(driver)
#                 # media(driver)

#                 station_data = station(driver)
#                 sensor_data = sensor(driver)
#                 # Gabungkan data station dan sensor
#                 combined_data = {**station_data, **sensor_data}

#                 # Simpan ke CSV
#                 save_station_data(combined_data)

#     finally:
#         driver.quit()
#         print("✅ Semua halaman telah dibuka.")

# def open_urls_with_selenium(data):
#     """Buka setiap URL berdasarkan ID menggunakan Selenium, mulai dari indeks ke-6."""
#     service = Service()  # Sesuaikan path jika perlu
#     options = Options()
#     options.add_argument('--start-maximized')
#     # options.add_argument('--headless')  # Aktifkan jika tidak ingin membuka browser

#     driver = webdriver.Chrome(service=service, options=options)

#     try:
#         # Mulai dari indeks ke-6 (yaitu index = 5)
#         for i, item in enumerate(data[index__:], start=index__ + 1):
#             station_id = item.get("id")
#             if station_id:
#                 url = f"https://econet.climate.ncsu.edu/m/?id={station_id}"
#                 print(f"[{i}] 🌐 Membuka URL: {url}")
#                 driver.get(url)
#                 time.sleep(3)

#                 close_modal_if_exists(driver)
#                 station_data = station(driver)
#                 sensor_data = sensor(driver)

#                 # Gabungkan data station dan sensor
#                 combined_data = {**station_data, **sensor_data}

#                 # Simpan ke CSV
#                 save_station_data(combined_data)

#     finally:
#         driver.quit()
#         print("✅ Semua halaman telah dibuka.")


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

                # Jalankan kedua fungsi
                station_data = station(driver)
                sensor_data = sensor(driver)

                # Gabungkan hanya jika tidak None
                combined_data = {}
                if station_data:
                    combined_data.update(station_data)
                if sensor_data:
                    combined_data.update(sensor_data)

                # Simpan jika ada data
                if combined_data:
                    save_station_data(combined_data)
                else:
                    print(f"⚠️ Tidak ada data yang ditemukan untuk ID: {station_id}")

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
