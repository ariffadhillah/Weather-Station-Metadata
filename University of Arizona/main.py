import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re
import time

BASE_URL = "https://azmet.arizona.edu/about/station-metadata"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}


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



def parse_station_detail(station_id):
    detail_url = f"https://azmet.arizona.edu/about/station-metadata/{station_id}"
    print(f"\n🌐 Membuka URL: {detail_url}")

    html = get_html(detail_url)
    if not html:
        print(f"❌ Gagal mengambil halaman detail untuk station_id: {station_id}")
        return

    soup = BeautifulSoup(html, 'html.parser')

    # Contoh: ambil konten utama dari halaman detail
    main_content = soup.find('main')
    if main_content:
        print(f"\n📄 Detail untuk {station_id}:\n")
        title = soup.find('h2', class_='my-0 bold text-midnight')
        print(title.text.strip())
        # print(main_content.get_text(strip=True)[:300])  # Cetak sebagian isi untuk preview
    else:
        print(f"⚠️ Tidak ditemukan konten utama untuk station_id: {station_id}")


def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
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