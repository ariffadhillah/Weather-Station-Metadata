import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re


BASE_URL = "http://chiliweb.southalabama.edu/station_metadata.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}


def get_html(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
# http://chiliweb.southalabama.edu/station_metadata.php?station={value_station}&{value_metadata}&dir=n&view=in

# def parse_option(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     urls = []

#     find_panel_heading = soup.find('div', class_='panel-heading')
#     if not find_panel_heading:
#         print("Elemen <div class='panel-heading'> tidak ditemukan.")
#         return urls

#     # Cari elemen <select> di dalam panel-heading
#     select_tag_station = find_panel_heading.find('select', {'name':'station'} )
#     if not select_tag_station:
#         print("Elemen <select> tidak ditemukan di dalam panel-heading.")
#         return urls

#     # Ambil semua option
#     options_station = select_tag_station.find_all('option')
#     if not options_station:
#         print("Tidak ada elemen <option> ditemukan.")
#     else:
#         print("Daftar option station yang ditemukan:")
#         for opt_station in options_station:
#             value_station = opt_station.get('value')
#             text_station = opt_station.text.strip()
#             print(f"Value: {value_station}, Text: {text_station}")


#     # Cari elemen <select> di dalam panel-heading
#     metadata_tag = find_panel_heading.find('select', {'name':'metadata'} )
#     if not metadata_tag:
#         print("Elemen <select> tidak ditemukan di dalam panel-heading.")
#         return urls

#     # Ambil semua option
#     options_metadata = metadata_tag.find_all('option')
#     if not options_metadata:
#         print("Tidak ada elemen <option> ditemukan.")
#     else:
#         print("Daftar option meta data yang ditemukan:")
#         for opt_metadata in options_metadata:
#             value_metadata = opt_metadata.get('value')
#             text_metadata = opt_metadata.text.strip()
#             print(f"Value: {value_metadata}, Text: {text_metadata}")



def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    station_options = []
    metadata_options = []

    find_panel_heading = soup.find('div', class_='panel-heading')
    if not find_panel_heading:
        print("Elemen <div class='panel-heading'> tidak ditemukan.")
        return station_options, metadata_options

    # Ambil select station
    select_tag_station = find_panel_heading.find('select', {'name': 'station'})
    if select_tag_station:
        options_station = select_tag_station.find_all('option')
        for opt in options_station:
            value = opt.get('value')
            text = opt.text.strip()
            if value:  # abaikan value kosong
                station_options.append({'value': value, 'text': text})

    # Ambil select metadata
    select_tag_metadata = find_panel_heading.find('select', {'name': 'metadata'})
    if select_tag_metadata:
        options_metadata = select_tag_metadata.find_all('option')
        for opt in options_metadata:
            value = opt.get('value')
            text = opt.text.strip()
            if value:
                metadata_options.append({'value': value, 'text': text})

    return station_options, metadata_options

def loop_options_and_scrape(base_html):
    station_options, metadata_options = parse_html(base_html)

    if not station_options or not metadata_options:
        print("Data station atau metadata kosong. Tidak dapat melanjutkan.")
        return
# http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&metadata=instrument&dir=n&view=in
# http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&metadata=eventlog&dir=n&view=in
# http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&metadata=images&dir=n&view=in
# http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&metadata=satellite&dir=n&view=in


# Fetching URL: http://chiliweb.southalabama.edu/station_metadata.php?station=agricola=instrument&dir=n&view=in
#   >> Title halaman: CHILI - Center for Hurricane Intensity and Landfall Investigation
# Fetching URL: http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&eventlog&dir=n&view=in
#   >> Title halaman: CHILI - Center for Hurricane Intensity and Landfall Investigation
# Fetching URL: http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&images&dir=n&view=in
#   >> Title halaman: CHILI - Center for Hurricane Intensity and Landfall Investigation
# Fetching URL: http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&satellite&dir=n&view=in
#   >> Title halaman: CHILI - Center for Hurricane Intensity and Landfall Investigation
# Fetching URL: http://chiliweb.southalabama.edu/station_metadata.php?station=agricola&dataproc&dir=n&view=in

    print("Mulai looping kombinasi URL...\n")
    for station in station_options:
        for meta in metadata_options:
            url = f"http://chiliweb.southalabama.edu/station_metadata.php?station={station['value']}&metadata={meta['value']}&dir=n&view=in"
            print(f"Fetching URL: {url}")
            html = get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.text if soup.title else "Tidak ada <title>"
                print(f"  >> Title halaman: {title}")
            else:
                print(f"  >> Gagal fetch: {url}")



def main():
    base_html = get_html(BASE_URL)
    if not base_html:
        print("Gagal mendapatkan HTML awal.")
        return

    loop_options_and_scrape(base_html)



if __name__ == "__main__":
    main()
