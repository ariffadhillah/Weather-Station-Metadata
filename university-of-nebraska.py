import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re


BASE_URL = "https://mesonet.unl.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga_R0NKRQLKF9=GS2.1.s1747284460$o1$g1$t1747284489$j0$l0$h0; _ga_GN0QTD6E2N=GS2.1.s1747284460$o1$g1$t1747284489$j0$l0$h0; _ga_BQ463012SY=GS2.1.s1747284398$o1$g1$t1747284590$j0$l0$h0; _ga_4EPFEB277P=GS2.1.s1747284401$o1$g1$t1747284590$j0$l0$h0; _ga=GA1.1.1503352859.1747095907; _ga_JCZVPC9VTT=GS2.1.s1747450403$o5$g1$t1747450535$j0$l0$h0'
}

CSV_FILENAME = "University of Nebraska.csv"
FIELDNAMES = [
        "Station Name", "County", "State", "Latitude", "Longitude", "Elevation", "In service date", "Status"
]


def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_drupal_settings(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Temukan semua tag <script>
    scripts = soup.find_all('script')
    
    for script in scripts:
        if script.string and 'Drupal.settings' in script.string:
            # Ekstrak isi objek JSON dari script menggunakan regex
            match = re.search(r'Drupal\.settings\s*,\s*(\{.*\})\s*\);', script.string, re.DOTALL)
            if match:
                json_str = match.group(1)
                
                # Ubah ke string JSON valid (hapus trailing koma, fix escape)
                json_str = json_str.replace("\\/", "/")

                try:
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError as e:
                    print("Gagal parsing JSON:", e)
                    return None

    print("Drupal.settings tidak ditemukan.")
    return None

import json

def print_full_point_data(point):
    print("\n===== DATA POINT =====")

    # ID utama
    print(f"ID: {point.get('id')}")

    # CONDITIONS
    print("\n-- CONDITIONS --")
    conditions = point.get("conditions")
    if isinstance(conditions, dict):
        for key, value in conditions.items():
            print(f"{key}: {value}")
    else:
        print("No conditions data available.")

    # POSITION
    print("\n-- POSITION --")
    pos = point.get("pos")
    if isinstance(pos, dict):
        for section, pos_data in pos.items():
            print(f"{section.upper()}:")
            if isinstance(pos_data, dict):
                for key, value in pos_data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {pos_data}")
    else:
        print("No position data available.")

    # DESCRIPTION
    print("\n-- DESCRIPTION --")
    desc = point.get("description")
    if isinstance(desc, dict):
        for key, value in desc.items():
            print(f"{key}: {value}")
    else:
        print("No description data available.")

    # IMAGES
    print("\n-- IMAGES --")
    images = point.get("images")
    if isinstance(images, list):
        for img_url in images:
            print(img_url)
    else:
        print("No images available.")

    print("=" * 40)


# def extract_data_from_url(html, url=None):
#     soup = BeautifulSoup(html, 'html.parser')
#     drupal_data = extract_drupal_settings(html)

#     if drupal_data:
#         print("Theme:", drupal_data.get("ajaxPageState", {}).get("theme"))
#         print("Token:", drupal_data.get("ajaxPageState", {}).get("theme_token"))

#         points_data = drupal_data.get("mesonet", {}).get("graph", {}).get("points", {})

#         if points_data:
#             print("\nData Points:")
#             for point_id, raw_point in points_data.items():
#                 try:
#                     point = json.loads(raw_point)

#                     conditions = point.get("conditions")
#                     if conditions:
#                         print(f"ID: {point_id}")
#                         print("Name:", conditions.get("Name"))
#                         print("Latitude:", conditions.get("Latitude"))
#                         print("Longitude:", conditions.get("Longitude"))
#                         print("Temperature:", conditions.get("Temperature"))
#                         print("Dewpoint:", conditions.get("Dewpoint"))
#                         print("Relative Humidity:", conditions.get("Relative Humidity"))
#                         print("images:", conditions.get("images"))
#                         print("-" * 40)
#                     else:
#                         print(f"ID: {point_id} - Tidak ada 'conditions'")
#                 except json.JSONDecodeError as e:
#                     print(f"Error decoding point {point_id}: {e}")

def extract_data_from_url(html, url=None):
    soup = BeautifulSoup(html, 'html.parser')
    drupal_data = extract_drupal_settings(html)

    if not drupal_data:
        print("Data Drupal tidak ditemukan.")
        return

    points = drupal_data.get("mesonet", {}).get("graph", {}).get("points", {})
    
    if not points:
        print("Data points tidak ditemukan.")
        return

    for point_id, raw_point in points.items():
        try:
            # Decode JSON string di setiap point
            point = json.loads(raw_point)
        except json.JSONDecodeError as e:
            print(f"Gagal decode JSON untuk ID {point_id}: {e}")
            continue

        # Ambil bagian-bagian penting dari description
        desc = point.get("description", {})

        # Ambil URL gambar
        images = point.get("images", [])
        image_urls = "\n".join(images) if images else ""

        # Buat dictionary data_save
        data_save = {
            "ID": point.get("id", ""),
            "Name": desc.get("Name", ""),
            "Latitude": desc.get("Latitude", ""),
            "Longitude": desc.get("Longitude", ""),
            "Elevation": desc.get("Elevation", ""),
            "Client": desc.get("Client", ""),
            "all image url": image_urls
        }


        # Cetak hasil
        print("\n===== DATA POINT =====")
        for key, value in data_save.items():
            if value.strip():
                print(f"{key}: {value}")
            else:
                print(f"{key}: Data tidak tersedia")
        print("=" * 40)


def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return
    
    # Tambahkan baris ini untuk memproses HTML yang sudah diambil
    extract_data_from_url(html, BASE_URL)


if __name__ == "__main__":
    main()
