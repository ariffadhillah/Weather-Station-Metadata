import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re

# http://www.georgiaweather.net/index.php?variable=ID&content=IF

BASE_URL = "http://www.georgiaweather.net/index.php?variable=ID&content=IF"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.423061837.1747059135; _ga_1HBFZE8FPB=GS2.1.s1748421055$o23$g1$t1748422029$j59$l0$h0'
}


# CSV_FILENAME = "Latitude and Longitude----University of Georgia.csv"
# FIELDNAMES = [
#         "Station Name", 'City', 'County', 'Zip Code', "Latitude", "Longitude", "Elevation", "Local Site Name"
# ]


# def save_station_data(row, filename=CSV_FILENAME):
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
#         writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
#         if not file_exists or os.stat(filename).st_size == 0:
#             writer.writeheader()
        
#         writer.writerow(row)
#         file.flush()


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
    data = {}
    data_list = []

    # Temukan tabel utama berdasarkan atribut
    table = soup.find('table', {
        'width': '100%'
        # 'cellpadding': '0',
        # 'cellspacing': '1',
        # 'align': 'left',
        # 'border':'0',
        # 'height':'500'
    })

    if not table:
        print("❌ Tabel tidak ditemukan.")
        return data

    # Ambil baris kedua
    rows = table.find_all('tr')

    for row in rows[1:]:
        cols = row.find_all('td')
        cols = [col.get_text(strip=True) for col in cols]
        if len(cols) == 7:
            data = {
                "City": cols[0],
                "County": cols[1],
                # "Zip Code": cols[2],
                "Local Site Name": cols[2],
                "Site": cols[3],
                "Date of Installation": cols[4],
            }
            data_list.append(data)
            # print(data_list)

    return data_list


def extract_data_from_url(html, url=None):

    meta_data_list = parse_html(html)

    if not meta_data_list:
        print("❌ Tidak ada data yang ditemukan dalam tabel.")
        return

    for meta_data in meta_data_list:
        print(json.dumps(meta_data, indent=4, ensure_ascii=False))
        print("")

        # station_name = meta_data.get("City", "")
        # city = meta_data.get("City", "")
        # county = meta_data.get("County", "")
        # zip_code = meta_data.get("Zip Code","")
        # latitude = meta_data.get("Latitude", "")
        # longitude = meta_data.get("Longitude", "")
        # elevation = meta_data.get("Elevation", "")
        # local_site_name = meta_data.get("Local Site Name", "")

        # data_save = {
        #     "Station Name": station_name,
        #     'City': city,
        #     'County': county,
        #     'Zip Code': zip_code,        
        #     "Latitude": f"'{latitude}" if latitude else "",
        #     "Longitude": f"'{longitude}" if longitude else "", 
        #     "Elevation": elevation,
        #     'Local Site Name': local_site_name
        # }

        # for key, value in data_save.items():
        #     if value.strip():
        #         print(f"{key}: {value}")
        #     else:
        #         print(f"{key}: Data tidak tersedia")

        # save_station_data(data_save)

    




def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return


    extract_data_from_url(html)




if __name__ == "__main__":
    main()
