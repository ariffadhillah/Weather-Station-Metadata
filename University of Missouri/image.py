import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

BASE_URL = "http://agebb.missouri.edu/weather/stations/index.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.3.943748827.1747283169; _ga_2N895J1MHX=GS2.3.s1747283170$o1$g0$t1747283170$j0$l0$h0; _ga_2N895J1MHX=GS2.2.s1747283170$o1$g0$t1747283170$j0$l0$h0; _ga=GA1.2.943748827.1747283169; _gid=GA1.2.691894314.1748313087; _ga_6B3E4XXQ03=GS2.1.s1748321134$o3$g0$t1748321134$j0$l0$h0'
}

def download_image(html, station_name):
    soup = BeautifulSoup(html, 'html.parser')

    # Temukan <td> dengan atribut tertentu
    table = soup.find('td', {
        'width': '180',
        'align': 'center',
        'rowspan': '2',
        'valign': 'top'
    })

    if not table:
        print("❌ Table dengan atribut tersebut tidak ditemukan.")
        return

    # Temukan tag <img> di dalam table tersebut
    img_tag = table.find('img')
    if not img_tag or not img_tag.get('src'):
        print("❌ Gambar tidak ditemukan di dalam table.")
        return

    # Ambil URL gambar
    img_src = img_tag['src'].strip()
    img_url = img_src  # bisa tambahkan domain jika perlu

    # Ambil ekstensi dari gambar
    file_ext = os.path.splitext(img_src)[-1]  # contoh: '.jpg'

    # Buat folder jika belum ada
    folder_name = "Image Station"
    os.makedirs(folder_name, exist_ok=True)

    # Buat nama file baru berdasarkan station_name
    safe_name = station_name.replace(" ", "_")  # jaga-jaga jika ada spasi
    new_filename = f"{safe_name}{file_ext}"
    save_path = os.path.join(folder_name, new_filename)

    # Download gambar
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Gambar berhasil diunduh dan disimpan di: {save_path}")
    except Exception as e:
        print(f"❌ Gagal mendownload gambar: {e}")

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

    # Mencari div dengan class "column2"
    find_location = soup.find('div', class_="column2")
    print(f"🔍 Mencari tabel dengan atribut lengkap: {find_location is not None}")
    if not find_location:
        print("❌ Tidak ditemukan tabel dengan atribut tersebut")
        return urls

    # Mencari semua <option> di dalam <select>
    select_tag = find_location.find('select')
    if not select_tag:
        print("❌ Tidak ditemukan elemen <select>")
        return urls

    option_tags = select_tag.find_all('option')
    print(f"📦 Ditemukan {len(option_tags)} elemen <option>")

    for option in option_tags:
        value = option.get('value')
        if value and value.startswith("http"):
            urls.append(value)
            print(f"🔗 Ditemukan URL: {value}")

    return urls


def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    # Temukan tabel utama berdasarkan atribut
    table = soup.find('table', {
        'width': '700',
        'cellpadding': '2',
        'cellspacing': '0',
        'border': '0',
        'align': 'center'
    })

    if not table:
        print("❌ Tabel tidak ditemukan.")
        return data

    # Ambil baris kedua
    row = table.find_all('tr')[1]
    
    # Ambil lokasi
    location_font = row.find('font', {'size': '2', 'face': 'Arial'})
    if location_font:
        full_location = location_font.get_text(strip=True)
        data['location'] = full_location

        # Pisah jadi city dan state
        if ',' in full_location:
            city, state = full_location.split(',', 1)
            data['city'] = city.strip()
            data['state'] = state.strip()

    # Ambil URL gambar
    img = row.find('img')
    if img and img.get('src'):
        data['image_url'] = img['src']

    # Ambil koordinat dari link
    latlon_link = row.find('a')
    if latlon_link:
        coord_text = latlon_link.get_text(strip=True)
        data['coordinates'] = coord_text

        # Pisah jadi latitude dan longitude
        if 'Lat:' in coord_text and 'Lon:' in coord_text:
            lat_part = coord_text.split('Lat:')[1].split('°')[0].strip()
            lon_part = coord_text.split('Lon:')[1].split('°')[0].strip()
            data['latitude'] = lat_part
            data['longitude'] = lon_part

    return data


def extract_data_from_url(html, url=None):

    meta_data = parse_station_info_table(html)
    
    print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    print("")
    


    # Ambil field dari meta_data dengan key lengkap (yang mengandung ':')
    station_name = meta_data.get("city", "")
    city = meta_data.get("city", "")
    state = meta_data.get("state", "")
    latitude = meta_data.get("latitude", "")
    longitude = meta_data.get("longitude", "")

    # # Buat struktur data yang diinginkan
    data_save = {
        "Station Name": station_name,
        'City': city,
        'State': state,
        "Latitude": f"'{latitude}" if latitude else "",
        "Longitude": f"'{longitude}" if longitude else "",
    }
    download_image(html, station_name)


    for key, value in data_save.items():
        if value.strip():
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")

def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return


    station_urls = parse_html(html)
    for url in station_urls:
        print(f"🌐 Memproses URL: {url}")
        station_html = get_html(url)
        print(station_html)
        if station_html:
            extract_data_from_url(station_html, url)
        # break 


if __name__ == "__main__":
    main()
