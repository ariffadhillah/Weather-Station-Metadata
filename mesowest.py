import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import csv
import os
import json
from urllib.parse import urljoin

BASE_URL = "https://mesowest.utah.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.747400015.1747097706; _ga_9H9H5K3K29=GS2.1.s1747100058$o1$g0$t1747100060$j0$l0$h0; _ga_S86FS8V059=deleted; _ga_S86FS8V059=GS2.1.s1747264885$o7$g1$t1747265301$j0$l0$h0'
}


data_save = []
CSV_FILENAME = "University of Utah.csv"

# output_folder = "img University of Utah"
# os.makedirs(output_folder, exist_ok=True)

FIELDNAMES = [
        "Station Name",
        "Station ID",
        "Mesonet ID",
        "County",
        "State",
        "Country",
        "Timezone",
        "Local Region Category",
        "NWS Region",
        "NWS CWA",
        "NWS Zone",
        "NWS Fire Zone",
        "GACC Region",
        "SUBGACC Region",
        "Latitude",
        "Longitude",        
        "Elevation",
        "Installed",
        "Calibration date",
        "In service date",
        "Last maintenance",       
        "Altimeter Sensor Type",
        "Altimeter Sensor Brand",
        "Altimeter Sensor Model",
        "Altimeter Sensor Install Date",
        "Altimeter Sensor Height from Station Base",
        "Altimeter Sensor Height AGL",
        "Ceiling Sensor Type",
        "Ceiling Sensor Brand",
        "Ceiling Sensor Model",
        "Ceiling Sensor Install Date",
        "Ceiling Sensor Height from Station Base",
        "Ceiling Sensor Height AGL",                
        "Precipitation 1hr Sensor Type",
        "Precipitation 1hr Sensor Brand",
        "Precipitation 1hr Sensor Model",
        "Precipitation 1hr Sensor Install Date",
        "Precipitation 1hr Sensor Height from Station Base",
        "Precipitation 1hr Sensor Height AGL",
        "Precipitation 2hr Sensor Type",
        "Precipitation 2hr Sensor Brand",
        "Precipitation 2hr Sensor Model",
        "Precipitation 2hr Sensor Install Date",
        "Precipitation 2hr Sensor Height from Station Base",
        "Precipitation 2hr Sensor Height AGL",
        "Precipitation 3hr Sensor Type",
        "Precipitation 3hr Sensor Brand",
        "Precipitation 3hr Sensor Model",
        "Precipitation 3hr Sensor Install Date",
        "Precipitation 3hr Sensor Height from Station Base",
        "Precipitation 3hr Sensor Height AGL",
        "Precipitation 6hr Sensor Type",
        "Precipitation 6hr Sensor Brand",
        "Precipitation 6hr Sensor Model",
        "Precipitation 6hr Sensor Install Date",
        "Precipitation 6hr Sensor Height from Station Base",
        "Precipitation 6hr Sensor Height AGL",
        "Pressure change (PCHA) Sensor Type",
        "Pressure change (PCHA) Sensor Brand",
        "Pressure change (PCHA) Sensor Model",
        "Pressure change (PCHA) Sensor Install Date",
        "Pressure change (PCHA) Sensor Height from Station Base",
        "Pressure change (PCHA) Sensor Sensor Height AGL",
        "Pressure Tendency (P03D) Sensor Type",
        "Pressure Tendency (P03D) Sensor Brand",
        "Pressure Tendency (P03D) Sensor Model",
        "Pressure Tendency (P03D) Sensor Install Date",
        "Pressure Tendency (P03D) Sensor Height from Station Base",
        "Pressure Tendency (P03D) Sensor Height AGL",
        "Relative Humidity (RELH) Sensor Type",
        "Relative Humidity (RELH) Sensor Brand",
        "Relative Humidity (RELH) Sensor Model",
        "Relative Humidity (RELH) Sensor Install Date",
        "Relative Humidity (RELH) Sensor Height from Station Base",
        "Relative Humidity (RELH) Sensor Height AGL",

        "Sea_level pressure (PMSL) Sensor Type",
        "Sea_level pressure (PMSL) Sensor Brand",
        "Sea_level pressure (PMSL) Sensor Model",
        "Sea_level pressure (PMSL) Sensor Install Date",
        "Sea_level pressure (PMSL) Sensor Height from Station Base",
        "Sea_level pressure (PMSL) Sensor Height AGL",

        "Temperature (TMPF) at 2 m Sensor Type",
        "Temperature (TMPF) at 2 m Sensor Brand",
        "Temperature (TMPF) at 2 m Sensor Model",
        "Temperature (TMPF) at 2 m Sensor Install Date",
        "Temperature (TMPF) at 2 m Sensor Height from Station Base",
        "Temperature (TMPF) at 2 m Sensor Height AGL",

        "Visibility (VSBY) Sensor Type",
        "Visibility (VSBY) Sensor Brand",
        "Visibility (VSBY) Sensor Model",
        "Visibility (VSBY) Sensor Install Date",
        "Visibility (VSBY) Sensor Height from Station Base",
        "Visibility (VSBY) Sensor Height AGL",

        "Weather conditions (WNUM) Sensor Type",
        "Weather conditions (WNUM) Sensor Brand",
        "Weather conditions (WNUM) Sensor Model",
        "Weather conditions (WNUM) Sensor Install Date",
        "Weather conditions (WNUM) Sensor Height from Station Base",
        "Weather conditions (WNUM) Sensor Height AGL",

        "Wind Direction (DRCT) at 10 m Sensor Type",
        "Wind Direction (DRCT) at 10 m Sensor Brand",
        "Wind Direction (DRCT) at 10 m Sensor Model",
        "Wind Direction (DRCT) at 10 m Sensor Install Date",
        "Wind Direction (DRCT) at 10 m Sensor Height from Station Base",
        "Wind Direction (DRCT) at 10 m Sensor Height AGL",

        "Wind Gust (GUST) at 10 m Sensor Type",
        "Wind Gust (GUST) at 10 m Sensor Brand",
        "Wind Gust (GUST) at 10 m Sensor Model",
        "Wind Gust (GUST) at 10 m Sensor Install Date",
        "Wind Gust (GUST) at 10 m Sensor Height from Station Base",
        "Wind Gust (GUST) at 10 m Sensor Height AGL",

        "Wind Speed (SKNT) at 10 m Sensor Type",
        "Wind Speed (SKNT) at 10 m Sensor Brand",
        "Wind Speed (SKNT) at 10 m Sensor Model",
        "Wind Speed (SKNT) at 10 m Sensor Install Date", 
        "Wind Speed (SKNT) at 10 m Sensor Height from Station Base",
        "Wind Speed (SKNT) at 10 m Sensor Height AGL",
]

def save_station_data(row, filename=CSV_FILENAME):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        
        writer.writerow(row)
        file.flush()


def get_states():
    response = requests.get(BASE_URL, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')
    form_search = soup.find("form", id="masterform")
    select = form_search.find("select", id="state")
    options = select.find_all("option")
    
    states = [option["value"] for option in options]
    print(f"🔢 Jumlah state ditemukan: {len(states)}")
    return states

def get_station_ids(state):
    url_state = f"{BASE_URL}cgi-bin/droman/raws_ca_monitor.cgi?state={state}&rawsflag=3"
    print(f"🌐 Memproses state: {state} - URL: {url_state}")
    
    response = requests.get(url_state, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all("table", attrs={"width": "800", "border": "1"})
    
    station_ids = []
    for idx, table in enumerate(tables, 1):
        print(f"\n📄 Tabel #{idx}")
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            for col in cols:
                link = col.find("a")
                if link and link.has_attr("href"):
                    href = link["href"]
                    parsed = urlparse(href)
                    query_params = parse_qs(parsed.query)
                    station_id = query_params.get("stn", [""])[0]
                    if station_id:
                        station_ids.append(station_id)
        print(f"✅ Tabel #{idx} selesai diproses.")
    
    print(f"\n🔢 Jumlah kode station ditemukan: {len(station_ids)}")
    return station_ids

    
def get_station_info(station_id):
    url_station = f"{BASE_URL}cgi-bin/droman/station_total.cgi?stn={station_id}&unit=0"
    print(f"➡️ Memproses Station ID: {station_id} - URL: {url_station}")
    
    response = requests.get(url_station, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')
    # page_url = 'https://mesowest.utah.edu'

    # # Temukan elemen gambar
    # img_tag = soup.select_one("div#map img")
    # if img_tag and img_tag.get("src"):
    #     img_src = img_tag["src"]
    #     img_url = urljoin(page_url, img_src)  # Buat URL absolut

    #     # Ambil nama file dari URL
    #     basename = os.path.basename(urlparse(img_url).path)  # Contoh: KPRN.jpeg

    #     # Tambahkan prefix jika diinginkan
    #     prefix = "example-"
    #     filename = prefix + basename  # Contoh: example-KPRN.jpeg

    #     # Buat path lengkap untuk menyimpan gambar
    #     save_path = os.path.join(output_folder, filename)

    #     # Unduh gambar
    #     img_response = requests.get(img_url)
    #     if img_response.status_code == 200:
    #         with open(save_path, "wb") as f:
    #             f.write(img_response.content)
    #         print(f"Gambar berhasil disimpan: {save_path}")
    #     else:
    #         print("Gagal mengunduh gambar.")
    # else:
    #     print("Gambar tidak ditemukan di dalam <div id='map'>.")


    def get_value(label):
        tag = soup.find("b", string=label)
        if tag:
            value_td = tag.find_parent("td").find_next_sibling("td")
            return value_td.get_text(strip=True) if value_td else None
        return None
    

    def extract_table_by_label(soup, label_text, id_prefix="tbl"):
        # Temukan elemen <u> berdasarkan teks label
        u_tag = soup.find("u", string=label_text)
        if not u_tag:
            return None

        # Ambil bagian ID dari <u> lalu ubah prefix-nya dari "hide" jadi "tbl"
        u_id = u_tag.get("id")
        if not u_id:
            return None

        # Ambil id target, misalnya: hide665 -> tbl665
        target_id = u_id.replace("hide", id_prefix)

        # Cari <div> yang id-nya cocok
        div_tag = soup.find("div", id=target_id)
        if not div_tag:
            return None

        # Cari tabel di dalam div tersebut
        table = div_tag.find("table")
        if not table:
            return None

        # Ekstrak isi tabel jadi dictionary
        rows = table.find_all("tr")
        table_data = {}
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].get_text(strip=True).replace(":", "")
                value = cols[1].get_text(strip=True).replace("\x00", "")
                table_data[key] = value
        return table_data
    
    try:
        altimeter_data = extract_table_by_label(soup, "Altimeter (ALTI) (Click to Hide)")
        # print(altimeter_data)
    except Exception as e:
        print(f"Error extracting altimeter data: {e}")

    # altimeter_data = extract_table_by_label(soup, "Altimeter (ALTI) (Click to Hide)")
    # print(altimeter_data)
    try:
        ceiling_data = extract_table_by_label(soup, "Ceiling (CIG) (Click to Hide)")
        # print(ceiling_data)
    except Exception as e:
        print(f"Error extracting ceiling data: {e}")
    

    try:
        precipitation_1hr_data = extract_table_by_label(soup, "Precipitation 1hr (P01I) (Click to Hide)")
        # print(precipitation_1hr_data)
    except Exception as e:
        print(f"Error extracting precipitation 1hr data: {e}")
    
    try:
        precipitation_2hr_data = extract_table_by_label(soup, "Precipitation 24hr (P24I) (Click to Hide)")
        # print(precipitation_2hr_data)
    except Exception as e:
        print(f"Error extracting precipitation 2hr data: {e}")
    
    try:
        precipitation_3hr_data = extract_table_by_label(soup, "Precipitation 3hr (P03I) (Click to Hide)")
        # print(precipitation_3hr_data)
    except Exception as e:
        print(f"Error extracting precipitation 3hr data: {e}")
    
    try:
        precipitation_6hr_data = extract_table_by_label(soup, "Precipitation 6hr (P06I) (Click to Hide)")
        # print(precipitation_6hr_data)
    except Exception as e:
        print(f"Error extracting precipitation 6hr data: {e}")
    
    try:
        pressure_change_PCHA = extract_table_by_label(soup, "Pressure change (PCHA) (Click to Hide)")    
        # print(pressure_change_PCHA)
    except Exception as e:
        print(f"Error extracting pressure change data: {e}")
    
    try:
        pressure_Tendency_P03D = extract_table_by_label(soup, "Pressure Tendency (P03D) (Click to Hide)")
        # print(pressure_Tendency_P03D)
    except Exception as e:
        print(f"Error extracting pressure tendency data: {e}")
    try:
        relative_Humidity_RELH = extract_table_by_label(soup, "Relative Humidity (RELH) (Click to Hide)")
        # print(relative_Humidity_RELH)
    except Exception as e:
        print(f"Error extracting relative humidity data: {e}")
    try:
        sea_level_pressure_PMSL = extract_table_by_label(soup, "Sea_level pressure (PMSL) (Click to Hide)")
        # print(sea_level_pressure_PMSL)
    except Exception as e:
        print(f"Error extracting sea level pressure data: {e}")
    try:
        temperature_TMPF_at_2_m = extract_table_by_label(soup, "Temperature (TMPF) at 2 m (Click to Hide)")
        # print(temperature_TMPF_at_2_m)
    except Exception as e:
        print(f"Error extracting temperature data: {e}")
    
    try:
        visibility_VSBY = extract_table_by_label(soup, "Visibility (VSBY) (Click to Hide)")
        # print(visibility_VSBY)
    except Exception as e:
        print(f"Error extracting visibility data: {e}")
    
    try:
        weather_conditions_WNUM = extract_table_by_label(soup, "Weather conditions (WNUM) (Click to Hide)")
        # print(weather_conditions_WNUM)
    except Exception as e:
        print(f"Error extracting weather conditions data: {e}")
    try:        
        wind_Direction_DRCT = extract_table_by_label(soup, "Wind Direction (DRCT) at 10 m (Click to Hide)")
        # print(wind_Direction_DRCT)
    except Exception as e:
        print(f"Error extracting wind direction data: {e}")
    try:
        wind_Gust_GUST_at_10_m = extract_table_by_label(soup, "Wind Gust (GUST) at 10 m (Click to Hide)")
        # print(wind_Gust_GUST_at_10_m)
    except Exception as e:
        print(f"Error extracting wind gust data: {e}")
    try:
        wind_Speed_SKNT_at_10_m = extract_table_by_label(soup, "Wind Speed (SKNT) at 10 m (Click to Hide)")
        # print(wind_Speed_SKNT_at_10_m)
    except Exception as e:
        print(f"Error extracting wind speed data: {e}")

    
    data = {
        "Station Name": get_value("Station Name:"),
        "Station ID": get_value("Station ID:"),
        "Mesonet ID": get_value("Mesonet ID:"),
        "County": get_value("County:"),
        "State": get_value("State:"),
        "Country": get_value("Country:"),
        "Timezone": get_value("Timezone:"),
        "Local Region Category": get_value("Local Region Category:"),
        "NWS Region": get_value("NWS Region:"),
        "NWS CWA": get_value("NWS CWA:"),
        "NWS Zone": get_value("NWS Zone:"),
        "NWS Fire Zone": get_value("NWS Fire Zone:"),
        "GACC Region": get_value("GACC Region:"),
        "SUBGACC Region": get_value("SUBGACC Region:"),
        "Latitude": f"'{get_value('Latitude:')}",
        "Longitude": f"'{get_value('Longitude:')}",        
        "Elevation":f"'{get_value('Elevation:')}",
        "Installed": f"'{get_value('Installed:')}",
        "Calibration date": f"'{get_value('Calibrated:')}",
        "In service date": f"'{get_value('First Date in MesoWest:')}",
        "Last maintenance": f"'{get_value('Last Metadata Update:')}",       

        "Altimeter Sensor Type": altimeter_data.get("Sensor Type") if altimeter_data else " ",
        "Altimeter Sensor Brand": altimeter_data.get("Brand") if altimeter_data else " ",
        "Altimeter Sensor Model": altimeter_data.get("Model") if altimeter_data else " ",
        "Altimeter Sensor Install Date": f"'{altimeter_data.get('Install Date')}" if altimeter_data else " ",
        "Altimeter Sensor Height from Station Base": altimeter_data.get("Sensor Height from Station Base") if altimeter_data else " ",
        "Altimeter Sensor Height AGL": altimeter_data.get("Sensor Height AGL") if altimeter_data else " ",
        
        "Ceiling Sensor Type": ceiling_data.get("Sensor Type") if ceiling_data else " ",
        "Ceiling Sensor Brand": ceiling_data.get("Brand") if ceiling_data else " ",
        "Ceiling Sensor Model": ceiling_data.get("Model") if ceiling_data else " ",
        "Ceiling Sensor Install Date": f"'{ceiling_data.get('Install Date')}" if ceiling_data else " ",
        "Ceiling Sensor Height from Station Base": ceiling_data.get("Sensor Height from Station Base") if ceiling_data else " ",
        "Ceiling Sensor Height AGL": ceiling_data.get("Sensor Height AGL") if ceiling_data else " ",
                
        "Precipitation 1hr Sensor Type": precipitation_1hr_data.get("Sensor Type") if precipitation_1hr_data else " ",
        "Precipitation 1hr Sensor Brand": precipitation_1hr_data.get("Brand") if precipitation_1hr_data else " ",
        "Precipitation 1hr Sensor Model": precipitation_1hr_data.get("Model") if precipitation_1hr_data else " ",
        "Precipitation 1hr Sensor Install Date": f"'{precipitation_1hr_data.get('Install Date')}" if precipitation_1hr_data else " ",
        "Precipitation 1hr Sensor Height from Station Base": precipitation_1hr_data.get("Sensor Height from Station Base") if precipitation_1hr_data else " ",
        "Precipitation 1hr Sensor Height AGL": precipitation_1hr_data.get("Sensor Height AGL") if precipitation_1hr_data else " ",

        "Precipitation 2hr Sensor Type": precipitation_2hr_data.get("Sensor Type") if precipitation_2hr_data else " ",
        "Precipitation 2hr Sensor Brand": precipitation_2hr_data.get("Brand") if precipitation_2hr_data else " ",
        "Precipitation 2hr Sensor Model": precipitation_2hr_data.get("Model") if precipitation_2hr_data else " ",
        "Precipitation 2hr Sensor Install Date": f"'{precipitation_2hr_data.get('Install Date')}" if precipitation_2hr_data else " ",
        "Precipitation 2hr Sensor Height from Station Base": precipitation_2hr_data.get("Sensor Height from Station Base") if precipitation_2hr_data else " ",
        "Precipitation 2hr Sensor Height AGL": precipitation_2hr_data.get("Sensor Height AGL") if precipitation_2hr_data else " ",

        "Precipitation 3hr Sensor Type": precipitation_3hr_data.get("Sensor Type") if precipitation_3hr_data else " ",
        "Precipitation 3hr Sensor Brand": precipitation_3hr_data.get("Brand") if precipitation_3hr_data else " ",
        "Precipitation 3hr Sensor Model": precipitation_3hr_data.get("Model") if precipitation_3hr_data else " ",
        "Precipitation 3hr Sensor Install Date": f"'{precipitation_3hr_data.get('Install Date')}" if precipitation_3hr_data else " ",
        "Precipitation 3hr Sensor Height from Station Base": precipitation_3hr_data.get("Sensor Height from Station Base") if precipitation_3hr_data else " ",
        "Precipitation 3hr Sensor Height AGL": precipitation_3hr_data.get("Sensor Height AGL") if precipitation_3hr_data else " ",

        "Precipitation 6hr Sensor Type": precipitation_6hr_data.get("Sensor Type") if precipitation_6hr_data else " ",
        "Precipitation 6hr Sensor Brand": precipitation_6hr_data.get("Brand") if precipitation_6hr_data else " ",
        "Precipitation 6hr Sensor Model": precipitation_6hr_data.get("Model") if precipitation_6hr_data else " ",
        "Precipitation 6hr Sensor Install Date": f"'{precipitation_6hr_data.get('Install Date')}" if precipitation_6hr_data else " ",
        "Precipitation 6hr Sensor Height from Station Base": precipitation_6hr_data.get("Sensor Height from Station Base") if precipitation_6hr_data else " ",
        "Precipitation 6hr Sensor Height AGL": precipitation_6hr_data.get("Sensor Height AGL") if precipitation_6hr_data else " ",

        "Pressure change (PCHA) Sensor Type": pressure_change_PCHA.get("Sensor Type") if pressure_change_PCHA else " ",
        "Pressure change (PCHA) Sensor Brand": pressure_change_PCHA.get("Brand") if pressure_change_PCHA else " ",
        "Pressure change (PCHA) Sensor Model": pressure_change_PCHA.get("Model") if pressure_change_PCHA else " ",
        "Pressure change (PCHA) Sensor Install Date": f"'{pressure_change_PCHA.get('Install Date')}" if pressure_change_PCHA else " ",
        "Pressure change (PCHA) Sensor Height from Station Base": pressure_change_PCHA.get("Sensor Height from Station Base") if pressure_change_PCHA else " ",
        "Pressure change (PCHA) Sensor Sensor Height AGL": pressure_change_PCHA.get("Sensor Height AGL") if pressure_change_PCHA else " ",

        "Pressure Tendency (P03D) Sensor Type": pressure_Tendency_P03D.get("Sensor Type") if pressure_Tendency_P03D else " ",
        "Pressure Tendency (P03D) Sensor Brand": pressure_Tendency_P03D.get("Brand") if pressure_Tendency_P03D else " ",
        "Pressure Tendency (P03D) Sensor Model": pressure_Tendency_P03D.get("Model") if pressure_Tendency_P03D else " ",
        "Pressure Tendency (P03D) Sensor Install Date": f"'{pressure_Tendency_P03D.get('Install Date')}" if pressure_Tendency_P03D else " ",
        "Pressure Tendency (P03D) Sensor Height from Station Base": pressure_Tendency_P03D.get("Sensor Height from Station Base") if pressure_Tendency_P03D else " ",
        "Pressure Tendency (P03D) Sensor Height AGL": pressure_Tendency_P03D.get("Sensor Height AGL") if pressure_Tendency_P03D else " ",

        "Relative Humidity (RELH) Sensor Type": relative_Humidity_RELH.get("Sensor Type") if relative_Humidity_RELH else " ",
        "Relative Humidity (RELH) Sensor Brand": relative_Humidity_RELH.get("Brand") if relative_Humidity_RELH else " ",
        "Relative Humidity (RELH) Sensor Model": relative_Humidity_RELH.get("Model") if relative_Humidity_RELH else " ",
        "Relative Humidity (RELH) Sensor Install Date": f"'{relative_Humidity_RELH.get('Install Date')}" if relative_Humidity_RELH else " ",
        "Relative Humidity (RELH) Sensor Height from Station Base": relative_Humidity_RELH.get("Sensor Height from Station Base") if relative_Humidity_RELH else " ",
        "Relative Humidity (RELH) Sensor Height AGL": relative_Humidity_RELH.get("Sensor Height AGL") if relative_Humidity_RELH else " ",

        "Sea_level pressure (PMSL) Sensor Type": sea_level_pressure_PMSL.get("Sensor Type") if sea_level_pressure_PMSL else " ",
        "Sea_level pressure (PMSL) Sensor Brand": sea_level_pressure_PMSL.get("Brand") if sea_level_pressure_PMSL else " ",
        "Sea_level pressure (PMSL) Sensor Model": sea_level_pressure_PMSL.get("Model") if sea_level_pressure_PMSL else " ",
        "Sea_level pressure (PMSL) Sensor Install Date": f"'{sea_level_pressure_PMSL.get('Install Date')}" if sea_level_pressure_PMSL else " ",
        "Sea_level pressure (PMSL) Sensor Height from Station Base": sea_level_pressure_PMSL.get("Sensor Height from Station Base") if sea_level_pressure_PMSL else " ",
        "Sea_level pressure (PMSL) Sensor Height AGL": sea_level_pressure_PMSL.get("Sensor Height AGL") if sea_level_pressure_PMSL else " ",

        "Temperature (TMPF) at 2 m Sensor Type": temperature_TMPF_at_2_m.get("Sensor Type") if temperature_TMPF_at_2_m else " ",
        "Temperature (TMPF) at 2 m Sensor Brand": temperature_TMPF_at_2_m.get("Brand") if temperature_TMPF_at_2_m else " ",
        "Temperature (TMPF) at 2 m Sensor Model": temperature_TMPF_at_2_m.get("Model") if temperature_TMPF_at_2_m else " ",
        "Temperature (TMPF) at 2 m Sensor Install Date": f"'{temperature_TMPF_at_2_m.get('Install Date')}" if temperature_TMPF_at_2_m else " ",
        "Temperature (TMPF) at 2 m Sensor Height from Station Base": temperature_TMPF_at_2_m.get("Sensor Height from Station Base") if temperature_TMPF_at_2_m else " ",
        "Temperature (TMPF) at 2 m Sensor Height AGL": temperature_TMPF_at_2_m.get("Sensor Height AGL") if temperature_TMPF_at_2_m else " ",        

        "Visibility (VSBY) Sensor Type": visibility_VSBY.get("Sensor Type") if visibility_VSBY else " ",
        "Visibility (VSBY) Sensor Brand": visibility_VSBY.get("Brand") if visibility_VSBY else " ",
        "Visibility (VSBY) Sensor Model": visibility_VSBY.get("Model") if visibility_VSBY else " ",
        "Visibility (VSBY) Sensor Install Date": f"'{visibility_VSBY.get('Install Date')}" if visibility_VSBY else " ",
        "Visibility (VSBY) Sensor Height from Station Base": visibility_VSBY.get("Sensor Height from Station Base") if visibility_VSBY else " ",
        "Visibility (VSBY) Sensor Height AGL": visibility_VSBY.get("Sensor Height AGL") if visibility_VSBY else " ",

        "Weather conditions (WNUM) Sensor Type": weather_conditions_WNUM.get("Sensor Type") if weather_conditions_WNUM else " ",
        "Weather conditions (WNUM) Sensor Brand": weather_conditions_WNUM.get("Brand") if weather_conditions_WNUM else " ",
        "Weather conditions (WNUM) Sensor Model": weather_conditions_WNUM.get("Model") if weather_conditions_WNUM else " ",
        "Weather conditions (WNUM) Sensor Install Date": f"'{weather_conditions_WNUM.get('Install Date')}" if weather_conditions_WNUM else " ",
        "Weather conditions (WNUM) Sensor Height from Station Base": weather_conditions_WNUM.get("Sensor Height from Station Base") if weather_conditions_WNUM else " ",
        "Weather conditions (WNUM) Sensor Height AGL": weather_conditions_WNUM.get("Sensor Height AGL") if weather_conditions_WNUM else " ",

        "Wind Direction (DRCT) at 10 m Sensor Type": wind_Direction_DRCT.get("Sensor Type") if wind_Direction_DRCT else " ",
        "Wind Direction (DRCT) at 10 m Sensor Brand": wind_Direction_DRCT.get("Brand") if wind_Direction_DRCT else " ",
        "Wind Direction (DRCT) at 10 m Sensor Model": wind_Direction_DRCT.get("Model") if wind_Direction_DRCT else " ",
        "Wind Direction (DRCT) at 10 m Sensor Install Date": f"'{wind_Direction_DRCT.get('Install Date')}" if wind_Direction_DRCT else " ",
        "Wind Direction (DRCT) at 10 m Sensor Height from Station Base": wind_Direction_DRCT.get("Sensor Height from Station Base") if wind_Direction_DRCT else " ",
        "Wind Direction (DRCT) at 10 m Sensor Height AGL": wind_Direction_DRCT.get("Sensor Height AGL") if wind_Direction_DRCT else " ",

        "Wind Gust (GUST) at 10 m Sensor Type": wind_Gust_GUST_at_10_m.get("Sensor Type") if wind_Gust_GUST_at_10_m else " ",
        "Wind Gust (GUST) at 10 m Sensor Brand": wind_Gust_GUST_at_10_m.get("Brand") if wind_Gust_GUST_at_10_m else " ",
        "Wind Gust (GUST) at 10 m Sensor Model": wind_Gust_GUST_at_10_m.get("Model") if wind_Gust_GUST_at_10_m else " ",
        "Wind Gust (GUST) at 10 m Sensor Install Date": f"'{wind_Gust_GUST_at_10_m.get('Install Date')}" if wind_Gust_GUST_at_10_m else " ",
        "Wind Gust (GUST) at 10 m Sensor Height from Station Base": wind_Gust_GUST_at_10_m.get("Sensor Height from Station Base") if wind_Gust_GUST_at_10_m else " ",
        "Wind Gust (GUST) at 10 m Sensor Height AGL": wind_Gust_GUST_at_10_m.get("Sensor Height AGL") if wind_Gust_GUST_at_10_m else " ",

        "Wind Speed (SKNT) at 10 m Sensor Type": wind_Speed_SKNT_at_10_m.get("Sensor Type") if wind_Speed_SKNT_at_10_m else " ",
        "Wind Speed (SKNT) at 10 m Sensor Brand": wind_Speed_SKNT_at_10_m.get("Brand") if wind_Speed_SKNT_at_10_m else " ",
        "Wind Speed (SKNT) at 10 m Sensor Model": wind_Speed_SKNT_at_10_m.get("Model") if wind_Speed_SKNT_at_10_m else " ",
        "Wind Speed (SKNT) at 10 m Sensor Install Date": f"'{wind_Speed_SKNT_at_10_m.get('Install Date')}" if wind_Speed_SKNT_at_10_m else " ", 
        "Wind Speed (SKNT) at 10 m Sensor Height from Station Base": wind_Speed_SKNT_at_10_m.get("Sensor Height from Station Base") if wind_Speed_SKNT_at_10_m else " ",
        "Wind Speed (SKNT) at 10 m Sensor Height AGL": wind_Speed_SKNT_at_10_m.get("Sensor Height AGL") if wind_Speed_SKNT_at_10_m else " ",

    }

    # for key, value in data.items():
    #     if value:
    #         print(f"{key}: {value}")
    #     else:
    #         print(f"{key}: Data tidak tersedia")
    #         print("")
    #         print("")


    save_station_data(data)  # 💾 Simpan langsung
    print(f"✅ Data Station ID {station_id} berhasil diproses.")



# def main():
#     states = get_states()
#     for i, state in enumerate(states, start=1):
#         print(f"\n🗺️ [{i}] Memproses state: {state}")
#         station_ids = get_station_ids(state)
        
#         for j, station_id in enumerate(station_ids, start=1):
#             print(f"\n🔍 [{j}] Info Station:")
#             get_station_info(station_id)
        
#         break  # hapus ini jika ingin proses semua state

def main():
    states = get_states()
    for i, state in enumerate(states, start=1):
        print(f"\n🗺️ [{i}] Memproses state: {state}")
        station_ids = get_station_ids(state)
        
        for j, station_id in enumerate(station_ids, start=1):
            print(f"\n🔍 [{j}] Info Station:")
            get_station_info(station_id)
        
        # break  # hapus ini jika ingin proses semua state


if __name__ == "__main__":
    main()
