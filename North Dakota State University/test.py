import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re

from urllib.parse import urlparse

BASE_URL = "https://ndawn.ndsu.nodak.edu"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.1645235476.1747095444; _ga_2MC44RLBN7=GS2.1.s1747611903$o11$g0$t1747611903$j0$l0$h0'
}

CSV_FILENAME = "North Dakota State University.csv"
FIELDNAMES = [
        "Station Name","Station Id", "County", "State", "Latitude", "Longitude", "Elevation", "In service date", "Status"
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

def extract_station_name(soup):
    """Ambil nama stasiun dari elemen <h1>"""
    station_info = soup.find("div", id='station-info')
    title_element = station_info.find('h1')
    if title_element:
        return sanitize_filename(
            title_element.text.replace('NDAWN Station', '')
        )
    return "Unknown_Station"




def download_first_image(html_content, base_url, name_text, save_dir="Image Station"):
    soup = BeautifulSoup(html_content, "html.parser")

    # Temukan div dengan id "pics"
    pics_div = soup.find("div", id="pics")
    if not pics_div:
        print("No image section found.")
        return

    # Temukan <a> pertama yang mengandung href (gambar resolusi tinggi)
    first_image_link = pics_div.find("a", class_="group")
    if not first_image_link:
        print("No image link found.")
        return

    image_url = first_image_link.get("href")  # misalnya "/station.jpg?t=l&s=93&n=1"
    if not image_url:
        print("No image URL found.")
        return

    # Lengkapi dengan base_url jika perlu
    full_image_url = base_url + image_url

    # Tentukan nama file berdasarkan nama stasiun
    extension = os.path.splitext(image_url.split('?')[0])[1] or ".jpg"
    filename = f"{name_text}{extension}"

    # Buat folder jika belum ada
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)

    # Download dan simpan gambar
    try:
        response = requests.get(full_image_url, timeout=10)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Image saved to {filepath}")
    except Exception as e:
        print(f"Failed to download image: {e}")

def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Temukan td dengan id='details'
    details_td = soup.find('td', id='details')
    if not details_td:
        print("Tidak ditemukan <td id='details'>")
        return data

    # Cari tabel di dalamnya
    table = details_td.find('table', class_='layout')
    if not table:
        print("Tidak ditemukan <table class='layout'> di dalam <td id='details'>")
        return data

    # Ambil semua baris di tabel
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2 and 'label' in cells[0].get('class', []):
            key = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            data[key] = value

    return data



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
    areas = []

    find_maps = soup.find('map', id="station-map")
    if not find_maps:
        print("Tidak ditemukan <map id='station-map'>")
        return areas

    area_tags = find_maps.find_all('area')

    for area in area_tags:
        href = area.get("href")
        alt = area.get("alt", "").strip()
        if href:
            full_url = f"https://ndawn.ndsu.nodak.edu{href}"
            areas.append({'url': full_url, 'alt': alt})
            print(f"{alt}: {full_url}")
        else:
            print("Area tanpa href")

    return areas

def extract_data_from_url(html, url=None, area_info=None):
    soup = BeautifulSoup(html, 'html.parser')
    station_name = extract_station_name(soup)

    print(f"✅ Memproses: {station_name}")
    if url:
        print(f"🌐 URL: {url}")

    station_id = None
    if url:
        path_parts = urlparse(url).path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[-2] == 'station':
            station_id = path_parts[-1]

    meta_data = parse_station_info_table(html)

    location = meta_data.get("Location:", "")
    period = meta_data.get("Period of record:", "")
    latitude = meta_data.get("Latitude:", "")
    longitude = meta_data.get("Longitude:", "")
    elevation = meta_data.get("Elevation:", "")

    county = state = ""
    if "," in location:
        county, state = location.split(",", 1)
        county = county.strip()
        state = state.strip()

    in_service_date = status = ""
    if " to " in period:
        in_service_date, status = period.split(" to ", 1)
        in_service_date = in_service_date.strip()
        status = status.strip()

    name_text = ""
    if area_info and url:
        for area in area_info:
            if area['url'] == url:
                name_text = area['alt']
                break

    data_save = {
        "Station Name": str(name_text or ""),
        "Station Id": str(station_id or ""),
        "County": str(county or ""),
        "State": str(state or ""),
        "Latitude": f"'{latitude}" if latitude else "",
        "Longitude": f"'{longitude}" if longitude else "",
        "Elevation": str(elevation or ""),
        "In service date": f"'{in_service_date}" if in_service_date else "",
        "Status": str(status or "")
    }
    for key, value in data_save.items():
        if value is not None and str(value).strip():
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")

    download_first_image(html, BASE_URL, name_text)
    save_station_data(data_save)

def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return

    station_urls = parse_html(html)
    for area in station_urls:
        station_html = get_html(area['url'])
        if station_html:
            extract_data_from_url(station_html, url=area['url'], area_info=station_urls)
        # break  # Uncomment jika hanya ingin test satu URL dulu


if __name__ == "__main__":
    main()
