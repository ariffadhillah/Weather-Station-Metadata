import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re
import time

BASE_URL = "https://azmet.arizona.edu/about/station-metadata"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

# def extract_sensor_info(soup):
#     data = []

#     # Cari semua <div class="card-body">
#     card_bodies = soup.find_all("div", class_="card-body")

#     for card in card_bodies:
#         section = card.find("h4")
#         if not section:
#             continue

#         section_name = section.get_text(strip=True)
#         sensor_info = {"Section": section_name}

#         # Cari semua <span> di dalam card
#         spans = card.find_all("span")

#         for span in spans:
#             label = span.get_text(strip=True).rstrip(":")  # Misal: "SENSOR", "SENSOR HEIGHT"
#             value = ""

#             # Ambil sibling text (bisa berupa NavigableString atau tag lainnya)
#             next_sibling = span.next_sibling
#             while next_sibling and not isinstance(next_sibling, str):
#                 next_sibling = next_sibling.next_sibling

#             if next_sibling:
#                 value = next_sibling.strip()

#             sensor_info[label] = value

#         data.append(sensor_info)

#     return data


def save_to_csv(data, filename="University of Arizona.csv"):
    file_exists = os.path.isfile(filename)

    # Urutan kolom yang diinginkan
    field_order = [
        "Station Name", "Symbol", "Station ID", "County", "Latitude", "Longitude",
        "Elevation (ft)", "Elevation (m)", "Status", "Description",
        
        # Sensor Data (pastikan sesuai dengan kombinasi key dari data hasil parsing)
        "Sensor Air Temperature", "Sensor Height Air Temperature",
        "Sensor Precipitation", "Sensor Height Precipitation",
        "Sensor Relative Humidity", "Sensor Height Relative Humidity",
        "Sensor 1 Relative Humidity", "Sensor 1 Depth Relative Humidity",
        "Sensor 2 Relative Humidity", "Sensor 2 Depth Relative Humidity",
        "Sensor Solar Radiation", "Sensor Height Solar Radiation",
        "Direction Sensor Wind", "Direction Height Sensor Wind",
        "Speed Sensor Wind", "Speed Sensor Height Wind",
        "Data Transmission Frequency Measurements", "Data Data Logger Measurements",
        "Sensor Scan Frequency Measurements",
        "Start Date Previous Locations", "End Date Previous Locations",
        "Latitude Previous Locations", "Longitude Previous Locations", "Elevation Previous Locations"
    ]

    # Hanya gunakan field yang tersedia di data
    actual_fields = [field for field in field_order if field in data]

    with open(filename, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=actual_fields)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

    print(f"💾 Data disimpan: {data.get('Station Name')}")




def extract_sensor_info(soup):
    all_card_data = []

    cards = soup.find_all("div", class_="card-body")
    for card in cards:
        section_title_tag = card.find("h4", class_="my-0")
        if not section_title_tag:
            continue

        section_name = section_title_tag.get_text(strip=True)
        info_dict = {"Section": section_name}

        # Ambil semua span dan text setelahnya
        spans = card.find_all("span")
        for span in spans:
            label = span.get_text(strip=True).strip(":").upper()
            # ambil text setelah <span> (yaitu next_sibling)
            value = span.next_sibling
            if value:
                text = value.strip()
                if text:
                    info_dict[label] = text

        all_card_data.append(info_dict)

    return all_card_data


def extract_table_data(soup):
    table = soup.find('table', class_='table table-striped table-bordered table-hover cols-10 p-2')
    if not table:
        print("❌ Tabel tidak ditemukan.")
        return []

    rows = table.find_all('tr')
    data_list = []

    for row in rows[1:]:  # Skip header
        cols = row.find_all('td')
        if len(cols) < 10:
            continue  # Skip jika kolom tidak lengkap

        data = {
            "Station Name": cols[0].get_text(strip=True),
            "Symbol": cols[1].get_text(strip=True),
            "Station ID": cols[2].get_text(strip=True),
            "County": cols[3].get_text(strip=True),
            "Latitude": cols[4].get_text(strip=True),
            "Longitude": cols[5].get_text(strip=True),
            "Elevation (ft)": cols[6].get_text(strip=True),
            "Elevation (m)": cols[7].get_text(strip=True),
            "Status": cols[8].get_text(strip=True),
            "Description": cols[9].get_text(strip=True),
        }
        data_list.append(data)

    return data_list


# def parse_station_detail(station_id):
#     detail_url = f"https://azmet.arizona.edu/about/station-metadata/{station_id}"
#     print(f"\n🌐 Membuka URL: {detail_url}")

#     html = get_html(detail_url)
#     if not html:
#         print(f"❌ Gagal mengambil halaman detail untuk station_id: {station_id}")
#         return

#     soup = BeautifulSoup(html, 'html.parser')

#     title = soup.find('h2', class_='my-0 bold text-midnight')
#     print(title.text.strip())

#     sensor_data = extract_sensor_info(soup)

#     # Inisialisasi variabel kosong
#     air_temperature_sensor = None
#     air_temperature_sensor_height = None
#     precipitation_sensor = None
#     precipitation_sensor_height = None
#     relative_humidity_sensor = None
#     relative_humidity_height = None
#     soil_temperature_sensor_1 = None
#     soil_temperature_sensor_1 = None
#     soil_temperature_sensor_1_DEPTH = None
#     soil_temperature_sensor_2 = None
#     soil_temperature_sensor_2_DEPTH = None
#     solar_radiation_sensor = None
#     solar_radiation_sensor_height = None
#     wind_direction_sensor = None
#     wind_direction_height_sensor = None
#     wind_speed_sensor = None
#     wind_speed_height_sensor = None  
#     measurements_data__sensor = None
#     measurements_data_logger = None
#     measurements_sensor_scan_frequency = None
#     start_Date_Previous_Locations = None
#     end_Date_Previous_Locations = None
#     latitude_Previous_Locations = None
#     longitude_Previous_Locations = None
#     elevation_Previous_Locations = None

#     # Loop sekali, ambil kedua data jika ketemu
#     for item in sensor_data:
#         section = item.get("Section", "").lower()

#         if section == "air temperature":
#             air_temperature_sensor = item.get("SENSOR")
#             air_temperature_sensor_height = item.get("SENSOR HEIGHT")

#         elif section == "precipitation":
#             precipitation_sensor = item.get("SENSOR")
#             precipitation_sensor_height = item.get("SENSOR HEIGHT")

#         elif section == "relative humidity":
#             relative_humidity_sensor = item.get("SENSOR")
#             relative_humidity_height = item.get("SENSOR HEIGHT")
    
#         elif section == "soil temperature":
#             soil_temperature_sensor_1 = item.get("SENSOR 1")
#             soil_temperature_sensor_1_DEPTH = item.get("SENSOR 1 DEPTH")
#             soil_temperature_sensor_2 = item.get("SENSOR 2")
#             soil_temperature_sensor_2_DEPTH = item.get("SENSOR 2 DEPTH")
    
#         elif section == "Solar Radiation":
#             solar_radiation_sensor = item.get("SENSOR")
#             solar_radiation_sensor_height = item.get("SENSOR HEIGHT")            
    
#         elif section == "wind":
#             wind_direction_sensor = item.get("DIRECTION SENSOR")
#             wind_direction_height_sensor = item.get("DIRECTION SENSOR HEIGHT")
#             wind_speed_sensor = item.get("SPEED SENSOR")
#             wind_speed_height_sensor = item.get("SPEED SENSOR HEIGHT")
    
#         elif section == "measurements":
#             measurements_data__sensor = item.get("DATA TRANSMISSION FREQUENCY")
#             measurements_data_logger = item.get("DATALOGGER")
#             measurements_sensor_scan_frequency = item.get("SENSOR SCAN FREQUENCY")
    
#         elif section == "Previous Locations":
#             start_Date_Previous_Locations = item.get("Start Date")
#             end_Date_Previous_Locations = item.get("End Date")
#             latitude_Previous_Locations = item.get("Latitude")
#             longitude_Previous_Locations = item.get("Longitude")
#             elevation_Previous_Locations = item.get("Elevation")
            
#     # Tampilkan hasil
#     print("Sensor Air Temperature:", air_temperature_sensor)
#     print("Sensor Height Air Temperature:", air_temperature_sensor_height)
    
#     print("Sensor Precipitation:", precipitation_sensor)
#     print("Sensor Height Precipitation:", precipitation_sensor_height)

#     print("Sensor Relative Humidity:", relative_humidity_sensor)
#     print("Sensor Height Relative Humidity:", relative_humidity_height)

#     print("Sensor 1 Relative Humidity:", soil_temperature_sensor_1)
#     print("Sensor 1 Depth Relative Humidity:", soil_temperature_sensor_1_DEPTH)
#     print("Sensor 2 Relative Humidity:", soil_temperature_sensor_2)
#     print("Sensor 2 Depth relative Humidity:", soil_temperature_sensor_2_DEPTH)

#     print("Sensor Solar Radiation:", solar_radiation_sensor)
#     print("Sensor Height Solar Radiation:", solar_radiation_sensor_height)

#     print("Direction Sensor Wind:", wind_direction_sensor)
#     print("Direction Height Sensor Wind:", wind_direction_height_sensor)
#     print("Speed Sensor Wind:", wind_speed_sensor)
#     print("Speed Sensor Height Wind:", wind_speed_height_sensor)
    
#     print("Data Transmission Frequency Measurements:", measurements_data__sensor)
#     print("Data Data Logger Measurements:", measurements_data_logger)
#     print("Data Transmission Frequency Measurements:", measurements_sensor_scan_frequency)
    
#     print("Start Date Previous Locations:", start_Date_Previous_Locations)
#     print("End Date Previous Locations:", end_Date_Previous_Locations)
#     print("Latitude Previous Locations:", latitude_Previous_Locations)
#     print("Start Date Previous Locations:", longitude_Previous_Locations)
#     print("Start Date Previous Locations:", elevation_Previous_Locations)


def get_station_detail_dict(station_id):
    detail_url = f"https://azmet.arizona.edu/about/station-metadata/{station_id}"
    print(f"🔍 Mengakses detail URL: {detail_url}")  # Tambahan untuk debug
    html = get_html(detail_url)
    if not html:
        print(f"❌ Gagal membuka: {detail_url}")
        return {}

    soup = BeautifulSoup(html, 'html.parser')
    sensor_data = extract_sensor_info(soup)
    result = {}

    for item in sensor_data:
        section = item.get("Section", "").lower()
        if section == "air temperature":
            result["Sensor Air Temperature"] = item.get("SENSOR")
            result["Sensor Height Air Temperature"] = item.get("SENSOR HEIGHT")
        elif section == "precipitation":
            result["Sensor Precipitation"] = item.get("SENSOR")
            result["Sensor Height Precipitation"] = item.get("SENSOR HEIGHT")
        elif section == "relative humidity":
            result["Sensor Relative Humidity"] = item.get("SENSOR")
            result["Sensor Height Relative Humidity"] = item.get("SENSOR HEIGHT")
        elif section == "soil temperature":
            result["Sensor 1 Relative Humidity"] = item.get("SENSOR 1")
            result["Sensor 1 Depth Relative Humidity"] = item.get("SENSOR 1 DEPTH")
            result["Sensor 2 Relative Humidity"] = item.get("SENSOR 2")
            result["Sensor 2 Depth Relative Humidity"] = item.get("SENSOR 2 DEPTH")
        elif section == "solar radiation":
            result["Sensor Solar Radiation"] = item.get("SENSOR")
            result["Sensor Height Solar Radiation"] = item.get("SENSOR HEIGHT")
        elif section == "wind":
            result["Direction Sensor Wind"] = item.get("DIRECTION SENSOR")
            result["Direction Height Sensor Wind"] = item.get("DIRECTION SENSOR HEIGHT")
            result["Speed Sensor Wind"] = item.get("SPEED SENSOR")
            result["Speed Sensor Height Wind"] = item.get("SPEED SENSOR HEIGHT")
        elif section == "measurements":
            result["Data Transmission Frequency Measurements"] = item.get("DATA TRANSMISSION FREQUENCY")
            result["Data Data Logger Measurements"] = item.get("DATALOGGER")
            result["Sensor Scan Frequency Measurements"] = item.get("SENSOR SCAN FREQUENCY")
        elif section == "previous locations":
            result["Start Date Previous Locations"] = item.get("Start Date")
            result["End Date Previous Locations"] = item.get("End Date")
            result["Latitude Previous Locations"] = item.get("Latitude")
            result["Longitude Previous Locations"] = item.get("Longitude")
            result["Elevation Previous Locations"] = item.get("Elevation")

    return result

def combine_station_data(station_basic_data):
    station_id = station_basic_data.get("Station ID")
    print(f"🔄 Menggabungkan data untuk Station ID: {station_id}")
    detail_data = get_station_detail_dict(station_id)
    combined_data = {**station_basic_data, **detail_data}
    return combined_data




def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    station_data = extract_table_data(soup)

    for entry in station_data:
        print(entry)





# def main():
#     base_html = get_html(BASE_URL)
#     if not base_html:
#         print("Gagal mendapatkan HTML awal.")
#         return

#     soup = BeautifulSoup(base_html, 'html.parser')
#     stations = extract_table_data(soup)

#     for station in stations:
#         station_id = station.get("Station ID")
#         if station_id:
#             parse_station_detail(station_id)
#             time.sleep(2)  # Hindari terlalu cepat ke server


def main():
    base_html = get_html(BASE_URL)
    if not base_html:
        print("Gagal mendapatkan HTML awal.")
        return

    soup = BeautifulSoup(base_html, 'html.parser')
    stations = extract_table_data(soup)

    for i, station in enumerate(stations, 1):
        station_id = station.get("Station ID")
        print(f"\n📍 [{i}/{len(stations)}] Memproses station: {station.get('Station Name')} - ID: {station_id}")
        if station_id:
            combined_data = combine_station_data(station)
            save_to_csv(combined_data, filename="stations_data.csv")  # Simpan langsung
            time.sleep(2)  # Hindari hit server terlalu cepat




if __name__ == "__main__":
    main()



# table table-striped table-bordered table-hover cols-10 p-2