import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

BASE_URL = "https://mesonet.unl.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga_R0NKRQLKF9=GS2.1.s1747284460$o1$g1$t1747284489$j0$l0$h0; _ga_GN0QTD6E2N=GS2.1.s1747284460$o1$g1$t1747284489$j0$l0$h0; _ga_BQ463012SY=GS2.1.s1747284398$o1$g1$t1747284590$j0$l0$h0; _ga_4EPFEB277P=GS2.1.s1747284401$o1$g1$t1747284590$j0$l0$h0; _ga=GA1.1.1503352859.1747095907; _ga_JCZVPC9VTT=GS2.1.s1747450403$o5$g1$t1747450535$j0$l0$h0'
}

CSV_FILENAME = "University of Nebraska.csv"
FIELDNAMES = [
            "Station Name", "Latitude", "Longitude", "Elevation","In service date","Status","Client"
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


def download_images(image_urls, name, station_id, folder="University of Nebraska"):
    if not isinstance(image_urls, list):
        print("❌ image_urls bukan list, melainkan:", type(image_urls))
        return
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for idx, url in enumerate(image_urls, 1):
        try:
            print(f"[↓] Mendownload dari: {url}")
            response = requests.get(url)
            response.raise_for_status()
            
            # Ekstensi dari URL (png, jpg, dll)
            ext = url.split('.')[-1].split("?")[0]
            filename = f"{name}-{station_id}-image_{idx}.{ext}"
            filepath = os.path.join(folder, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"[✔] Tersimpan: {filepath}")
        except Exception as e:
            print(f"[✘] Gagal download {url}: {e}")

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

        station_id = point.get("id", "").strip()
        name = desc.get("Name", "").strip()
        period = desc.get("Period of Record", "")



        # Inisialisasi
        period_only = period.strip()
        status = ""

        # Coba ekstrak tanggal lengkap (YYYY-MM-DD) dari awal string
        match = re.search(r"\d{4}-\d{2}-\d{2}", period)
        if match:
            period_only = match.group(0)

        # Coba ambil status dari bagian akhir (misalnya "Present")
        if "-" in period:
            parts = [p.strip() for p in period.split("-")]
            if len(parts) >= 2:
                last_part = parts[-1]
                if "Present" in last_part or "present" in last_part:
                    status = last_part

        data_save = {
            "Station ID": station_id,
            "Station Name": name,
            "Latitude": desc.get("Latitude", ""),
            "Longitude": desc.get("Longitude", ""),
            "Elevation": desc.get("Elevation", ""),
            "In service date": period_only,
            "Status": status,
            "Client": desc.get("Client", ""),
            "all image url": image_urls
        }
        # print(data_save)
        image_urls_list = image_urls.splitlines()

        # Gunakan folder tetap
        folder_name = "University of Nebraska"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Bersihkan nama untuk digunakan di nama file
        safe_name = name.replace(" ", "_").replace("/", "-")

        # Download dan simpan gambar
        for url in image_urls_list:
            filename_from_url = url.split('/')[-1]
            base, ext = os.path.splitext(filename_from_url)

            new_filename = f"{safe_name}-{station_id}-{base}{ext}"
            save_path = os.path.join(folder_name, new_filename)

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Saved: {save_path}")
                else:
                    print(f"Failed to download (status {response.status_code}): {url}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")

        # # Cetak hasil
        # print("\n===== DATA POINT =====")
        # for key, value in data_save.items():
        #     if value.strip():
        #         print(f"{key}: {value}")
        #     else:
        #         print(f"{key}: Data tidak tersedia")
        # print("=" * 40)

        # save_station_data(data_save)
        
        # Simpan gambar-gambar
        


def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return
    
    # Tambahkan baris ini untuk memproses HTML yang sudah diambil
    extract_data_from_url(html, BASE_URL)


if __name__ == "__main__":
    main()
