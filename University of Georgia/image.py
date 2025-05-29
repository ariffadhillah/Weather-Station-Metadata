import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://www.georgiaweather.net/index.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.423061837.1747059135; _ga_1HBFZE8FPB=GS2.1.s1748421055$o23$g1$t1748422029$j59$l0$h0'
}


# CSV_FILENAME = "University of Missouri.csv"
# FIELDNAMES = [
#         "Station Name", "City", "State", "Latitude", "Longitude"
# ]


# http://www.georgiaweather.net/index.php?content=calculator&variable=CC&site=ALAPAHA
# http://www.georgiaweather.net/mindex.php?variable=SI&site=ALAPAHA


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

    find_form = soup.find('form', {'name': "myform"})
    print(f"🔍 Mencari <form name='myform'>: {find_form is not None}")
    if not find_form:
        print("Tidak ditemukan <form name='myform'>")
        return urls

    option_tags = find_form.find_all('option')
    print(f"📦 Ditemukan {len(option_tags)} elemen <option>")

    for option in option_tags:
        value = option.get('value')  # contoh: '?content=calculator&variable=CC&site=ALAPAHA'
        if value:
            full_url = BASE_URL + value
            parsed_url = urlparse(full_url)
            query_params = parse_qs(parsed_url.query)
            site_id = query_params.get("site", [None])[0]  # ambil nilai site

            if site_id:
                final_url = f"http://www.georgiaweather.net/mindex.php?variable=SI&site={site_id}"
                urls.append(final_url)
                print(f"🔗 Dibuat URL: {final_url}")

    return urls


# import os
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# BASE_URL = "http://www.georgiaweather.net/"  # Sesuaikan jika berbeda

# def extract_center_image(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     img_tag = soup.find('img', src=lambda x: x and '_center' in x)

#     if not img_tag:
#         print("❌ Gambar '_center' tidak ditemukan.")
#         return None

#     img_src = img_tag['src']
#     full_url = urljoin(BASE_URL, img_src)

#     # Ambil nama seperti ALMA_center.jpg lalu ubah ke ALMA.jpg
#     original_filename = os.path.basename(img_src)
#     station_name = original_filename.split('_')[0] + ".jpg"

#     # Pastikan folder ada
#     os.makedirs("Image Station", exist_ok=True)

#     # Path penyimpanan
#     save_path = os.path.join("Image Station", station_name)

#     # Download gambar
#     try:
#         response = requests.get(full_url)
#         if response.status_code == 200:
#             with open(save_path, "wb") as f:
#                 f.write(response.content)
#             print(f"✅ Gambar berhasil disimpan: {save_path}")
#         else:
#             print(f"❌ Gagal mengunduh gambar. Status code: {response.status_code}")
#     except Exception as e:
#         print(f"⚠️ Terjadi kesalahan saat mengunduh gambar: {e}")

#     return save_path

BASE_URLimage = "http://www.georgiaweather.net/"

def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    

    soup = BeautifulSoup(html, 'html.parser')
    
    # Cari semua tag <img> yang src-nya mengandung '_center'
    center_img = soup.find('img', src=lambda x: x and '_center' in x)

    if not center_img:
        print("❌ Gambar '_center' tidak ditemukan.")
        return None

    # Ambil link gambar
    img_src = center_img['src']
    full_url = urljoin(BASE_URLimage, img_src)  # pastikan URL lengkap

    # Ambil nama file asli misalnya ALMA_center.jpg
    filename = os.path.basename(img_src)

    # Ambil nama sebelum '_center' → ALMA
    station_name = filename.split('_')[0] + ".jpg"

    # Buat folder jika belum ada
    os.makedirs("Image Station", exist_ok=True)
    save_path = os.path.join("Image Station", station_name)

    # Download gambar
    try:
        response = requests.get(full_url)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Gambar berhasil disimpan: {save_path}")
        else:
            print(f"❌ Gagal mengunduh gambar. Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Terjadi kesalahan saat download: {e}")

    return save_path



def extract_data_from_url(html, url=None):

    meta_data = parse_station_info_table(html)
    
    print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    print("")



def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return


    station_urls = parse_html(html)
    # print(station_urls)
    for url in station_urls[1:]:
        print(f"🌐 Memproses URL: {url}")
        station_html = get_html(url)
        # print(station_html)
        if station_html:
            extract_data_from_url(station_html, url)
        break 


if __name__ == "__main__":
    main()
