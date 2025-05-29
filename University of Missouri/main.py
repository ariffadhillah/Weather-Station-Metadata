import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re

BASE_URL = "http://agebb.missouri.edu/weather/stations/index.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '__utmz=160820525.1747094332.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1491667457.1747362224; _scid=GtxVVMTmJbKbmULrIHsGAizhEdKnCwHI; _clck=1oo6rmj%7C2%7Cfvy%7C0%7C1962; _scid_r=E1xVVMTmJbKbmULrIHsGAizhEdKnCwHI62MTQQ; _sctr=1%7C1747328400000; _ga_X5WTGNM3XF=GS2.2.s1747362223$o1$g1$t1747362239$j44$l0$h0; __utma=160820525.1810650120.1747094332.1748367047.1748386769.8; __utmc=160820525; __utmt=1; __utmb=160820525.1.10.1748386769'
}


CSV_FILENAME = "University of Missouri.csv"
FIELDNAMES = [
        "Station Name", "City", "State", "Latitude", "Longitude"
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

def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    urls = []

    # Mencari div dengan class "column2"
    find_location = soup.find('div', class_="column2")
    print(f"🔍 Mencari tabel dengan atribut lengkap: {find_location is not None}")
    if not find_location:
        print("❌ Tidak ditemukan tabel dengan atribut tersebut")
        return urls

    # Mencari semua <option> di dalam <select>
    select_tag = find_location.find('select')
    if not select_tag:
        print("❌ Tidak ditemukan elemen <select>")
        return urls

    option_tags = select_tag.find_all('option')
    print(f"📦 Ditemukan {len(option_tags)} elemen <option>")

    for option in option_tags:
        value = option.get('value')
        if value and value.startswith("http"):
            urls.append(value)
            print(f"🔗 Ditemukan URL: {value}")

    return urls


def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Temukan tabel utama berdasarkan atribut
    table = soup.find('table', {
        'width': '700',
        'cellpadding': '2',
        'cellspacing': '0',
        'border': '0',
        'align': 'center'
    })

    if not table:
        print("❌ Tabel tidak ditemukan.")
        return data

    # Ambil baris kedua
    row = table.find_all('tr')[1]
    
    # Ambil lokasi
    location_font = row.find('font', {'size': '2', 'face': 'Arial'})
    if location_font:
        full_location = location_font.get_text(strip=True)
        data['location'] = full_location

        # Pisah jadi city dan state
        if ',' in full_location:
            city, state = full_location.split(',', 1)
            data['city'] = city.strip()
            data['state'] = state.strip()

    # Ambil URL gambar
    img = row.find('img')
    if img and img.get('src'):
        data['image_url'] = img['src']

    # Ambil koordinat dari link
    latlon_link = row.find('a')
    if latlon_link:
        coord_text = latlon_link.get_text(strip=True)
        data['coordinates'] = coord_text

        # Pisah jadi latitude dan longitude
        if 'Lat:' in coord_text and 'Lon:' in coord_text:
            lat_part = coord_text.split('Lat:')[1].split('°')[0].strip()
            lon_part = coord_text.split('Lon:')[1].split('°')[0].strip()
            data['latitude'] = lat_part
            data['longitude'] = lon_part

    return data


def extract_data_from_url(html, url=None):

    meta_data = parse_station_info_table(html)
    
    print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    print("")
    


    # Ambil field dari meta_data dengan key lengkap (yang mengandung ':')
    station_name = meta_data.get("city", "")
    city = meta_data.get("city", "")
    state = meta_data.get("state", "")
    latitude = meta_data.get("latitude", "")
    longitude = meta_data.get("longitude", "")

    # # Buat struktur data yang diinginkan
    data_save = {
        "Station Name": station_name,
        'City': city,
        'State': state,
        "Latitude": f"'{latitude}" if latitude else "",
        "Longitude": f"'{longitude}" if longitude else "",
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
