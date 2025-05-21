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


def save_station_data(data, filename="station_data.csv"):
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


def station(driver):
    try:
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

        # Parse HTML setelah elemen benar-benar muncul
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')



        station_name = get_sibling_text_by_label(soup, "Station Name (ID)")
        if station_name:
            print(f"📅 Stations Name: {station_name}")
        else:
            print(f"❌ Tidak menemukan informasi '{station_name}'.")

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



def sensor(driver):
    """Klik tab 'Sensors'."""
    try:
        time.sleep(1)  # Beri waktu DOM stabil

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


        sensor_html = driver.page_source
        soup = BeautifulSoup(sensor_html, 'html.parser')

        sensor_name_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id(soup, "apogee_sp-510", "Sensor:")
        install_date_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id(soup, "apogee_sp-510", "Install Date:")
        measures_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id(soup, "apogee_sp-510", "Measures:")
        last_maintenance_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id(soup, "apogee_sp-510", "Last Maintenance:")
        height_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id(soup, "apogee_sp-510", "Height:")
        next_Maintenance_Apogee_Instruments_SP_510 = get_sibling_text_by_label_from_id(soup, "apogee_sp-510", "Next Maintenance:")


        sensor_name_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id(soup, "apogee_sq-110", "Sensor:")
        install_date_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id(soup, "apogee_sq-110", "Install Date:")
        measures_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id(soup, "apogee_sq-110", "Measures:")
        last_maintenance_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id(soup, "apogee_sq-110", "Last Maintenance:")
        height_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id(soup, "apogee_sq-110", "Height:")
        next_Maintenance_Apogee_Instruments_SQ_110 = get_sibling_text_by_label_from_id(soup, "apogee_sq-110", "Next Maintenance:")


        sensor_name_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id(soup, "cr1000", "Sensor:")
        install_date_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id(soup, "cr1000", "Install Date:")
        measures_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id(soup, "cr1000", "Measures:")
        last_maintenance_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id(soup, "cr1000", "Last Maintenance:")
        height_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id(soup, "cr1000", "Height:")
        next_Maintenance_Campbell_Scientific_CR1000 = get_sibling_text_by_label_from_id(soup, "cr1000", "Next Maintenance:")


        sensor_name_Campbell_Scientific_109 = get_sibling_text_by_label_from_id(soup, "cs_109-l", "Sensor:")
        install_date_Campbell_Scientific_109 = get_sibling_text_by_label_from_id(soup, "cs_109-l", "Install Date:")
        measures_Campbell_Scientific_109 = get_sibling_text_by_label_from_id(soup, "cs_109-l", "Measures:")
        last_maintenance_Campbell_Scientific_109 = get_sibling_text_by_label_from_id(soup, "cs_109-l", "Last Maintenance:")
        height_Campbell_Scientific_109 = get_sibling_text_by_label_from_id(soup, "cs_109-l", "Height:")
        next_Maintenance_Campbell_Scientific_109 = get_sibling_text_by_label_from_id(soup, "cs_109-l", "Next Maintenance:")

        sensor_name_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id(soup, "cs_bgt", "Sensor:")
        install_date_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id(soup, "cs_bgt", "Install Date:")
        measures_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id(soup, "cs_bgt", "Measures:")
        last_maintenance_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id(soup, "cs_bgt", "Last Maintenance:")
        height_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id(soup, "cs_bgt", "Height:")
        next_Maintenance_Campbell_Scientific_Black_Globe_Thermometer = get_sibling_text_by_label_from_id(soup, "cs_bgt", "Next Maintenance:")

        sensor_name_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id(soup, "decagon_lws", "Sensor:")
        install_date_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id(soup, "decagon_lws", "Install Date:")
        measures_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id(soup, "decagon_lws", "Measures:")
        last_maintenance_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id(soup, "decagon_lws", "Last Maintenance:")
        height_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id(soup, "decagon_lws", "Height:")
        next_Maintenance_METER_Leaf_Wetness_Senso = get_sibling_text_by_label_from_id(soup, "decagon_lws", "Next Maintenance:")

        sensor_name_Delta_T_ML3 = get_sibling_text_by_label_from_id(soup, "delta-t_ml3", "Sensor:")
        install_date_Delta_T_ML3 = get_sibling_text_by_label_from_id(soup, "delta-t_ml3", "Install Date:")
        measures_Delta_T_ML3 = get_sibling_text_by_label_from_id(soup, "delta-t_ml3", "Measures:")
        last_maintenance_Delta_T_ML3 = get_sibling_text_by_label_from_id(soup, "delta-t_ml3", "Last Maintenance:")
        height_Delta_T_ML3 = get_sibling_text_by_label_from_id(soup, "delta-t_ml3", "Height:")
        next_Maintenance_Delta_T_ML3 = get_sibling_text_by_label_from_id(soup, "delta-t_ml3", "Next Maintenance:")

        sensor_name_Vaisala_HMP155 = get_sibling_text_by_label_from_id(soup, "hmp-155", "Sensor:")
        install_date_Vaisala_HMP155 = get_sibling_text_by_label_from_id(soup, "hmp-155", "Install Date:")
        measures_Vaisala_HMP155 = get_sibling_text_by_label_from_id(soup, "hmp-155", "Measures:")
        last_maintenance_Vaisala_HMP155 = get_sibling_text_by_label_from_id(soup, "hmp-155", "Last Maintenance:")
        height_Vaisala_HMP155 = get_sibling_text_by_label_from_id(soup, "hmp-155", "Height:")
        next_Maintenance_Vaisala_HMP155 = get_sibling_text_by_label_from_id(soup, "hmp-155", "Next Maintenance:")

        sensor_name_RM_Young_05103 = get_sibling_text_by_label_from_id(soup, "rm_young_05103", "Sensor:")
        install_date_RM_Young_05103 = get_sibling_text_by_label_from_id(soup, "rm_young_05103", "Install Date:")
        measures_RM_Young_05103 = get_sibling_text_by_label_from_id(soup, "rm_young_05103", "Measures:")
        last_maintenance_RM_Young_05103 = get_sibling_text_by_label_from_id(soup, "rm_young_05103", "Last Maintenance:")
        height_RM_Young_05103 = get_sibling_text_by_label_from_id(soup, "rm_young_05103", "Height:")
        next_Maintenance_RM_Young_05103 = get_sibling_text_by_label_from_id(soup, "rm_young_05103", "Next Maintenance:")

        sensor_name_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id(soup, "tb3", "Sensor:")
        install_date_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id(soup, "tb3", "Install Date:")
        measures_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id(soup, "tb3", "Measures:")
        last_maintenance_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id(soup, "tb3", "Last Maintenance:")
        height_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id(soup, "tb3", "Height:")
        next_Maintenance_Hydrological_Services_TB3 = get_sibling_text_by_label_from_id(soup, "tb3", "Next Maintenance:")

        sensor_name_Vaisala_WXT_520 = get_sibling_text_by_label_from_id(soup, "wxt-520", "Sensor:")
        install_date_Vaisala_WXT_520 = get_sibling_text_by_label_from_id(soup, "wxt-520", "Install Date:")
        measures_Vaisala_WXT_520 = get_sibling_text_by_label_from_id(soup, "wxt-520", "Measures:")
        last_maintenance_Vaisala_WXT_520 = get_sibling_text_by_label_from_id(soup, "wxt-520", "Last Maintenance:")
        height_Vaisala_WXT_520 = get_sibling_text_by_label_from_id(soup, "wxt-520", "Height:")
        next_Maintenance_Vaisala_WXT_520 = get_sibling_text_by_label_from_id(soup, "wxt-520", "Next Maintenance:")



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
            
            "Campbell Scientific CR1000 Sensor": sensor_name_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Install Date": install_date_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Measures": measures_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Last Maintenance": last_maintenance_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Height": height_Campbell_Scientific_CR1000,
            "Campbell Scientific CR1000 Next Maintenance": next_Maintenance_Campbell_Scientific_CR1000,
            
            "Campbell Scientific 109 Sensor": sensor_name_Campbell_Scientific_109,
            "Campbell Scientific 109 Install Date": install_date_Campbell_Scientific_109,
            "Campbell Scientific 109 Measures": measures_Campbell_Scientific_109,
            "Campbell Scientific 109 Last Maintenance": last_maintenance_Campbell_Scientific_109,
            "Campbell Scientific 109 Height": height_Campbell_Scientific_109,
            "Campbell Scientific 109 Next Maintenance": next_Maintenance_Campbell_Scientific_109,
            
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


        }
        return data_sensor

    except Exception as e:
        print(f"❌ Gagal mengklik tab 'Sensor': {e}")





def open_urls_with_selenium(data):
    """Buka setiap URL berdasarkan ID menggunakan Selenium."""
    service = Service()  # Sesuaikan path jika perlu
    options = Options()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # Aktifkan jika tidak ingin membuka browser

    driver = webdriver.Chrome(service=service, options=options)

    try:
        for i, item in enumerate(data, start=1):
            station_id = item.get("id")
            if station_id:
                url = f"https://econet.climate.ncsu.edu/m/?id={station_id}"
                print(f"[{i}] 🌐 Membuka URL: {url}")
                driver.get(url)
                time.sleep(3)

                close_modal_if_exists(driver)
                station(driver)
                sensor(driver)

                station_data = station(driver)
                sensor_data = sensor(driver)
                # Gabungkan data station dan sensor
                combined_data = {**station_data, **sensor_data}

                # Simpan ke CSV
                save_station_data(combined_data)

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
