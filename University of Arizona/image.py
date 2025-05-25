import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re
import time
from urllib.parse import urlparse

BASE_URL = "https://azmet.arizona.edu/about/station-metadata"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"❌ Error saat ambil HTML: {e}")
    return None

def extract_bg_image_from_embedded_css(html):
    soup = BeautifulSoup(html, "html.parser")
    styles = soup.find_all("style")

    for style in styles:
        css = style.get_text()
        pattern = r'#station-bg-img\s*{\s*[^}]*background-image\s*:\s*url\(([^)]+)\)'
        match = re.search(pattern, css)
        if match:
            return match.group(1).strip(' "\'')
    return None

def extract_sensor_info(soup):
    all_card_data = []

    cards = soup.find_all("div", class_="card-body")
    for card in cards:
        section_title_tag = card.find("h4", class_="my-0")
        if not section_title_tag:
            continue

        section_name = section_title_tag.get_text(strip=True)
        info_dict = {"Section": section_name}

        # Ambil semua span dan text setelahnya
        spans = card.find_all("span")
        for span in spans:
            label = span.get_text(strip=True).strip(":").upper()
            # ambil text setelah <span> (yaitu next_sibling)
            value = span.next_sibling
            if value:
                text = value.strip()
                if text:
                    info_dict[label] = text

        all_card_data.append(info_dict)

    return all_card_data


def extract_table_data(soup):
    table = soup.find('table', class_='table table-striped table-bordered table-hover cols-10 p-2')
    if not table:
        print("❌ Tabel tidak ditemukan.")
        return []

    rows = table.find_all('tr')
    data_list = []

    for row in rows[1:]:  # Skip header
        cols = row.find_all('td')
        if len(cols) < 10:
            continue  # Skip jika kolom tidak lengkap

        data = {
            "Station Name": cols[0].get_text(strip=True),
            "Symbol": cols[1].get_text(strip=True),
            "Station ID": cols[2].get_text(strip=True),
            "County": cols[3].get_text(strip=True),
            "Latitude": cols[4].get_text(strip=True),
            "Longitude": cols[5].get_text(strip=True),
            "Elevation (ft)": cols[6].get_text(strip=True),
            "Elevation (m)": cols[7].get_text(strip=True),
            "Status": cols[8].get_text(strip=True),
            "Description": cols[9].get_text(strip=True),
        }
        data_list.append(data)

    return data_list

def get_extension_from_url(url):
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1]
    return ext if ext else ".jpg"


def download_image(url, station_id):
    folder = "Image Station"
    os.makedirs(folder, exist_ok=True)
    ext = get_extension_from_url(url)
    filename = f"{station_id}{ext}"
    filepath = os.path.join(folder, filename)

    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"📥 Gambar disimpan: {filepath}")
        else:
            print("❌ Gagal mengunduh gambar.")
    except Exception as e:
        print(f"❌ Error saat download gambar: {e}")
        

def parse_station_detail(station_id):
    base_url = "https://azmet.arizona.edu"
    detail_url = f"{base_url}/about/station-metadata/{station_id}"
    print(f"\n🌐 Membuka URL: {detail_url}")

    html = get_html(detail_url)
    if not html:
        print("❌ Gagal ambil HTML halaman detail.")
        return

    image_url = extract_bg_image_from_embedded_css(html)
    if image_url:
        # Lengkapi URL jika relatif
        if image_url.startswith("/"):
            image_url = base_url + image_url
        print(f"✅ Gambar latar belakang: {image_url}")
        download_image(image_url, station_id)
    else:
        print("❌ Tidak menemukan gambar latar belakang.")
# Contoh:


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    parse_station_detail("aguila")
    station_data = extract_table_data(soup)


    for entry in station_data:
        print(entry)





def main():
    base_html = get_html(BASE_URL)
    if not base_html:
        print("Gagal mendapatkan HTML awal.")
        return

    soup = BeautifulSoup(base_html, 'html.parser')
    stations = extract_table_data(soup)

    for station in stations:
        station_id = station.get("Station ID")
        if station_id:
            parse_station_detail(station_id)
            time.sleep(2)  # Hindari terlalu cepat ke server





if __name__ == "__main__":
    main()



# table table-striped table-bordered table-hover cols-10 p-2