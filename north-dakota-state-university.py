import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re


BASE_URL = "https://ndawn.ndsu.nodak.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.1645235476.1747095444; _ga_2MC44RLBN7=GS2.1.s1747611903$o11$g0$t1747611903$j0$l0$h0'
}

# CSV_FILENAME = "Rutgers University.csv"
# FIELDNAMES = [

# ]


# def print_sensor_data(data_dict):
#     for key, value in data_dict.items():
#         if value and value.strip():
#             print(f"{key}: {value}")
#         else:
#             print(f"{key}: Data tidak tersedia")
#     print()  # Tambah baris kosong setelah print selesai

# def save_station_data(row, filename=CSV_FILENAME):
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
#         writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
#         if not file_exists or os.stat(filename).st_size == 0:
#             writer.writeheader()
        
#         writer.writerow(row)
#         file.flush()

def sanitize_filename(name):
    """Hapus karakter ilegal dari nama file"""
    return re.sub(r'[\\/*?:"<>|]', '', name).strip()

def extract_station_name(soup):
    """Ambil nama stasiun dari elemen <h1>"""
    title_element = soup.find('h1', class_='title')
    if title_element:
        return sanitize_filename(
            title_element.text.replace('- Forecast, Radar and Current Weather', '')
        )
    return "Unknown_Station"

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
    

    
    # print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    # print("")




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
