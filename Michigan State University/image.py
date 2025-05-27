import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://mawn.geo.msu.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.3.943748827.1747283169; _ga_2N895J1MHX=GS2.3.s1747283170$o1$g0$t1747283170$j0$l0$h0; _ga_2N895J1MHX=GS2.2.s1747283170$o1$g0$t1747283170$j0$l0$h0; _ga=GA1.2.943748827.1747283169; _gid=GA1.2.691894314.1748313087; _ga_6B3E4XXQ03=GS2.1.s1748321134$o3$g0$t1748321134$j0$l0$h0'
}

def download_image(html, base_url="https://mawn.geo.msu.edu"):
    soup = BeautifulSoup(html, 'html.parser')

    # Temukan table yang ditentukan
    table = soup.find('table', {'width': '100%', 'height': '216', 'border': '1'})
    if not table:
        print("❌ Table dengan atribut tersebut tidak ditemukan.")
        return

    # Temukan tag <img> di dalam table tersebut
    img_tag = table.find('img')
    if not img_tag or not img_tag.get('src'):
        print("❌ Gambar tidak ditemukan di dalam table.")
        return

    # Ambil path gambar
    img_src = img_tag['src'].strip()
    img_url = urljoin(base_url, img_src)

    # Buat folder penyimpanan jika belum ada
    folder_name = "Image Station"
    os.makedirs(folder_name, exist_ok=True)

    # Ambil nama file dari URL
    filename = os.path.basename(img_src)
    save_path = os.path.join(folder_name, filename)

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

    # Definisi atribut tabel utama
    width = "100%"
    height = "100%"
    border = "0"
    bgcolor = "#ffffff"

    # Temukan tabel utama
    find_maps = soup.find('table', {'width': width, 'height': height, 'border': border, 'bgcolor': bgcolor})
    print(f"🔍 Mencari tabel dengan atribut lengkap: {find_maps is not None}")
    if not find_maps:
        print("❌ Tidak ditemukan tabel dengan atribut tersebut")
        return urls

    # Di dalam tabel utama, cari semua <td class="stntabledata">
    td_tags = find_maps.find_all('td', class_='stntabledata')
    print(f"📦 Ditemukan {len(td_tags)} elemen <td class='stntabledata'>")

    # Ambil href dan teks dari <a> di dalam <td>
    for td in td_tags:
        a_tag = td.find('a')
        if a_tag and a_tag.get('href'):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            full_url = f"https://mawn.geo.msu.edu{href}"
            urls.append(full_url)
        else:
            print("⚠️ <td> tanpa <a> atau tanpa href")

    return urls

def extract_data_from_url(html, url=None):

    # meta_data = parse_station_info_table(html)
    
    # print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    # print("")
    download_image(html)

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
