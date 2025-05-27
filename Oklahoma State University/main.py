import requests
import json
import time
import csv
import os
BASE_URL = "https://api.prod.mesonet.org/index.php/meta/sites/status/active/vars/stid,name,lat,lon,wfo"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

CSV_FILENAME = "Oklahoma State University.csv"

FIELDNAMES = ['Nama Stasiun', 'Station ID', 'Station Number', 'Latitude', 'Longitude',
              'Elevation', 'City', 'County', 'Location', 'Commissioned',
              'Maximum Air Temperature (°F)', 'Maximum air temperature (°F) Date',
              'Minimum Air Temperature (°F)', 'Minimum Air Temperature (°F) Date',
              'Daily Rainfall (in.)', 'Daily rainfall (in.) Date',
              'Monthly rainfall (in.)', 'Monthly rainfall (in.) Date',
              'Annual rainfall (in.)', 'Annual rainfall (in.) Date',
              'Maximum Wind Speed (mph)', 'Maximum Wind Speed (mph) Date',
              'BATV', 'PRES', 'RAIN', 'RELH', 'SRAD', 'TA9M', 'TAIR', 
              'TSLO', 'WDIR', 'WDSD', 'WMAX', 'WMX2', 'WS2M', 
              'WSPD', 'WSSD', 'WVEC', 
              'TB10', 
              'TS05', 
              'TS10', 
              'TS25', 
              'TS60',
              'FT05',
              'FT25',
              'FT60',
              'FTB10',
              'FTS10',
              'ST05',
              'ST25',
              'ST60',
              'STB10',
              'STS10',
              "TREF"]


# def save_station_data(row, filename=CSV_FILENAME):
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
#         writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
#         if not file_exists or os.stat(filename).st_size == 0:
#             writer.writeheader()
        
#         writer.writerow(row)
#         file.flush()


def get_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"⚠️ Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error saat ambil data: {e}")
    return None

def parse_json(html):
    try:
        parsed = json.loads(html)
        stations = parsed["response"]
        station_ids = [station.get("stid") for station in stations.values() if station.get("stid")]
        return station_ids
    except Exception as e:
        print(f"❌ Error saat parsing JSON: {e}")
        return []

def cari_deskripsi_variable(variables, kode_paid):
    for key, items in variables.items():
        for item in items:
            if item.get("paid") == kode_paid:
                return f"{kode_paid} : {item.get('name')}"
    return f"{kode_paid} : Tidak ditemukan."

def json_page(station_id):
    time.sleep(2)
    detail_url = f"https://api.prod.mesonet.org/index.php/meta/site_info/stid/{station_id}"
    time.sleep(1)
    print(f"🔍 Mengakses detail URL: {detail_url}")

    html = get_url(detail_url)
    if not html:
        print("❌ Gagal mendapatkan data detail.")
        return

    try:
        detail_json = json.loads(html)  # Tanpa indent di sini
        # Cetak dengan indent untuk melihat struktur dengan rapi
        # meta_data = json.dumps(detail_json, indent=4)
        # print(meta_data)

        detail_info__station = detail_json["response"]['info']
        info_variables = detail_json["response"]['variables']        
        detail_extremes__station_tair_max = detail_json["response"]['extremes']['data']['tair_max']
        detail_extremes__station_rain_daily = detail_json["response"]['extremes']['data']['rain_daily']
        detail_extremes__station_tair_min = detail_json["response"]['extremes']['data']['tair_min']
        detail_extremes__station_rain_monthly = detail_json["response"]['extremes']['data']['rain_monthly']
        detail_extremes__station_rain_annual = detail_json["response"]['extremes']['data']['rain_annual']
        detail_extremes__station_wind_max = detail_json["response"]['extremes']['data']['wind_max']
        # detail_name_extremes_tair_max = detail_extremes__station_tair_max['name']
        detail_value_extremes_tair_max = detail_extremes__station_tair_max['value']
        detail_date_extremes_tair_max = detail_extremes__station_tair_max['date']
        # detail_name_extremes_tair_min = detail_extremes__station_tair_min['name']
        detail_value_extremes_tair_min = detail_extremes__station_tair_min['value']
        detail_date_extremes_tair_min = detail_extremes__station_tair_min['date']
        # detail_name_extremes_rain_daily = detail_extremes__station_rain_daily['name']
        detail_value_extremes_rain_daily = detail_extremes__station_rain_daily['value']
        detail_date_extremes_rain_daily = detail_extremes__station_rain_daily['date']
        # detail_name_extremes_rain_monthly = detail_extremes__station_rain_monthly['name']
        detail_value_extremes_rain_monthly = detail_extremes__station_rain_monthly['value']
        detail_date_extremes_rain_monthly = detail_extremes__station_rain_monthly['date']
        # detail_name_extremes_rain_annual = detail_extremes__station_rain_annual['name']
        detail_value_extremes_rain_annual = detail_extremes__station_rain_annual['value']
        detail_date_extremes_rain_annual = detail_extremes__station_rain_annual['date']
        # detail_name_extremes_wind_max = detail_extremes__station_wind_max['name']
        detail_value_extremes_wind_max = detail_extremes__station_wind_max['value']
        detail_date_extremes_wind_max = detail_extremes__station_wind_max['date']



        # print(detail_extremes__station)

        detail_name = detail_info__station['name']
        id_detail_station = detail_info__station['stid']
        station_Number = detail_info__station['stnm']
        lat = detail_info__station['lat']
        lon = detail_info__station['lon']
        elev = detail_info__station['elev']
        city = detail_info__station['city']
        county = detail_info__station['cnty']
        location_rang = detail_info__station['rang']
        location_cdir = detail_info__station['cdir']
        location = location_rang +" mi "+ location_cdir +" of " + city
        commissioned = detail_info__station['datc']
        commissioned_date = commissioned.split(" ")[0] if commissioned else ""
        
        batv  = cari_deskripsi_variable(info_variables, "BATV")
        pres  = cari_deskripsi_variable(info_variables, "PRES")
        rain  = cari_deskripsi_variable(info_variables, "RAIN")
        rain  = cari_deskripsi_variable(info_variables, "RELH")
        srad  = cari_deskripsi_variable(info_variables, "SRAD")
        ta9m  = cari_deskripsi_variable(info_variables, "TA9M")
        tair  = cari_deskripsi_variable(info_variables, "TAIR")
        tslo  = cari_deskripsi_variable(info_variables, "TSLO")
        wdir  = cari_deskripsi_variable(info_variables, "WDIR")
        wdsd  = cari_deskripsi_variable(info_variables, "WDSD")
        wmax  = cari_deskripsi_variable(info_variables, "WMAX")
        wmx2  = cari_deskripsi_variable(info_variables, "WMX2")
        ws2m  = cari_deskripsi_variable(info_variables, "WS2M")
        wspd  = cari_deskripsi_variable(info_variables, "WSPD")
        wssd  = cari_deskripsi_variable(info_variables, "WSSD")
        wvec  = cari_deskripsi_variable(info_variables, "WVEC")
        tb10  = cari_deskripsi_variable(info_variables, "TB10")
        ts05  = cari_deskripsi_variable(info_variables, "TS05")
        ts10  = cari_deskripsi_variable(info_variables, "TS10")
        ts25  = cari_deskripsi_variable(info_variables, "TS25")
        ts60  = cari_deskripsi_variable(info_variables, "TS60")
        ft05  = cari_deskripsi_variable(info_variables, "FT05")
        ft25  = cari_deskripsi_variable(info_variables, "FT25")
        ft60  = cari_deskripsi_variable(info_variables, "FT60")
        ftb10 = cari_deskripsi_variable(info_variables, "FTB10")
        fts10 = cari_deskripsi_variable(info_variables, "FTS10")
        st05  = cari_deskripsi_variable(info_variables, "ST05")
        st25  = cari_deskripsi_variable(info_variables, "ST25")
        st60  = cari_deskripsi_variable(info_variables, "ST60")
        stb10 = cari_deskripsi_variable(info_variables, "STB10")
        sts10 = cari_deskripsi_variable(info_variables, "STS10")
        tref = cari_deskripsi_variable(info_variables, "TREF")


        data_save = {
            'Nama Stasiun': detail_name,
            'Station ID': id_detail_station,
            'Station Number': station_Number,
            'Latitude': f"'{lat}",
            'Longitude': f"'{lon}",
            'Elevation': f"'{elev}",
            'City': city,
            'County': county,
            'Location': location,
            'Commissioned': commissioned_date,
            'Maximum Air Temperature (°F)': f"'{detail_value_extremes_tair_max}",
            'Maximum air temperature (°F) Date': detail_date_extremes_tair_max,
            'Minimum Air Temperature (°F)': f"'{detail_value_extremes_tair_min}",
            'Minimum Air Temperature (°F) Date': detail_date_extremes_tair_min,
            'Daily Rainfall (in.)': f"'{detail_value_extremes_rain_daily}",
            'Daily rainfall (in.) Date': detail_date_extremes_rain_daily,
            'Monthly rainfall (in.)': f"'{detail_value_extremes_rain_monthly}",
            'Monthly rainfall (in.) Date': detail_date_extremes_rain_monthly,
            'Annual rainfall (in.)': f"'{detail_value_extremes_rain_annual}",
            'Annual rainfall (in.) Date': detail_date_extremes_rain_annual,
            'Maximum Wind Speed (mph)': f"'{detail_value_extremes_wind_max}",
            'Maximum Wind Speed (mph) Date': detail_date_extremes_wind_max,
            'BATV': batv.replace("BATV", "").strip(),
            'PRES': pres.replace("PRES", "").strip(),
            'RAIN': rain.replace("RAIN", "").strip(),
            'RELH': rain.replace("RELH", "").strip(),
            'SRAD': srad.replace("SRAD", "").strip(),
            'TA9M': ta9m.replace("TA9M", "").strip(),
            'TAIR': tair.replace("TAIR", "").strip(),
            'TSLO': tslo.replace("TSLO", "").strip(),
            'WDIR': wdir.replace("WDIR", "").strip(),
            'WDSD': wdsd.replace("WDSD", "").strip(),
            'WMAX': wmax.replace("WMAX", "").strip(),
            'WMX2': wmx2.replace("WMX2", "").strip(),
            'WS2M': ws2m.replace("WS2M", "").strip(),
            'WSPD': wspd.replace("WSPD", "").strip(),
            'WSSD': wssd.replace("WSSD", "").strip(),
            'WVEC': wvec.replace("WVEC", "").strip(),
            'TB10': tb10.replace("TB10", "").strip(),
            'TS05': ts05.replace("TS05", "").strip(),
            'TS10': ts10.replace("TS10", "").strip(),
            'TS25': ts25.replace("TS25", "").strip(),
            'TS60': ts60.replace("TS60", "").strip(),
            'FT05': ft05.replace("FT05", "").strip(),
            'FT25': ft25.replace("FT25", "").strip(),
            'FT60': ft60.replace("FT60", "").strip(),
            'FTB10': ftb10.replace("FTB10", "").strip(),
            'FTS10': fts10.replace("FTS10", "").strip(),
            'ST05': st05.replace("ST05", "").strip(),
            'ST25': st25.replace("ST25", "").strip(),
            'ST60': st60.replace("ST60", "").strip(),
            'STB10': stb10.replace("STB10", "").strip(),
            'STS10': sts10.replace("STS10", "").strip(),
            'TREF': tref.replace("TREF", "").strip()
        }
        print(f"✅ Data untuk {detail_name} berhasil diambil.")
        print(f"🔄 Menyimpan data ke {CSV_FILENAME}...")
        # Simpan data ke CSV
        # Pastikan file CSV sudah ada, jika tidak, buat file baru
        if not os.path.isfile(CSV_FILENAME):
            with open(CSV_FILENAME, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data_save.keys())
                writer.writeheader()
                writer.writerow(data_save)
        else:
            with open(CSV_FILENAME, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data_save.keys())
                writer.writerow(data_save)

        # save_station_data(data_save)

    except json.JSONDecodeError as e:
        print("❌ Gagal parsing JSON:", e)
        return
    
def main():
    base_html = get_url(BASE_URL)
    if not base_html:
        print("❌ Gagal mendapatkan data.")
        return
    station_ids = parse_json(base_html)
    for station_id in station_ids:
        json_page(station_id)

if __name__ == "__main__":
    main()
