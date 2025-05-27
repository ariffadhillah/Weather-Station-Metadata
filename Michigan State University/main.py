import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re

BASE_URL = "https://mawn.geo.msu.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.3.943748827.1747283169; _ga_2N895J1MHX=GS2.3.s1747283170$o1$g0$t1747283170$j0$l0$h0; _ga_2N895J1MHX=GS2.2.s1747283170$o1$g0$t1747283170$j0$l0$h0; _ga=GA1.2.943748827.1747283169; _gid=GA1.2.691894314.1748313087; _ga_6B3E4XXQ03=GS2.1.s1748321134$o3$g0$t1748321134$j0$l0$h0'
}

CSV_FILENAME = "Michigan State University.csv"
FIELDNAMES = [
        "Station Name", "Station ID", "Location", "City", "Latitude", "Longitude", "Elevation"
]


def print_sensor_data(data_dict):
    for key, value in data_dict.items():
        if value and value.strip():
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")
    print()  # Tambah baris kosong setelah print selesai

def save_station_data(row, filename=CSV_FILENAME):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        
        writer.writerow(row)
        file.flush()

def sanitize_filename(name):
    """Hapus karakter ilegal dari nama file"""
    return re.sub(r'[\\/*?:"<>|]', '', name).strip()


def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Temukan tabel berdasarkan atribut
    table = soup.find('table', {'width': '100%', 'height': '216', 'border': '0'})
    if not table:
        print("❌ Tabel tidak ditemukan.")
        return data

    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).replace(':', '')
            value = cells[1].get_text(strip=True)

            # Lewati baris kosong
            if label and value and label != '\xa0' and value != '\xa0':
                data[label] = value

    # Tampilkan hasil
    for k, v in data.items():
        print(f"{k}: {v}")
    
    return data


def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


# def parse_html(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     urls = []

#     find_maps = soup.find('map', {'name': "MawnMap"})
#     print(f"🔍 Mencari <map name='MawnMap'>: {find_maps is not None}")
#     if not find_maps:
#         print("Tidak ditemukan <map name='MawnMap'>")
#         return urls

#     area_tags = find_maps.find_all('table')

#     for area in area_tags:
#         href = area.get("href")
#         if href:
#             full_url = f"https://mawn.geo.msu.edu/{href}"
#             urls.append(full_url)
#             # print(full_url)
#         else:
#             print("Area tanpa href")

#     return urls


from bs4 import BeautifulSoup

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    urls = []

    # Definisi atribut tabel utama
    width = "100%"
    height = "100%"
    border = "0"
    bgcolor = "#ffffff"

    # Temukan tabel utama
    find_maps = soup.find('table', {'width': width, 'height': height, 'border': border, 'bgcolor': bgcolor})
    print(f"🔍 Mencari tabel dengan atribut lengkap: {find_maps is not None}")
    if not find_maps:
        print("❌ Tidak ditemukan tabel dengan atribut tersebut")
        return urls

    # Di dalam tabel utama, cari semua <td class="stntabledata">
    td_tags = find_maps.find_all('td', class_='stntabledata')
    print(f"📦 Ditemukan {len(td_tags)} elemen <td class='stntabledata'>")

    # Ambil href dan teks dari <a> di dalam <td>
    for td in td_tags:
        a_tag = td.find('a')
        if a_tag and a_tag.get('href'):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            full_url = f"https://mawn.geo.msu.edu{href}"
            urls.append(full_url)
        else:
            print("⚠️ <td> tanpa <a> atau tanpa href")

    return urls


def extract_data_from_url(html, url=None):

    meta_data = parse_station_info_table(html)
    
    print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    print("")
    
    # Ambil field dari meta_data dengan key lengkap (yang mengandung ':')
    station_name = meta_data.get("Station", "")
    station_id = meta_data.get("Station ID", "")
    location = meta_data.get("Location", "")
    city = meta_data.get("City", "")
    latitude = meta_data.get("Latitude", "")
    longitude = meta_data.get("Longitude", "")
    elevation = meta_data.get("Elevation", "")

    # # Buat struktur data yang diinginkan
    data_save = {
        "Station Name": station_name,
        'Station ID': station_id,
        'Location': location,
        'City': city,
        "Latitude": f"'{latitude}" if latitude else "",
        "Longitude": f"'{longitude}" if longitude else "",
        "Elevation": f"'{elevation}" if elevation else "",
    }


    for key, value in data_save.items():
        if value.strip():
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")
    
    save_station_data(data_save)


def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return


    station_urls = parse_html(html)
    for url in station_urls:
        print(f"🌐 Memproses URL: {url}")
        station_html = get_html(url)
        # print(station_html)
        if station_html:
            extract_data_from_url(station_html, url)
        # break 


if __name__ == "__main__":
    main()
