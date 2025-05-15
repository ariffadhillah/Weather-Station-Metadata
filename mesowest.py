import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import csv
import os
import json

BASE_URL = "https://mesowest.utah.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.747400015.1747097706; _ga_9H9H5K3K29=GS2.1.s1747100058$o1$g0$t1747100060$j0$l0$h0; _ga_S86FS8V059=deleted; _ga_S86FS8V059=GS2.1.s1747264885$o7$g1$t1747265301$j0$l0$h0'
}


data_save = []
CSV_FILENAME = "example.csv"

FIELDNAMES = [
    "Station Name", "Station ID", "County", "State", "Country", "Timezone",
    "Local Region Category", "NWS Region", "NWS CWA", "NWS Zone",
    "NWS Fire Zone", "Additional Site/Station Description"
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


# def get_station_info(station_id):
#     url_station = f"{BASE_URL}cgi-bin/droman/station_total.cgi?stn={station_id}&unit=0"
#     print(f"➡️ Memproses Station ID: {station_id} - URL: {url_station}")
    
#     response = requests.get(url_station, headers=HEADERS, cookies=COOKIES)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     def get_value(label):
#         tag = soup.find("b", string=label)
#         if tag:
#             value_td = tag.find_parent("td").find_next_sibling("td")
#             return value_td.get_text(strip=True) if value_td else None
#         return None

#     station_name = get_value("Station Name:")
#     station_id_text = get_value("Station ID:")
#     county_text = get_value("County:")
#     state_text = get_value("State:")
#     country_text = get_value("Country:")
#     timezone_text = get_value("Timezone:")
#     local_Region_Category_text = get_value("Local Region Category:")
#     nWS_Region_text = get_value("NWS Region:")
#     nWS_CWA_text = get_value("NWS CWA:")
#     nWS_Zone_text = get_value("NWS Zone:")
#     nWS_Fire_Zone_text = get_value("NWS Fire Zone:")
#     additional = get_value("Additional Site/Station Description:")

#     data = {
#         "Station Name": station_name,
#         "Station ID": station_id_text,
#         "County": county_text,
#         "State": state_text,
#         "Country": country_text,
#         "Timezone": timezone_text,
#         "Local Region Category": local_Region_Category_text,
#         "NWS Region": nWS_Region_text,
#         "NWS CWA": nWS_CWA_text,
#         "NWS Zone": nWS_Zone_text,
#         "NWS Fire Zone": nWS_Fire_Zone_text,
#         "Additional Site/Station Description": additional        
#     }
#     data_save.append(data)
#     print(f"✅ Data Station ID {station_id} berhasil diproses.")
    
def get_station_info(station_id):
    url_station = f"{BASE_URL}cgi-bin/droman/station_total.cgi?stn={station_id}&unit=0"
    print(f"➡️ Memproses Station ID: {station_id} - URL: {url_station}")
    
    response = requests.get(url_station, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')

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
                value = cols[1].get_text(strip=True)
                table_data[key] = value
        return table_data

    location_data = extract_table_by_label(soup, "Altimeter (ALTI) (Click to Hide)")
    print(location_data)

    # def get_value(label):
    #     tag = soup.find("b", string=label)



    # def get_sensor_table(soup, label_title):
    #     # Cari elemen <u> dengan teks sesuai label yang ditarget
    #     u_tag = soup.find("u", string=label_title)
    #     if u_tag:
    #         # Ambil elemen <div> saudara (sibling) terdekat yang berisi tabel sensor
    #         div_id = u_tag.get("id").replace("hide", "tbl")  # "hide665" -> "tbl665"
    #         div_tag = soup.find("div", id=div_id)
    #         if div_tag:
    #             table = div_tag.find("table")
    #             if table:
    #                 # Ambil semua baris dalam tabel
    #                 rows = table.find_all("tr")
    #                 sensor_data = {}
    #                 for row in rows:
    #                     cols = row.find_all("td")
    #                     if len(cols) == 2:
    #                         key = cols[0].get_text(strip=True).replace(":", "")
    #                         value = cols[1].get_text(strip=True)
    #                         sensor_data[key] = value
    #                 return sensor_data
    #     return None


    # sensor_wind = get_sensor_table(get_sensor_table, "Wind Sensor (WSPD, WDIR) (Click to Hide)")
    # print(sensor_wind)

    # from bs4 import BeautifulSoup

    # def get_sensor_table(soup, label_title):
    #     u_tag = soup.find("u", string=label_title)
    #     if u_tag:
    #         div_id = u_tag.get("id").replace("hide", "tbl")
    #         div_tag = soup.find("div", id=div_id)
    #         if div_tag:
    #             table = div_tag.find("table")
    #             if table:
    #                 rows = table.find_all("tr")
    #                 sensor_data = {}
    #                 for row in rows:
    #                     cols = row.find_all("td")
    #                     if len(cols) == 2:
    #                         key = cols[0].get_text(strip=True).replace(":", "")
    #                         value = cols[1].get_text(strip=True)
    #                         sensor_data[key] = value
    #                 return sensor_data
    #     return None

    # # contoh parsing html
    # # html = """<html>...HTML di sini...</html>"""  # isi HTML yang kamu parse
    # # soup = BeautifulSoup(html, "html.parser")

    # sensor_wind = get_sensor_table(soup, "Wind Sensor (WSPD, WDIR) (Click to Hide)")
    # print(sensor_wind)


    # print(json.dumps(sensor_wind, indent=2))
    # sensor_temp = get_sensor_table(sensors, "Temperature (TAIR) (Click to Hide)")

    # sensor_altimeter = get_sensor_table(sensors, "Altimeter (ALTI) (Click to Hide)")
    # print(json.dumps(sensor_altimeter, indent=2))


    # def get_value_Additional(label_):
    #     tag = soup.find("b", string=label_)
    #     if tag:
    #         value_td = tag.find_parent("td").find_next_sibling("tr")
    #         return value_td.get_text(strip=False) if value_td else None
    #     return None
    
    # def get_additional_html(soup):
    #     label_tag = soup.find("b", string="Additional Site/Station Description:")
    #     if label_tag:
    #         tr = label_tag.find_parent("tr")
    #         if tr:
    #             next_tr = tr.find_next_sibling("tr")
    #             if next_tr:
    #                 return str(next_tr)
    #     return None

    # Kemudian gunakan saat membangun data dict
    # data = {
    #     "Station Name": get_value("Station Name:"),
    #     "Station ID": get_value("Station ID:"),
    #     "County": get_value("County:"),
    #     "State": get_value("State:"),
    #     "Country": get_value("Country:"),
    #     "Timezone": get_value("Timezone:"),
    #     "Local Region Category": get_value("Local Region Category:"),
    #     "NWS Region": get_value("NWS Region:"),
    #     "NWS CWA": get_value("NWS CWA:"),
    #     "NWS Zone": get_value("NWS Zone:"),
    #     "NWS Fire Zone": get_value("NWS Fire Zone:"),
    #     "GACC Region": get_value("GACC Region:"),
    # }
    # location_data = extract_table_by_label(soup, "Altimeter (ALTI) (Click to Hide)")
    
    data = {
        "Station Name": get_value("Station Name:"),
        "Station ID": get_value("Station ID:"),
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
        "In service date": get_value("First Date in MesoWest:"),
        "Last maintenance": get_value("Last Metadata Update:"),
        "Calibration date": get_value("Calibrated:"),
        "Sensor Type": location_data["Sensor Type"],
        "Sensor Brand": location_data["Brand"],
        "Sensor Model": location_data["Model"],
    }

    for key, value in data.items():
        if value:
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")
            print("")
            print("")






    # save_station_data(data)  # 💾 Simpan langsung
    # print(f"✅ Data Station ID {station_id} berhasil diproses.")



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
        
        break  # hapus ini jika ingin proses semua state


if __name__ == "__main__":
    main()
