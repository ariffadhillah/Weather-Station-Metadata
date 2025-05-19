import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re


BASE_URL = "https://ndawn.ndsu.nodak.edu"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.1645235476.1747095444; _ga_2MC44RLBN7=GS2.1.s1747611903$o11$g0$t1747611903$j0$l0$h0'
}

CSV_FILENAME = "North Dakota State University.csv"
FIELDNAMES = [
        "Station Name", "County", "State", "Latitude", "Longitude", "Elevation", "In service date", "Status"
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

def download_station_images(html, base_url, save_folder="North Dakota State University"):
    soup = BeautifulSoup(html, 'html.parser')
    pics_div = soup.find('div', id='pics')
    if not pics_div:
        print("Gambar tidak ditemukan.")
        return

    os.makedirs(save_folder, exist_ok=True)

    img_tags = pics_div.find_all('img')
    for img in img_tags:
        img_src = img.get('src')
        img_alt = img.get('alt', 'image')

        # Bersihkan nama file dari karakter ilegal
        safe_filename = re.sub(r'[^\w\s-]', '', img_alt).strip().replace(' ', '_') + '.jpg'
        img_url = urljoin(base_url, img_src)

        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                file_path = os.path.join(save_folder, safe_filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✔ Gambar disimpan: {file_path}")
            else:
                print(f"✘ Gagal mengunduh {img_url} - status code: {response.status_code}")
        except Exception as e:
            print(f"✘ Error saat mengunduh {img_url}: {e}")


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
    urls = []

    find_maps = soup.find('map', id="station-map")
    if not find_maps:
        print("Tidak ditemukan <map id='station-map'>")
        return urls

    area_tags = find_maps.find_all('area')

    for area in area_tags:
        href = area.get("href")
        if href:
            full_url = f"https://ndawn.ndsu.nodak.edu{href}"
            urls.append(full_url)
            print(full_url)
        else:
            print("Area tanpa href")

    return urls

def extract_data_from_url(html, url=None):
    soup = BeautifulSoup(html, 'html.parser')
    station_name = extract_station_name(soup)

    print(f"✅ Memproses: {station_name}")
    if url:
        print(f"🌐 URL: {url}")

    download_station_images(html, BASE_URL)

    meta_data = parse_station_info_table(html)
    
    # print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    # print("")
    
    # Ambil field dari meta_data dengan key lengkap (yang mengandung ':')
    location = meta_data.get("Location:", "")
    period = meta_data.get("Period of record:", "")
    latitude = meta_data.get("Latitude:", "")
    longitude = meta_data.get("Longitude:", "")
    elevation = meta_data.get("Elevation:", "")

    # Pecah lokasi menjadi County dan State
    county = state = ""
    if "," in location:
        county, state = location.split(",", 1)
        county = county.strip()
        state = state.strip()

    # Pecah period menjadi tanggal dan status
    in_service_date = status = ""
    if " to " in period:
        in_service_date, status = period.split(" to ", 1)
        in_service_date = in_service_date.strip()
        status = status.strip()

    # Buat struktur data yang diinginkan
    data_save = {
        "Station Name": station_name,
        "County": county,
        "State": state,
        "Latitude": f"'{latitude}" if latitude else "",
        "Longitude": f"'{longitude}" if longitude else "",
        "Elevation": elevation,
        "In service date": f"'{in_service_date}",
        "Status": status
    }


    for key, value in data_save.items():
        if value.strip():
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")

    # print(data_save)
    save_station_data(data_save)

def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return


    station_urls = parse_html(html)
    for url in station_urls:
        station_html = get_html(url)
        if station_html:
            extract_data_from_url(station_html, url)
        # break 


if __name__ == "__main__":
    main()
