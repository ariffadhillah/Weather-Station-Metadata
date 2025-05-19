import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import json
import re


BASE_URL = "https://www.njweather.org/data/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.2.565206082.1747096139; SSESS7f721ec65e4f914322cbab428654ae15=bdujimIhqKK99__P-h7K7lDsBeSY1E38Pwmo8b7Rk60; has_js=1; _gid=GA1.2.1935681149.1747450430; STATIONID=1101; _ga_R0HNQ181MR=GS2.2.s1747452999$o6$g1$t1747453382$j0$l0$h0'
}

CSV_FILENAME = "Rutgers University.csv"

FIELDNAMES = [
        "Station Name",
        "Alt. name",
        "Station Type",
        "Network",
        "Heated Rain Gauge",
        "County",
        "City",
        "State",
        "Latitude",
        "Longitude",
        "Elevation",
        "Wind Sensor Height",
        "Activation",
        "Deactivation",

        "Apogee PYR-P Pyranometer Name",
        "Apogee PYR-P Pyranometer Observation Method",
        "Apogee PYR-P Pyranometer Min Measurement Range",
        "Apogee PYR-P Pyranometer Max Measurement Range",
        "Apogee PYR-P Pyranometer Accuracy",
        # "Apogee PYR-P Pyranometer description",
        
        "Apogee SP-110 Pyranometer Name",
        "Apogee SP-110 Pyranometer Observation Method",
        "Apogee SP-110 Pyranometer Min Measurement Range",
        "Apogee SP-110 Pyranometer Max Measurement Range",
        "Apogee SP-110 Pyranometer Accuracy",
        # "Apogee SP-110 Pyranometer description",
        
        "Kipp And Zonen CMP3 Pyranometer Name",
        "Kipp And Zonen CMP3 Pyranometer Observation Method",
        "Kipp And Zonen CMP3 Pyranometer Min Measurement Range",
        "Kipp And Zonen CMP3 Pyranometer Max Measurement Range",
        "Kipp And Zonen CMP3 Pyranometer Accuracy",
        # "Kipp And Zonen CMP3 Pyranometer description",
        
        "LiCor, Inc LI200X Pyranometer Name",
        "LiCor, Inc LI200X Pyranometer Observation Method",
        "LiCor, Inc LI200X Pyranometer Min Measurement Range",
        "LiCor, Inc LI200X Pyranometer Max Measurement Range",
        "LiCor, Inc LI200X Pyranometer Accuracy",
        # "LiCor, Inc LI200X Pyranometer description",
        
        "Met One 385 Rain Gauge Name",
        "Met One 385 Rain Gauge Observation Method",
        "Met One 385 Rain Gauge Min Measurement Range",
        "Met One 385 Rain Gauge Max Measurement Range",
        "Met One 385 Rain Gauge Accuracy",
        # "Met One 385 Rain Gauge description",
        
        "R.M. Young Company 05103 Wind Monitor Name",
        "R.M. Young Company 05103 Wind Monitor Observation Method",
        "R.M. Young Company 05103 Wind Monitor Min Measurement Range",
        "R.M. Young Company 05103 Wind Monitor Max Measurement Range",
        "R.M. Young Company 05103 Wind Monitor Accuracy",
        # "R.M. Young Company 05103 Wind Monitor description",
        
        "R.M. Young Company 05106 Wind Monitor Name",
        "R.M. Young Company 05106 Wind Monitor Observation Method",
        "R.M. Young Company 05106 Wind Monitor Min Measurement Range",
        "R.M. Young Company 05106 Wind Monitor Max Measurement Range",
        "R.M. Young Company 05106 Wind Monitor Accuracy",
        # "R.M. Young Company 05106 Wind Monitor description",
        
        "R.M. Young Company 03001 Wind Monitor Name",
        "R.M. Young Company 03001 Wind Monitor Observation Method",
        "R.M. Young Company 03001 Wind Monitor Min Measurement Range",
        "R.M. Young Company 03001 Wind Monitor Max Measurement Range",
        "R.M. Young Company 03001 Wind Monitor Accuracy",
        # "R.M. Young Company 03001 Wind Monitor description",
        
        "R.M. Young Company 03002 Wind Monitor Name",
        "R.M. Young Company 03002 Wind Monitor Observation Method",
        "R.M. Young Company 03002 Wind Monitor Min Measurement Range",
        "R.M. Young Company 03002 Wind Monitor Max Measurement Range",
        "R.M. Young Company 03002 Wind Monitor Accuracy",
        # "R.M. Young Company 03002 Wind Monitor description",
        
        "Texas Electronics TR-525I Rain Gauge Name",
        "Texas Electronics TR-525I Rain Gauge Observation Method",
        "Texas Electronics TR-525I Rain Gauge Min Measurement Range",
        "Texas Electronics TR-525I Rain Gauge Max Measurement Range",
        "Texas Electronics TR-525I Rain Gauge Accuracy",
        # "Texas Electronics TR-525I Rain Gauge description",
        
        "Texas Electronics TR-525I-HT Rain Gauge Name",
        "Texas Electronics TR-525I-HT Rain Gauge Observation Method",
        "Texas Electronics TR-525I-HT Rain Gauge Min Measurement Range",
        "Texas Electronics TR-525I-HT Rain Gauge Max Measurement Range",
        "Texas Electronics TR-525I-HT Rain Gauge Accuracy",
        # "Texas Electronics TR-525I-HT Rain Gauge description",
        
        "Texas Electronics TR-525USW Rain Gauge Name",
        "Texas Electronics TR-525USW Rain Gauge Observation Method",
        "Texas Electronics TR-525USW Rain Gauge Min Measurement Range",
        "Texas Electronics TR-525USW Rain Gauge Max Measurement Range",
        "Texas Electronics TR-525USW Rain Gauge Accuracy",
        # "Texas Electronics TR-525USW Rain Gauge description",
         
        "Vaisala HMP45C Thermometer & Hygrometer Name",
        "Vaisala HMP45C Thermometer & Hygrometer Observation Method",
        "Vaisala HMP45C Thermometer & Hygrometer Min Measurement Range",
        "Vaisala HMP45C Thermometer & Hygrometer Max Measurement Range",
        "Vaisala HMP45C Thermometer & Hygrometer Accuracy",
        # "Vaisala HMP45C Thermometer & Hygrometer description",
        
        "Vaisala HMP35C Thermometer & Hygrometer Name",
        "Vaisala HMP35C Thermometer & Hygrometer Observation Method",
        "Vaisala HMP35C Thermometer & Hygrometer Min Measurement Range",
        "Vaisala HMP35C Thermometer & Hygrometer Max Measurement Range",
        "Vaisala HMP35C Thermometer & Hygrometer Accuracy",
        # "Vaisala HMP35C Thermometer & Hygrometer description",
        
        "Vaisala PTB101B Barometer Name",
        "Vaisala PTB101B Barometer Observation Method",
        "Vaisala PTB101B Barometer Min Measurement Range",
        "Vaisala PTB101B Barometer Max Measurement Range",
        "Vaisala PTB101B Barometer Accuracy",
        # "Vaisala PTB101B Barometer description",
        
        "Campbell Scientific 107 Soil Thermometer Name",
        "Campbell Scientific 107 Soil Thermometer Observation Method",
        "Campbell Scientific 107 Soil Thermometer Min Measurement Range",
        "Campbell Scientific 107 Soil Thermometer Max Measurement Range",
        "Campbell Scientific 107 Soil Thermometer Accuracy",
        # "Campbell Scientific 107 Soil Thermometer description",
        
        "Campbell Scientific CS616 Soil Hygrometer Name",
        "Campbell Scientific CS616 Soil Hygrometer Observation Method",
        "Campbell Scientific CS616 Soil Hygrometer Min Measurement Range",
        "Campbell Scientific CS616 Soil Hygrometer Max Measurement Range",
        "Campbell Scientific CS616 Soil Hygrometer Accuracy",
        # "Campbell Scientific CS616 Soil Hygrometer description",
        
        "Peet Brothers 2000 Ultimeter Name",
        "Peet Brothers 2000 Ultimeter Observation Method",
        "Peet Brothers 2000 Ultimeter Min Measurement Range",
        "Peet Brothers 2000 Ultimeter Max Measurement Range",
        "Peet Brothers 2000 Ultimeter Accuracy",
        # "Peet Brothers 2000 Ultimeter description",
        
        "Peet Brothers 2100 Ultimeter Name",
        "Peet Brothers 2100 Ultimeter Observation Method",
        "Peet Brothers 2100 Ultimeter Min Measurement Range",
        "Peet Brothers 2100 Ultimeter Max Measurement Range",
        "Peet Brothers 2100 Ultimeter Accuracy",
        # "Peet Brothers 2100 Ultimeter description",
        
        "Peet Brothers UNKNOWN Ultimeter Name",
        "Peet Brothers UNKNOWN Ultimeter Observation Method",
        "Peet Brothers UNKNOWN Ultimeter Min Measurement Range",
        "Peet Brothers UNKNOWN Ultimeter Max Measurement Range",
        "Peet Brothers UNKNOWN Ultimeter Accuracy",
        # "Peet Brothers UNKNOWN Ultimeter description",
        
        
        "Campbell Scientific SR50A Snow Depth Sensor Name",
        "Campbell Scientific SR50A Snow Depth Sensor Observation Method",
        "Campbell Scientific SR50A Snow Depth Sensor Min Measurement Range",
        "Campbell Scientific SR50A Snow Depth Sensor Max Measurement Range",
        "Campbell Scientific SR50A Snow Depth Sensor Accuracy",
        # "Campbell Scientific SR50A Snow Depth Sensor description",
        
        "Campbell Scientific SR50 Snow Depth Sensor Name",
        "Campbell Scientific SR50 Snow Depth Sensor Observation Method",
        "Campbell Scientific SR50 Snow Depth Sensor Min Measurement Range",
        "Campbell Scientific SR50 Snow Depth Sensor Max Measurement Range",
        "Campbell Scientific SR50 Snow Depth Sensor Accuracy",
        # "Campbell Scientific SR50 Snow Depth Sensor description",
        
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Name",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Observation Method",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Min Measurement Range",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Max Measurement Range",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Accuracy",
        # "Peet Brothers WSF-10072 Thermometer & Hygrometer description",
        
        "Peet Brothers OTS Thermometer Name",
        "Peet Brothers OTS Thermometer Observation Method",
        "Peet Brothers OTS Thermometer Min Measurement Range",
        "Peet Brothers OTS Thermometer Max Measurement Range",
        "Peet Brothers OTS Thermometer Accuracy",
        # "Peet Brothers OTS Thermometer description",

        "Peet Brothers AWVS Wind Monitor Name",
        "Peet Brothers AWVS Wind Monitor Observation Method",
        "Peet Brothers AWVS Wind Monitor Min Measurement Range",
        "Peet Brothers AWVS Wind Monitor Max Measurement Range",
        "Peet Brothers AWVS Wind Monitor Accuracy",
        # "Peet Brothers AWVS Wind Monitor description",

        "Peet Brothers AWVP Wind Monitor Name",
        "Peet Brothers AWVP Wind Monitor Observation Method",
        "Peet Brothers AWVP Wind Monitor Min Measurement Range",
        "Peet Brothers AWVP Wind Monitor Max Measurement Range",
        "Peet Brothers AWVP Wind Monitor Accuracy",
        # "Peet Brothers AWVP Wind Monitor description",
        
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Name",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Observation Method",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Min Measurement Range",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Max Measurement Range",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Accuracy",
        # "Campbell Scientific CS650 Soil Hygrometer & Thermometer description",
        
        
        "Rotronic HC2S3 Thermometer & Hygrometer Name",
        "Rotronic HC2S3 Thermometer & Hygrometer Observation Method",
        "Rotronic HC2S3 Thermometer & Hygrometer Min Measurement Range",
        "Rotronic HC2S3 Thermometer & Hygrometer Max Measurement Range",
        "Rotronic HC2S3 Thermometer & Hygrometer Accuracy",
        # "Rotronic HC2S3 Thermometer & Hygrometer description",
        
        "Vaisala PTB110 Barometer Name",
        "Vaisala PTB110 Barometer Observation Method",
        "Vaisala PTB110 Barometer Min Measurement Range",
        "Vaisala PTB110 Barometer Max Measurement Range",
        "Vaisala PTB110 Barometer Accuracy",
        # "Vaisala PTB110 Barometer description",
        
        "Campbell Scientific EE181 Thermometer & Hygrometer Name",
        "Campbell Scientific EE181 Thermometer & Hygrometer Observation Method",
        "Campbell Scientific EE181 Thermometer & Hygrometer Min Measurement Range",
        "Campbell Scientific EE181 Thermometer & Hygrometer Max Measurement Range",
        "Campbell Scientific EE181 Thermometer & Hygrometer Accuracy",
        # "Campbell Scientific EE181 Thermometer & Hygrometer description",
        
        "Setra Model 278 Barometer Name",
        "Setra Model 278 Barometer Observation Method",
        "Setra Model 278 Barometer Min Measurement Range",
        "Setra Model 278 Barometer Max Measurement Range",
        "Setra Model 278 Barometer Accuracy",
        # "Setra Model 278 Barometer description",       
        
        "Campbell Scientific 034B-L Wind Monitor Name",
        "Campbell Scientific 034B-L Wind Monitor Observation Method",
        "Campbell Scientific 034B-L Wind Monitor Min Measurement Range",
        "Campbell Scientific 034B-L Wind Monitor Max Measurement Range",
        "Campbell Scientific 034B-L Wind Monitor Accuracy",
        # "Campbell Scientific 034B-L Wind Monitor description",
        
        "Campbell Scientific BaroVue 10 Barometer Name",
        "Campbell Scientific BaroVue 10 Barometer Observation Method",
        "Campbell Scientific BaroVue 10 Barometer Min Measurement Range",
        "Campbell Scientific BaroVue 10 Barometer Max Measurement Range",
        "Campbell Scientific BaroVue 10 Barometer Accuracy",
        # "Campbell Scientific BaroVue 10 Barometer description",
        
        
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Name",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Observation Method",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Min Measurement Range",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Max Measurement Range",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Accuracy",
        # "Campbell Scientific SnowVue 10 Snow Depth Sensor description",     
        
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Name",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Observation Method",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Min Measurement Range",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Max Measurement Range",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Accuracy",
        # "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor description",  
        
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Name",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Observation Method",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Min Measurement Range",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Max Measurement Range",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Accuracy",
        # "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor description", 
        
        "R.M. Young Company 04101 Wind Monitor Name",
        "R.M. Young Company 04101 Wind Monitor Observation Method",
        "R.M. Young Company 04101 Wind Monitor Min Measurement Range",
        "R.M. Young Company 04101 Wind Monitor Max Measurement Range",
        "R.M. Young Company 04101 Wind Monitor Accuracy",
        # "R.M. Young Company 04101 Wind Monitor description"

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

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    urls = []

    table = soup.find('table')
    rows = table.find_all('tr')[1:]

    for row in rows:
        row_id = row.get('id')
        if row_id:
            url = f"https://www.njweather.org/station/{row_id}"
            urls.append(url)
            print(url)
        else:
            print("Baris tanpa ID")

    return urls

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

# def download_images(soup, station_name):
#     """Unduh semua gambar dari slider dengan nama berdasarkan title"""
#     slider = soup.find("div", id="slider")
#     if not slider:
#         print("⚠️ Tidak ada slider ditemukan.")
#         return

#     img_tags = slider.find_all("img")
#     os.makedirs("Rutgers University Image", exist_ok=True)

#     for img in img_tags:
#         src = img.get("src")
#         title = img.get("title")

#         if not src or not title:
#             continue  # Skip gambar tanpa judul

#         ext = os.path.splitext(src)[1]
#         safe_title = sanitize_filename(title)
#         filename = f"{station_name} - {safe_title}{ext}"
#         filepath = os.path.join("Rutgers University Image", filename)

#         try:
#             response = requests.get(src)
#             response.raise_for_status()
#             with open(filepath, "wb") as f:
#                 f.write(response.content)
#             print(f"✅ Disimpan: {filename}")
#         except Exception as e:
#             print(f"❌ Gagal mengunduh {src}: {e}")


def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='stationInfo')
    data = {}

    if table:
        rows = table.find_all('tr')
        for row in rows:
            key_cell = row.find('td', class_='key')
            value_cell = row.find('td', class_='value')
            if key_cell and value_cell:
                key = key_cell.get_text(strip=True)
                value = value_cell.get_text(strip=True)
                data[key] = value

    return data


def extract_sensor_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    sensor_list = soup.find('ul', id='stationSensors')

    if not sensor_list:
        print("⚠️ Tidak menemukan <ul id='stationSensors'>")
        return []

    links = []
    for li in sensor_list.find_all('li'):
        a_tag = li.find('a')
        if a_tag and a_tag.get('href'):
            link_url = urljoin("https://www.njweather.org/", a_tag['href'])  # full URL
            link_text = a_tag.text.strip()
            links.append((link_text, link_url))
            print(f"🔗 {link_text}: {link_url}")
    return links


# def process_sensor_links(sensor_links):
#     for name, link in sensor_links:
#         try:
#             response = requests.get(link, timeout=10)
#             print(f"\n✅ Membuka sensor: {name}")
#             print(f"🌐 URL: {link}")

#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text, 'html.parser')

#                 # ✅ Contoh ambil isi sensor description
#                 description = soup.find("h3", class_="sensorname")
#                 if description:
#                     print(f"📄 Deskripsi: {description.text.strip()}")
#                 else:
#                     print("ℹ️ Tidak menemukan deskripsi.")

#                 # Tambahkan logika parsing lainnya di sini jika diperlukan

#             else:
#                 print(f"⚠️ Halaman tidak berhasil dimuat (status {response.status_code})")

#         except Exception as e:
#             print(f"❌ Gagal membuka {link}: {e}")


# def extract_sensor_detail_by_anchor(html, anchor_id):
#     soup = BeautifulSoup(html, 'html.parser')
#     sensor_divs = soup.find_all("div", class_="sensor")

#     for sensor_div in sensor_divs:
#         anchor = sensor_div.find("a", attrs={"name": anchor_id})
#         if anchor:
#             sensor_data = {}

#             name = sensor_div.find("h3", class_="sensorname")
#             if name:
#                 sensor_data["name"] = name.text.strip()

#             img_tag = sensor_div.find("div", class_="sensorImage")
#             if img_tag and img_tag.find("img"):
#                 sensor_data["image"] = img_tag.find("img")["src"]

#             desc_tag = sensor_div.find("div", class_="sensorDescription")
#             if desc_tag:
#                 sensor_data["description"] = desc_tag.text.strip()

#             table = sensor_div.find("table", class_="sensorInfo")
#             if table:
#                 rows = table.find_all("tr")
#                 for row in rows:
#                     cols = row.find_all("td")
#                     if len(cols) == 2:
#                         key = cols[0].text.strip()
#                         value = cols[1].decode_contents().strip()  # ambil HTML dalamnya
#                         value = re.sub(r'<br\s*/?>', '\n', value)  # ganti <br> dengan newline
#                         value = BeautifulSoup(value, 'html.parser').text  # hapus HTML tag
#                         value = value.replace('\r', '').replace('\xa0', ' ')  # bersihkan karakter aneh
#                         sensor_data[key] = value
#                     elif len(cols) == 1:
#                         sensor_data["extra"] = cols[0].text.strip()



#             return sensor_data
        

#     return None


def extract_sensor_detail_by_anchor(html, anchor_id):
    soup = BeautifulSoup(html, 'html.parser')
    sensor_divs = soup.find_all("div", class_="sensor")

    for sensor_div in sensor_divs:
        anchor = sensor_div.find("a", attrs={"name": anchor_id})
        if anchor:
            sensor_data = {}
            name_tag = sensor_div.find("h3", class_="sensorname")
            if name_tag:
                name = name_tag.text.strip()
                sensor_data["name"] = name  # <- tambahkan name di dalam data
            else:
                name = f"Sensor_{anchor_id}"
                sensor_data["name"] = name

            img_tag = sensor_div.find("div", class_="sensorImage")
            if img_tag and img_tag.find("img"):
                sensor_data["image"] = img_tag.find("img")["src"]

            desc_tag = sensor_div.find("div", class_="sensorDescription")
            if desc_tag:
                sensor_data["description"] = desc_tag.text.strip()

            table = sensor_div.find("table", class_="sensorInfo")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) == 2:
                        key = cols[0].text.strip()
                        value = cols[1].decode_contents().strip()
                        value = re.sub(r'<br\s*/?>', '\n', value)
                        value = BeautifulSoup(value, 'html.parser').text
                        value = value.replace('\r', '').replace('\xa0', ' ')
                        sensor_data[key] = value
                    elif len(cols) == 1:
                        sensor_data["extra"] = cols[0].text.strip()

            return {name: sensor_data}
    return None




# def process_sensor_links(sensor_links):
#     for name, link in sensor_links:
#         try:
#             print(f"\n✅ Membuka sensor: {name}")
#             print(f"🌐 URL: {link}")

#             anchor_id = link.split('#')[-1]
#             base_url = link.split('#')[0]

#             response = requests.get(base_url, timeout=10)
#             if response.status_code == 200:
#                 sensor_info = extract_sensor_detail_by_anchor(response.text, anchor_id)
#                 if sensor_info:
#                     print(json.dumps(sensor_info, indent=4, ensure_ascii=False))
#                 else:
#                     print("ℹ️ Tidak ditemukan informasi sensor dari anchor.")
#             else:
#                 print(f"⚠️ Halaman tidak berhasil dimuat (status {response.status_code})")

#         except Exception as e:
#             print(f"❌ Gagal membuka {link}: {e}")



def process_sensor_links(sensor_links):
    all_sensor_data = {}
    for name, link in sensor_links:
        try:
            print(f"\n✅ Membuka sensor: {name}")
            print(f"🌐 URL: {link}")

            anchor_id = link.split('#')[-1]
            base_url = link.split('#')[0]

            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                sensor_info = extract_sensor_detail_by_anchor(response.text, anchor_id)
                if sensor_info:
                    all_sensor_data.update(sensor_info)
                    print(f"✅ Sensor berhasil diproses: {list(sensor_info.keys())[0]}")
                else:
                    print("ℹ️ Tidak ditemukan informasi sensor dari anchor.")
            else:
                print(f"⚠️ Halaman tidak berhasil dimuat (status {response.status_code})")

        except Exception as e:
            print(f"❌ Gagal membuka {link}: {e}")
    return all_sensor_data





# def extract_data_from_url(html, url=None):
#     soup = BeautifulSoup(html, 'html.parser')
#     station_name = extract_station_name(soup)

#     print(f"✅ Memproses: {station_name}")
#     if url:
#         print(f"🌐 URL: {url}")

#     # download_images(soup, station_name)

#     # Ambil metadata dari tabel
#     meta_data = parse_station_info_table(html)
#     meta_data_json = json.dumps(meta_data, indent=4, ensure_ascii=False)
#     print(meta_data_json)
#     print("")

#     # Ambil dan proses link sensor
#     sensor_links = extract_sensor_links(html)
#     process_sensor_links(sensor_links)
#     # sensor = json.dumps(process_sensor_links)
#     # print(sensor)

#     data = {
#         "Texas Electronics TR-525I Rain Gauge": process_sensor_links.get("name")
#     }
#     print(data)
    


def extract_data_from_url(html, url=None):
    soup = BeautifulSoup(html, 'html.parser')
    station_name = extract_station_name(soup)

    print(f"✅ Memproses: {station_name}")
    if url:
        print(f"🌐 URL: {url}")
    
    # download_images(soup, station_name)

    meta_data = parse_station_info_table(html)
    
    print(json.dumps(meta_data, indent=4, ensure_ascii=False))
    print("")

    # Proses sensor dan tampilkan semua sensor dalam bentuk JSON
    sensor_links = extract_sensor_links(html)
    sensor_data = process_sensor_links(sensor_links)

    # # Cetak semua sensor
    # # print("\n📦 Data Sensor (JSON):")
    print(json.dumps(sensor_data, indent=4, ensure_ascii=False))

    
    sensor_Apogee_PYR_P_Pyranometer = sensor_data.get("Apogee PYR-P Pyranometer")
    sensor_Apogee_SP_110_Pyranometer = sensor_data.get("Apogee SP-110 Pyranometer")    
    sensor_Kipp_And_Zonen_CMP3_Pyranometer = sensor_data.get("Kipp And Zonen CMP3 Pyranometer")    
    sensor_LiCor_Inc_LI200X_Pyranometer = sensor_data.get("LiCor, Inc LI200X Pyranometer")
    sensor_Met_One_385_Rain_Gauge = sensor_data.get("Met One 385 Rain Gauge")
    sensor_R_M_Young_Company_05103_Wind_Monitor = sensor_data.get("R.M. Young Company 05103 Wind Monitor")
    sensor_R_M_Young_Company_05106_Wind_Monitor = sensor_data.get("R.M. Young Company 05106 Wind Monitor")
    sensor_R_M_Young_Company_03001_Wind_Monitor = sensor_data.get("R.M. Young Company 03001 Wind Monitor")
    sensor_R_M_Young_Company_03002_Wind_Monitor = sensor_data.get("R.M. Young Company 03002 Wind Monitor")
    sensor_Texas_Electronics_TR_525I_Rain_Gauge = sensor_data.get("Texas Electronics TR-525I Rain Gauge")
    sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge = sensor_data.get("Texas Electronics TR-525I-HT Rain Gauge")
    sensor_Texas_Electronics_TR_525USW_Rain_Gauge = sensor_data.get("Texas Electronics TR-525USW Rain Gauge")
    sensor_Vaisala_HMP35C_Thermometer_Hygrometer = sensor_data.get("Vaisala HMP35C Thermometer & Hygrometer")
    sensor_Vaisala_HMP45C_Thermometer_Hygrometer = sensor_data.get("Vaisala HMP45C Thermometer & Hygrometer")
    sensor_Vaisala_PTB101B_Barometer = sensor_data.get("Vaisala PTB101B Barometer")
    sensor_Campbell_Scientific_107_Soil_Thermometer = sensor_data.get("Campbell Scientific 107 Soil Thermometer")
    sensor_Campbell_Scientific_CS616_Soil_Hygrometer = sensor_data.get("Campbell Scientific CS616 Soil Hygrometer")
    sensor_Peet_Brothers_2000_Ultimeter = sensor_data.get("Peet Brothers 2000 Ultimeter")
    sensor_Peet_Brothers_2100_Ultimeter = sensor_data.get("Peet Brothers 2100 Ultimeter")
    sensor_Peet_Brothers_UNKNOWN_Ultimeter = sensor_data.get("Peet Brothers UNKNOWN Ultimeter")
    sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor = sensor_data.get("Campbell Scientific SR50A Snow Depth Sensor")
    sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor = sensor_data.get("Campbell Scientific SR50 Snow Depth Sensor")
    sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer = sensor_data.get("Peet Brothers WSF-10072 Thermometer & Hygrometer")
    sensor_Peet_Brothers_OTS_Thermometer = sensor_data.get("Peet Brothers OTS Thermometer")
    sensor_Peet_Brothers_AWVS_Wind_Monitor = sensor_data.get("Peet Brothers AWVS Wind Monitor")
    sensor_Peet_Brothers_AWVP_Wind_Monitor = sensor_data.get("Peet Brothers AWVP Wind Monitor")
    sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer = sensor_data.get("Campbell Scientific CS650 Soil Hygrometer & Thermometer")
    sensor_Rotronic_HC2S3_Thermometer_Hygrometer = sensor_data.get("Rotronic HC2S3 Thermometer & Hygrometer")
    sensor_Vaisala_PTB110_Barometer = sensor_data.get("Vaisala PTB110 Barometer")
    sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer = sensor_data.get("Campbell Scientific EE181 Thermometer & Hygrometer")
    sensor_Setra_Model_278_Barometer = sensor_data.get("Setra Model 278 Barometer")
    sensor_Campbell_Scientific_034B_L_Wind_Monitor = sensor_data.get("Campbell Scientific 034B-L Wind Monitor")
    sensor_Campbell_Scientific_BaroVue_10_Barometer = sensor_data.get("Campbell Scientific BaroVue 10 Barometer")
    sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor = sensor_data.get("Campbell Scientific SnowVue 10 Snow Depth Sensor")
    sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor = sensor_data.get("Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor")
    sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor = sensor_data.get("Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor")
    sensor_R_M_Young_Company_04101_Wind_Monitor = sensor_data.get("R.M. Young Company 04101 Wind Monitor")


    data_save = {
        "Station Name" : station_name,
        "Alt. name" : meta_data.get("Alt. name") if meta_data else " ",
        "Station Type" : meta_data.get("Type") if meta_data else " ",
        "Network": meta_data.get("Network") if meta_data else " ",
        "Heated Rain Gauge": meta_data.get("Heated Rain Gauge") if meta_data else " ",
        "County": meta_data.get("County") if meta_data else " ",
        "City": meta_data.get("City") if meta_data else " ",
        "State": meta_data.get("State") if meta_data else " ",
        "Latitude": f"'{meta_data.get('Latitude')}" if meta_data else " ",
        "Longitude": f"'{meta_data.get('Longitude')}" if meta_data else " ",
        "Elevation": meta_data.get("Elevation") if meta_data else " ",
        "Wind Sensor Height" : meta_data.get("Wind Sensor Height") if meta_data else " ",
        "Activation" : f"'{meta_data.get('Activation')}" if meta_data else "  ", 
        "Deactivation" : f"'{meta_data.get('Deactivation')}" if meta_data else "  ",

        "Apogee PYR-P Pyranometer Name" : sensor_Apogee_PYR_P_Pyranometer.get("name") if sensor_Apogee_PYR_P_Pyranometer else "",
        "Apogee PYR-P Pyranometer Observation Method": sensor_Apogee_PYR_P_Pyranometer.get("Observation Method") if sensor_Apogee_PYR_P_Pyranometer else "",
        "Apogee PYR-P Pyranometer Min Measurement Range": f"'{sensor_Apogee_PYR_P_Pyranometer.get('Min Measurement Range')}" if sensor_Apogee_PYR_P_Pyranometer else "",
        "Apogee PYR-P Pyranometer Max Measurement Range": f"'{sensor_Apogee_PYR_P_Pyranometer.get('Max Measurement Range')}" if sensor_Apogee_PYR_P_Pyranometer else "",
        "Apogee PYR-P Pyranometer Accuracy": f"'{sensor_Apogee_PYR_P_Pyranometer.get('Accuracy')}" if sensor_Apogee_PYR_P_Pyranometer else "",
        # "Apogee PYR-P Pyranometer description": f"'{sensor_Apogee_PYR_P_Pyranometer.get('description')}" if sensor_Apogee_PYR_P_Pyranometer else "",
        
        "Apogee SP-110 Pyranometer Name" : sensor_Apogee_SP_110_Pyranometer.get("name") if sensor_Apogee_SP_110_Pyranometer else "",
        "Apogee SP-110 Pyranometer Observation Method": sensor_Apogee_SP_110_Pyranometer.get("Observation Method") if sensor_Apogee_SP_110_Pyranometer else "",
        "Apogee SP-110 Pyranometer Min Measurement Range": f"'{sensor_Apogee_SP_110_Pyranometer.get('Min Measurement Range')}" if sensor_Apogee_SP_110_Pyranometer else "",
        "Apogee SP-110 Pyranometer Max Measurement Range": f"'{sensor_Apogee_SP_110_Pyranometer.get('Max Measurement Range')}" if sensor_Apogee_SP_110_Pyranometer else "",
        "Apogee SP-110 Pyranometer Accuracy": f"'{sensor_Apogee_SP_110_Pyranometer.get('Accuracy')}" if sensor_Apogee_SP_110_Pyranometer else "",
        # "Apogee SP-110 Pyranometer description": f"'{sensor_Apogee_SP_110_Pyranometer.get('description')}" if sensor_Apogee_SP_110_Pyranometer else "",
        
        "Kipp And Zonen CMP3 Pyranometer Name" : sensor_Kipp_And_Zonen_CMP3_Pyranometer.get("name") if sensor_Kipp_And_Zonen_CMP3_Pyranometer else "",
        "Kipp And Zonen CMP3 Pyranometer Observation Method": sensor_Kipp_And_Zonen_CMP3_Pyranometer.get("Observation Method") if sensor_Kipp_And_Zonen_CMP3_Pyranometer else "",
        "Kipp And Zonen CMP3 Pyranometer Min Measurement Range": f"'{sensor_Kipp_And_Zonen_CMP3_Pyranometer.get('Min Measurement Range')}" if sensor_Kipp_And_Zonen_CMP3_Pyranometer else "",
        "Kipp And Zonen CMP3 Pyranometer Max Measurement Range": f"'{sensor_Kipp_And_Zonen_CMP3_Pyranometer.get('Max Measurement Range')}" if sensor_Kipp_And_Zonen_CMP3_Pyranometer else "",
        "Kipp And Zonen CMP3 Pyranometer Accuracy": f"'{sensor_Kipp_And_Zonen_CMP3_Pyranometer.get('Accuracy')}" if sensor_Kipp_And_Zonen_CMP3_Pyranometer else "",
        # "Kipp And Zonen CMP3 Pyranometer description": f"'{sensor_Kipp_And_Zonen_CMP3_Pyranometer.get('description')}" if sensor_Kipp_And_Zonen_CMP3_Pyranometer else "",
        
        "LiCor, Inc LI200X Pyranometer Name" : sensor_LiCor_Inc_LI200X_Pyranometer.get("name") if sensor_LiCor_Inc_LI200X_Pyranometer else "",
        "LiCor, Inc LI200X Pyranometer Observation Method": sensor_LiCor_Inc_LI200X_Pyranometer.get("Observation Method") if sensor_LiCor_Inc_LI200X_Pyranometer else "",
        "LiCor, Inc LI200X Pyranometer Min Measurement Range": f"'{sensor_LiCor_Inc_LI200X_Pyranometer.get('Min Measurement Range')}" if sensor_LiCor_Inc_LI200X_Pyranometer else "",
        "LiCor, Inc LI200X Pyranometer Max Measurement Range": f"'{sensor_LiCor_Inc_LI200X_Pyranometer.get('Max Measurement Range')}" if sensor_LiCor_Inc_LI200X_Pyranometer else "",
        "LiCor, Inc LI200X Pyranometer Accuracy": f"'{sensor_LiCor_Inc_LI200X_Pyranometer.get('Accuracy')}" if sensor_LiCor_Inc_LI200X_Pyranometer else "",
        # "LiCor, Inc LI200X Pyranometer description": f"'{sensor_LiCor_Inc_LI200X_Pyranometer.get('description')}" if sensor_LiCor_Inc_LI200X_Pyranometer else "",
        
        "Met One 385 Rain Gauge Name" : sensor_Met_One_385_Rain_Gauge.get("name") if sensor_Met_One_385_Rain_Gauge else "",
        "Met One 385 Rain Gauge Observation Method": sensor_Met_One_385_Rain_Gauge.get("Observation Method") if sensor_Met_One_385_Rain_Gauge else "",
        "Met One 385 Rain Gauge Min Measurement Range": f"'{sensor_Met_One_385_Rain_Gauge.get('Min Measurement Range')}" if sensor_Met_One_385_Rain_Gauge else "",
        "Met One 385 Rain Gauge Max Measurement Range": f"'{sensor_Met_One_385_Rain_Gauge.get('Max Measurement Range')}" if sensor_Met_One_385_Rain_Gauge else "",
        "Met One 385 Rain Gauge Accuracy": f"'{sensor_Met_One_385_Rain_Gauge.get('Accuracy')}" if sensor_Met_One_385_Rain_Gauge else "",
        # "Met One 385 Rain Gauge description": f"'{sensor_Met_One_385_Rain_Gauge.get('description')}" if sensor_Met_One_385_Rain_Gauge else "",
        
        "R.M. Young Company 05103 Wind Monitor Name" : sensor_R_M_Young_Company_05103_Wind_Monitor.get("name") if sensor_R_M_Young_Company_05103_Wind_Monitor else "",
        "R.M. Young Company 05103 Wind Monitor Observation Method": sensor_R_M_Young_Company_05103_Wind_Monitor.get("Observation Method") if sensor_R_M_Young_Company_05103_Wind_Monitor else "",
        "R.M. Young Company 05103 Wind Monitor Min Measurement Range": f"'{sensor_R_M_Young_Company_05103_Wind_Monitor.get('Min Measurement Range')}" if sensor_R_M_Young_Company_05103_Wind_Monitor else "",
        "R.M. Young Company 05103 Wind Monitor Max Measurement Range": f"'{sensor_R_M_Young_Company_05103_Wind_Monitor.get('Max Measurement Range')}" if sensor_R_M_Young_Company_05103_Wind_Monitor else "",
        "R.M. Young Company 05103 Wind Monitor Accuracy": f"'{sensor_R_M_Young_Company_05103_Wind_Monitor.get('Accuracy')}" if sensor_R_M_Young_Company_05103_Wind_Monitor else "",
        # "R.M. Young Company 05103 Wind Monitor description": f"'{sensor_R_M_Young_Company_05103_Wind_Monitor.get('description')}" if sensor_R_M_Young_Company_05103_Wind_Monitor else "",
        
        "R.M. Young Company 05106 Wind Monitor Name" : sensor_R_M_Young_Company_05106_Wind_Monitor.get("name") if sensor_R_M_Young_Company_05106_Wind_Monitor else "",
        "R.M. Young Company 05106 Wind Monitor Observation Method": sensor_R_M_Young_Company_05106_Wind_Monitor.get("Observation Method") if sensor_R_M_Young_Company_05106_Wind_Monitor else "",
        "R.M. Young Company 05106 Wind Monitor Min Measurement Range": f"'{sensor_R_M_Young_Company_05106_Wind_Monitor.get('Min Measurement Range')}" if sensor_R_M_Young_Company_05106_Wind_Monitor else "",
        "R.M. Young Company 05106 Wind Monitor Max Measurement Range": f"'{sensor_R_M_Young_Company_05106_Wind_Monitor.get('Max Measurement Range')}" if sensor_R_M_Young_Company_05106_Wind_Monitor else "",
        "R.M. Young Company 05106 Wind Monitor Accuracy": f"'{sensor_R_M_Young_Company_05106_Wind_Monitor.get('Accuracy')}" if sensor_R_M_Young_Company_05106_Wind_Monitor else "",
        # "R.M. Young Company 05106 Wind Monitor description": f"'{sensor_R_M_Young_Company_05106_Wind_Monitor.get('description')}" if sensor_R_M_Young_Company_05106_Wind_Monitor else "",
        
        "R.M. Young Company 03001 Wind Monitor Name" : sensor_R_M_Young_Company_03001_Wind_Monitor.get("name") if sensor_R_M_Young_Company_03001_Wind_Monitor else "",
        "R.M. Young Company 03001 Wind Monitor Observation Method": sensor_R_M_Young_Company_03001_Wind_Monitor.get("Observation Method") if sensor_R_M_Young_Company_03001_Wind_Monitor else "",
        "R.M. Young Company 03001 Wind Monitor Min Measurement Range": f"'{sensor_R_M_Young_Company_03001_Wind_Monitor.get('Min Measurement Range')}" if sensor_R_M_Young_Company_03001_Wind_Monitor else "",
        "R.M. Young Company 03001 Wind Monitor Max Measurement Range": f"'{sensor_R_M_Young_Company_03001_Wind_Monitor.get('Max Measurement Range')}" if sensor_R_M_Young_Company_03001_Wind_Monitor else "",
        "R.M. Young Company 03001 Wind Monitor Accuracy": f"'{sensor_R_M_Young_Company_03001_Wind_Monitor.get('Accuracy')}" if sensor_R_M_Young_Company_03001_Wind_Monitor else "",
        # "R.M. Young Company 03001 Wind Monitor description": f"'{sensor_R_M_Young_Company_03001_Wind_Monitor.get('description')}" if sensor_R_M_Young_Company_03001_Wind_Monitor else "",
        
        "R.M. Young Company 03002 Wind Monitor Name" : sensor_R_M_Young_Company_03002_Wind_Monitor.get("name") if sensor_R_M_Young_Company_03002_Wind_Monitor else "",
        "R.M. Young Company 03002 Wind Monitor Observation Method": sensor_R_M_Young_Company_03002_Wind_Monitor.get("Observation Method") if sensor_R_M_Young_Company_03002_Wind_Monitor else "",
        "R.M. Young Company 03002 Wind Monitor Min Measurement Range": f"'{sensor_R_M_Young_Company_03002_Wind_Monitor.get('Min Measurement Range')}" if sensor_R_M_Young_Company_03002_Wind_Monitor else "",
        "R.M. Young Company 03002 Wind Monitor Max Measurement Range": f"'{sensor_R_M_Young_Company_03002_Wind_Monitor.get('Max Measurement Range')}" if sensor_R_M_Young_Company_03002_Wind_Monitor else "",
        "R.M. Young Company 03002 Wind Monitor Accuracy": f"'{sensor_R_M_Young_Company_03002_Wind_Monitor.get('Accuracy')}" if sensor_R_M_Young_Company_03002_Wind_Monitor else "",
        # "R.M. Young Company 03002 Wind Monitor description": f"'{sensor_R_M_Young_Company_03002_Wind_Monitor.get('description')}" if sensor_R_M_Young_Company_03002_Wind_Monitor else "",
        
        "Texas Electronics TR-525I Rain Gauge Name" : sensor_Texas_Electronics_TR_525I_Rain_Gauge.get("name") if sensor_Texas_Electronics_TR_525I_Rain_Gauge else "",
        "Texas Electronics TR-525I Rain Gauge Observation Method": sensor_Texas_Electronics_TR_525I_Rain_Gauge.get("Observation Method") if sensor_Texas_Electronics_TR_525I_Rain_Gauge else "",
        "Texas Electronics TR-525I Rain Gauge Min Measurement Range": f"'{sensor_Texas_Electronics_TR_525I_Rain_Gauge.get('Min Measurement Range')}" if sensor_Texas_Electronics_TR_525I_Rain_Gauge else "",
        "Texas Electronics TR-525I Rain Gauge Max Measurement Range": f"'{sensor_Texas_Electronics_TR_525I_Rain_Gauge.get('Max Measurement Range')}" if sensor_Texas_Electronics_TR_525I_Rain_Gauge else "",
        "Texas Electronics TR-525I Rain Gauge Accuracy": f"'{sensor_Texas_Electronics_TR_525I_Rain_Gauge.get('Accuracy')}" if sensor_Texas_Electronics_TR_525I_Rain_Gauge else "",
        # "Texas Electronics TR-525I Rain Gauge description": f"'{sensor_Texas_Electronics_TR_525I_Rain_Gauge.get('description')}" if sensor_Texas_Electronics_TR_525I_Rain_Gauge else "",
        
        "Texas Electronics TR-525I-HT Rain Gauge Name" : sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge.get("name") if sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge else "",
        "Texas Electronics TR-525I-HT Rain Gauge Observation Method": sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge.get("Observation Method") if sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge else "",
        "Texas Electronics TR-525I-HT Rain Gauge Min Measurement Range": f"'{sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge.get('Min Measurement Range')}" if sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge else "",
        "Texas Electronics TR-525I-HT Rain Gauge Max Measurement Range": f"'{sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge.get('Max Measurement Range')}" if sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge else "",
        "Texas Electronics TR-525I-HT Rain Gauge Accuracy": f"'{sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge.get('Accuracy')}" if sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge else "",
        # "Texas Electronics TR-525I-HT Rain Gauge description": f"'{sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge.get('description')}" if sensor_Texas_Electronics_TR_525I_HT_Rain_Gauge else "",
        
        "Texas Electronics TR-525USW Rain Gauge Name" : sensor_Texas_Electronics_TR_525USW_Rain_Gauge.get("name") if sensor_Texas_Electronics_TR_525USW_Rain_Gauge else "",
        "Texas Electronics TR-525USW Rain Gauge Observation Method": sensor_Texas_Electronics_TR_525USW_Rain_Gauge.get("Observation Method") if sensor_Texas_Electronics_TR_525USW_Rain_Gauge else "",
        "Texas Electronics TR-525USW Rain Gauge Min Measurement Range": f"'{sensor_Texas_Electronics_TR_525USW_Rain_Gauge.get('Min Measurement Range')}" if sensor_Texas_Electronics_TR_525USW_Rain_Gauge else "",
        "Texas Electronics TR-525USW Rain Gauge Max Measurement Range": f"'{sensor_Texas_Electronics_TR_525USW_Rain_Gauge.get('Max Measurement Range')}" if sensor_Texas_Electronics_TR_525USW_Rain_Gauge else "",
        "Texas Electronics TR-525USW Rain Gauge Accuracy": f"'{sensor_Texas_Electronics_TR_525USW_Rain_Gauge.get('Accuracy')}" if sensor_Texas_Electronics_TR_525USW_Rain_Gauge else "",
        # "Texas Electronics TR-525USW Rain Gauge description": f"'{sensor_Texas_Electronics_TR_525USW_Rain_Gauge.get('description')}" if sensor_Texas_Electronics_TR_525USW_Rain_Gauge else "",
         
        "Vaisala HMP45C Thermometer & Hygrometer Name" : sensor_Vaisala_HMP45C_Thermometer_Hygrometer.get("name") if sensor_Vaisala_HMP45C_Thermometer_Hygrometer else "",
        "Vaisala HMP45C Thermometer & Hygrometer Observation Method": sensor_Vaisala_HMP45C_Thermometer_Hygrometer.get("Observation Method") if sensor_Vaisala_HMP45C_Thermometer_Hygrometer else "",
        "Vaisala HMP45C Thermometer & Hygrometer Min Measurement Range": f"'{sensor_Vaisala_HMP45C_Thermometer_Hygrometer.get('Min Measurement Range')}" if sensor_Vaisala_HMP45C_Thermometer_Hygrometer else "",
        "Vaisala HMP45C Thermometer & Hygrometer Max Measurement Range": f"'{sensor_Vaisala_HMP45C_Thermometer_Hygrometer.get('Max Measurement Range')}" if sensor_Vaisala_HMP45C_Thermometer_Hygrometer else "",
        "Vaisala HMP45C Thermometer & Hygrometer Accuracy": f"'{sensor_Vaisala_HMP45C_Thermometer_Hygrometer.get('Accuracy')}" if sensor_Vaisala_HMP45C_Thermometer_Hygrometer else "",
        # "Vaisala HMP45C Thermometer & Hygrometer description": f"'{sensor_Vaisala_HMP45C_Thermometer_Hygrometer.get('description')}" if sensor_Vaisala_HMP45C_Thermometer_Hygrometer else "",
        
        "Vaisala HMP35C Thermometer & Hygrometer Name" : sensor_Vaisala_HMP35C_Thermometer_Hygrometer.get("name") if sensor_Vaisala_HMP35C_Thermometer_Hygrometer else "",
        "Vaisala HMP35C Thermometer & Hygrometer Observation Method": sensor_Vaisala_HMP35C_Thermometer_Hygrometer.get("Observation Method") if sensor_Vaisala_HMP35C_Thermometer_Hygrometer else "",
        "Vaisala HMP35C Thermometer & Hygrometer Min Measurement Range": f"'{sensor_Vaisala_HMP35C_Thermometer_Hygrometer.get('Min Measurement Range')}" if sensor_Vaisala_HMP35C_Thermometer_Hygrometer else "",
        "Vaisala HMP35C Thermometer & Hygrometer Max Measurement Range": f"'{sensor_Vaisala_HMP35C_Thermometer_Hygrometer.get('Max Measurement Range')}" if sensor_Vaisala_HMP35C_Thermometer_Hygrometer else "",
        "Vaisala HMP35C Thermometer & Hygrometer Accuracy": f"'{sensor_Vaisala_HMP35C_Thermometer_Hygrometer.get('Accuracy')}" if sensor_Vaisala_HMP35C_Thermometer_Hygrometer else "",
        # "Vaisala HMP35C Thermometer & Hygrometer description": f"'{sensor_Vaisala_HMP35C_Thermometer_Hygrometer.get('description')}" if sensor_Vaisala_HMP35C_Thermometer_Hygrometer else "",
        
        "Vaisala PTB101B Barometer Name" : sensor_Vaisala_PTB101B_Barometer.get("name") if sensor_Vaisala_PTB101B_Barometer else "",
        "Vaisala PTB101B Barometer Observation Method": sensor_Vaisala_PTB101B_Barometer.get("Observation Method") if sensor_Vaisala_PTB101B_Barometer else "",
        "Vaisala PTB101B Barometer Min Measurement Range": f"'{sensor_Vaisala_PTB101B_Barometer.get('Min Measurement Range')}" if sensor_Vaisala_PTB101B_Barometer else "",
        "Vaisala PTB101B Barometer Max Measurement Range": f"'{sensor_Vaisala_PTB101B_Barometer.get('Max Measurement Range')}" if sensor_Vaisala_PTB101B_Barometer else "",
        "Vaisala PTB101B Barometer Accuracy": f"'{sensor_Vaisala_PTB101B_Barometer.get('Accuracy')}" if sensor_Vaisala_PTB101B_Barometer else "",
        # "Vaisala PTB101B Barometer description": f"'{sensor_Vaisala_PTB101B_Barometer.get('description')}" if sensor_Vaisala_PTB101B_Barometer else "",
        
        "Campbell Scientific 107 Soil Thermometer Name" : sensor_Campbell_Scientific_107_Soil_Thermometer.get("name") if sensor_Campbell_Scientific_107_Soil_Thermometer else "",
        "Campbell Scientific 107 Soil Thermometer Observation Method": sensor_Campbell_Scientific_107_Soil_Thermometer.get("Observation Method") if sensor_Campbell_Scientific_107_Soil_Thermometer else "",
        "Campbell Scientific 107 Soil Thermometer Min Measurement Range": f"'{sensor_Campbell_Scientific_107_Soil_Thermometer.get('Min Measurement Range')}" if sensor_Campbell_Scientific_107_Soil_Thermometer else "",
        "Campbell Scientific 107 Soil Thermometer Max Measurement Range": f"'{sensor_Campbell_Scientific_107_Soil_Thermometer.get('Max Measurement Range')}" if sensor_Campbell_Scientific_107_Soil_Thermometer else "",
        "Campbell Scientific 107 Soil Thermometer Accuracy": f"'{sensor_Campbell_Scientific_107_Soil_Thermometer.get('Accuracy')}" if sensor_Campbell_Scientific_107_Soil_Thermometer else "",
        # "Campbell Scientific 107 Soil Thermometer description": f"'{sensor_Campbell_Scientific_107_Soil_Thermometer.get('description')}" if sensor_Campbell_Scientific_107_Soil_Thermometer else "",
        
        "Campbell Scientific CS616 Soil Hygrometer Name" : sensor_Campbell_Scientific_CS616_Soil_Hygrometer.get("name") if sensor_Campbell_Scientific_CS616_Soil_Hygrometer else "",
        "Campbell Scientific CS616 Soil Hygrometer Observation Method": sensor_Campbell_Scientific_CS616_Soil_Hygrometer.get("Observation Method") if sensor_Campbell_Scientific_CS616_Soil_Hygrometer else "",
        "Campbell Scientific CS616 Soil Hygrometer Min Measurement Range": f"'{sensor_Campbell_Scientific_CS616_Soil_Hygrometer.get('Min Measurement Range')}" if sensor_Campbell_Scientific_CS616_Soil_Hygrometer else "",
        "Campbell Scientific CS616 Soil Hygrometer Max Measurement Range": f"'{sensor_Campbell_Scientific_CS616_Soil_Hygrometer.get('Max Measurement Range')}" if sensor_Campbell_Scientific_CS616_Soil_Hygrometer else "",
        "Campbell Scientific CS616 Soil Hygrometer Accuracy": f"'{sensor_Campbell_Scientific_CS616_Soil_Hygrometer.get('Accuracy')}" if sensor_Campbell_Scientific_CS616_Soil_Hygrometer else "",
        # "Campbell Scientific CS616 Soil Hygrometer description": f"'{sensor_Campbell_Scientific_CS616_Soil_Hygrometer.get('description')}" if sensor_Campbell_Scientific_CS616_Soil_Hygrometer else "",
        
        "Peet Brothers 2000 Ultimeter Name" : sensor_Peet_Brothers_2000_Ultimeter.get("name") if sensor_Peet_Brothers_2000_Ultimeter else "",
        "Peet Brothers 2000 Ultimeter Observation Method": sensor_Peet_Brothers_2000_Ultimeter.get("Observation Method") if sensor_Peet_Brothers_2000_Ultimeter else "",
        "Peet Brothers 2000 Ultimeter Min Measurement Range": f"'{sensor_Peet_Brothers_2000_Ultimeter.get('Min Measurement Range')}" if sensor_Peet_Brothers_2000_Ultimeter else "",
        "Peet Brothers 2000 Ultimeter Max Measurement Range": f"'{sensor_Peet_Brothers_2000_Ultimeter.get('Max Measurement Range')}" if sensor_Peet_Brothers_2000_Ultimeter else "",
        "Peet Brothers 2000 Ultimeter Accuracy": f"'{sensor_Peet_Brothers_2000_Ultimeter.get('Accuracy')}" if sensor_Peet_Brothers_2000_Ultimeter else "",
        # "Peet Brothers 2000 Ultimeter description": f"'{sensor_Peet_Brothers_2000_Ultimeter.get('description')}" if sensor_Peet_Brothers_2000_Ultimeter else "",
        
        "Peet Brothers 2100 Ultimeter Name" : sensor_Peet_Brothers_2100_Ultimeter.get("name") if sensor_Peet_Brothers_2100_Ultimeter else "",
        "Peet Brothers 2100 Ultimeter Observation Method": sensor_Peet_Brothers_2100_Ultimeter.get("Observation Method") if sensor_Peet_Brothers_2100_Ultimeter else "",
        "Peet Brothers 2100 Ultimeter Min Measurement Range": f"'{sensor_Peet_Brothers_2100_Ultimeter.get('Min Measurement Range')}" if sensor_Peet_Brothers_2100_Ultimeter else "",
        "Peet Brothers 2100 Ultimeter Max Measurement Range": f"'{sensor_Peet_Brothers_2100_Ultimeter.get('Max Measurement Range')}" if sensor_Peet_Brothers_2100_Ultimeter else "",
        "Peet Brothers 2100 Ultimeter Accuracy": f"'{sensor_Peet_Brothers_2100_Ultimeter.get('Accuracy')}" if sensor_Peet_Brothers_2100_Ultimeter else "",
        # "Peet Brothers 2100 Ultimeter description": f"'{sensor_Peet_Brothers_2100_Ultimeter.get('description')}" if sensor_Peet_Brothers_2100_Ultimeter else "",
        
        "Peet Brothers UNKNOWN Ultimeter Name" : sensor_Peet_Brothers_UNKNOWN_Ultimeter.get("name") if sensor_Peet_Brothers_UNKNOWN_Ultimeter else "",
        "Peet Brothers UNKNOWN Ultimeter Observation Method": sensor_Peet_Brothers_UNKNOWN_Ultimeter.get("Observation Method") if sensor_Peet_Brothers_UNKNOWN_Ultimeter else "",
        "Peet Brothers UNKNOWN Ultimeter Min Measurement Range": f"'{sensor_Peet_Brothers_UNKNOWN_Ultimeter.get('Min Measurement Range')}" if sensor_Peet_Brothers_UNKNOWN_Ultimeter else "",
        "Peet Brothers UNKNOWN Ultimeter Max Measurement Range": f"'{sensor_Peet_Brothers_UNKNOWN_Ultimeter.get('Max Measurement Range')}" if sensor_Peet_Brothers_UNKNOWN_Ultimeter else "",
        "Peet Brothers UNKNOWN Ultimeter Accuracy": f"'{sensor_Peet_Brothers_UNKNOWN_Ultimeter.get('Accuracy')}" if sensor_Peet_Brothers_UNKNOWN_Ultimeter else "",
        # "Peet Brothers UNKNOWN Ultimeter description": f"'{sensor_Peet_Brothers_UNKNOWN_Ultimeter.get('description')}" if sensor_Peet_Brothers_UNKNOWN_Ultimeter else "",
        
        
        "Campbell Scientific SR50A Snow Depth Sensor Name" : sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor.get("name") if sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50A Snow Depth Sensor Observation Method": sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor.get("Observation Method") if sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50A Snow Depth Sensor Min Measurement Range": f"'{sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor.get('Min Measurement Range')}" if sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50A Snow Depth Sensor Max Measurement Range": f"'{sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor.get('Max Measurement Range')}" if sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50A Snow Depth Sensor Accuracy": f"'{sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor.get('Accuracy')}" if sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor else "",
        # "Campbell Scientific SR50A Snow Depth Sensor description": f"'{sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor.get('description')}" if sensor_Campbell_Scientific_SR50A_Snow_Depth_Sensor else "",
        
        "Campbell Scientific SR50 Snow Depth Sensor Name" : sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor.get("name") if sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50 Snow Depth Sensor Observation Method": sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor.get("Observation Method") if sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50 Snow Depth Sensor Min Measurement Range": f"'{sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor.get('Min Measurement Range')}" if sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50 Snow Depth Sensor Max Measurement Range": f"'{sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor.get('Max Measurement Range')}" if sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor else "",
        "Campbell Scientific SR50 Snow Depth Sensor Accuracy": f"'{sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor.get('Accuracy')}" if sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor else "",
        # "Campbell Scientific SR50 Snow Depth Sensor description": f"'{sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor.get('description')}" if sensor_Campbell_Scientific_SR50_Snow_Depth_Sensor else "",
        
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Name" : sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer.get("name") if sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer else "",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Observation Method": sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer.get("Observation Method") if sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer else "",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Min Measurement Range": f"'{sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer.get('Min Measurement Range')}" if sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer else "",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Max Measurement Range": f"'{sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer.get('Max Measurement Range')}" if sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer else "",
        "Peet Brothers WSF-10072 Thermometer & Hygrometer Accuracy": f"'{sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer.get('Accuracy')}" if sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer else "",
        # "Peet Brothers WSF-10072 Thermometer & Hygrometer description": f"'{sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer.get('description')}" if sensor_Peet_Brothers_WSF_10072_Thermometer_Hygrometer else "",
        
        "Peet Brothers OTS Thermometer Name" : sensor_Peet_Brothers_OTS_Thermometer.get("name") if sensor_Peet_Brothers_OTS_Thermometer else "",
        "Peet Brothers OTS Thermometer Observation Method": sensor_Peet_Brothers_OTS_Thermometer.get("Observation Method") if sensor_Peet_Brothers_OTS_Thermometer else "",
        "Peet Brothers OTS Thermometer Min Measurement Range": f"'{sensor_Peet_Brothers_OTS_Thermometer.get('Min Measurement Range')}" if sensor_Peet_Brothers_OTS_Thermometer else "",
        "Peet Brothers OTS Thermometer Max Measurement Range": f"'{sensor_Peet_Brothers_OTS_Thermometer.get('Max Measurement Range')}" if sensor_Peet_Brothers_OTS_Thermometer else "",
        "Peet Brothers OTS Thermometer Accuracy": f"'{sensor_Peet_Brothers_OTS_Thermometer.get('Accuracy')}" if sensor_Peet_Brothers_OTS_Thermometer else "",
        # "Peet Brothers OTS Thermometer description": f"'{sensor_Peet_Brothers_OTS_Thermometer.get('description')}" if sensor_Peet_Brothers_OTS_Thermometer else "",

        "Peet Brothers AWVS Wind Monitor Name" : sensor_Peet_Brothers_AWVS_Wind_Monitor.get("name") if sensor_Peet_Brothers_AWVS_Wind_Monitor else "",
        "Peet Brothers AWVS Wind Monitor Observation Method": sensor_Peet_Brothers_AWVS_Wind_Monitor.get("Observation Method") if sensor_Peet_Brothers_AWVS_Wind_Monitor else "",
        "Peet Brothers AWVS Wind Monitor Min Measurement Range": f"'{sensor_Peet_Brothers_AWVS_Wind_Monitor.get('Min Measurement Range')}" if sensor_Peet_Brothers_AWVS_Wind_Monitor else "",
        "Peet Brothers AWVS Wind Monitor Max Measurement Range": f"'{sensor_Peet_Brothers_AWVS_Wind_Monitor.get('Max Measurement Range')}" if sensor_Peet_Brothers_AWVS_Wind_Monitor else "",
        "Peet Brothers AWVS Wind Monitor Accuracy": f"'{sensor_Peet_Brothers_AWVS_Wind_Monitor.get('Accuracy')}" if sensor_Peet_Brothers_AWVS_Wind_Monitor else "",
        # "Peet Brothers AWVS Wind Monitor description": f"'{sensor_Peet_Brothers_AWVS_Wind_Monitor.get('description')}" if sensor_Peet_Brothers_AWVS_Wind_Monitor else "",

        "Peet Brothers AWVP Wind Monitor Name" : sensor_Peet_Brothers_AWVP_Wind_Monitor.get("name") if sensor_Peet_Brothers_AWVP_Wind_Monitor else "",
        "Peet Brothers AWVP Wind Monitor Observation Method": sensor_Peet_Brothers_AWVP_Wind_Monitor.get("Observation Method") if sensor_Peet_Brothers_AWVP_Wind_Monitor else "",
        "Peet Brothers AWVP Wind Monitor Min Measurement Range": f"'{sensor_Peet_Brothers_AWVP_Wind_Monitor.get('Min Measurement Range')}" if sensor_Peet_Brothers_AWVP_Wind_Monitor else "",
        "Peet Brothers AWVP Wind Monitor Max Measurement Range": f"'{sensor_Peet_Brothers_AWVP_Wind_Monitor.get('Max Measurement Range')}" if sensor_Peet_Brothers_AWVP_Wind_Monitor else "",
        "Peet Brothers AWVP Wind Monitor Accuracy": f"'{sensor_Peet_Brothers_AWVP_Wind_Monitor.get('Accuracy')}" if sensor_Peet_Brothers_AWVP_Wind_Monitor else "",
        # "Peet Brothers AWVP Wind Monitor description": f"'{sensor_Peet_Brothers_AWVP_Wind_Monitor.get('description')}" if sensor_Peet_Brothers_AWVP_Wind_Monitor else "",
        
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Name" : sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer.get("name") if sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer else "",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Observation Method": sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer.get("Observation Method") if sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer else "",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Min Measurement Range": f"'{sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer.get('Min Measurement Range')}" if sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer else "",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Max Measurement Range": f"'{sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer.get('Max Measurement Range')}" if sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer else "",
        "Campbell Scientific CS650 Soil Hygrometer & Thermometer Accuracy": f"'{sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer.get('Accuracy')}" if sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer else "",
        # "Campbell Scientific CS650 Soil Hygrometer & Thermometer description": f"'{sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer.get('description')}" if sensor_Campbell_Scientific_CS650_Soil_Hygrometer_Thermometer else "",
        
        
        "Rotronic HC2S3 Thermometer & Hygrometer Name" : sensor_Rotronic_HC2S3_Thermometer_Hygrometer.get("name") if sensor_Rotronic_HC2S3_Thermometer_Hygrometer else "",
        "Rotronic HC2S3 Thermometer & Hygrometer Observation Method": sensor_Rotronic_HC2S3_Thermometer_Hygrometer.get("Observation Method") if sensor_Rotronic_HC2S3_Thermometer_Hygrometer else "",
        "Rotronic HC2S3 Thermometer & Hygrometer Min Measurement Range": f"'{sensor_Rotronic_HC2S3_Thermometer_Hygrometer.get('Min Measurement Range')}" if sensor_Rotronic_HC2S3_Thermometer_Hygrometer else "",
        "Rotronic HC2S3 Thermometer & Hygrometer Max Measurement Range": f"'{sensor_Rotronic_HC2S3_Thermometer_Hygrometer.get('Max Measurement Range')}" if sensor_Rotronic_HC2S3_Thermometer_Hygrometer else "",
        "Rotronic HC2S3 Thermometer & Hygrometer Accuracy": f"'{sensor_Rotronic_HC2S3_Thermometer_Hygrometer.get('Accuracy')}" if sensor_Rotronic_HC2S3_Thermometer_Hygrometer else "",
        # "Rotronic HC2S3 Thermometer & Hygrometer description": f"'{sensor_Rotronic_HC2S3_Thermometer_Hygrometer.get('description')}" if sensor_Rotronic_HC2S3_Thermometer_Hygrometer else "",
        
        "Vaisala PTB110 Barometer Name" : sensor_Vaisala_PTB110_Barometer.get("name") if sensor_Vaisala_PTB110_Barometer else "",
        "Vaisala PTB110 Barometer Observation Method": sensor_Vaisala_PTB110_Barometer.get("Observation Method") if sensor_Vaisala_PTB110_Barometer else "",
        "Vaisala PTB110 Barometer Min Measurement Range": f"'{sensor_Vaisala_PTB110_Barometer.get('Min Measurement Range')}" if sensor_Vaisala_PTB110_Barometer else "",
        "Vaisala PTB110 Barometer Max Measurement Range": f"'{sensor_Vaisala_PTB110_Barometer.get('Max Measurement Range')}" if sensor_Vaisala_PTB110_Barometer else "",
        "Vaisala PTB110 Barometer Accuracy": f"'{sensor_Vaisala_PTB110_Barometer.get('Accuracy')}" if sensor_Vaisala_PTB110_Barometer else "",
        # "Vaisala PTB110 Barometer description": f"'{sensor_Vaisala_PTB110_Barometer.get('description')}" if sensor_Vaisala_PTB110_Barometer else "",
        
        "Campbell Scientific EE181 Thermometer & Hygrometer Name" : sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer.get("name") if sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer else "",
        "Campbell Scientific EE181 Thermometer & Hygrometer Observation Method": sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer.get("Observation Method") if sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer else "",
        "Campbell Scientific EE181 Thermometer & Hygrometer Min Measurement Range": f"'{sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer.get('Min Measurement Range')}" if sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer else "",
        "Campbell Scientific EE181 Thermometer & Hygrometer Max Measurement Range": f"'{sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer.get('Max Measurement Range')}" if sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer else "",
        "Campbell Scientific EE181 Thermometer & Hygrometer Accuracy": f"'{sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer.get('Accuracy')}" if sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer else "",
        # "Campbell Scientific EE181 Thermometer & Hygrometer description": f"'{sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer.get('description')}" if sensor_Campbell_Scientific_EE181_Thermometer_Hygrometer else "",
        
        "Setra Model 278 Barometer Name" : sensor_Setra_Model_278_Barometer.get("name") if sensor_Setra_Model_278_Barometer else "",
        "Setra Model 278 Barometer Observation Method": sensor_Setra_Model_278_Barometer.get("Observation Method") if sensor_Setra_Model_278_Barometer else "",
        "Setra Model 278 Barometer Min Measurement Range": f"'{sensor_Setra_Model_278_Barometer.get('Min Measurement Range')}" if sensor_Setra_Model_278_Barometer else "",
        "Setra Model 278 Barometer Max Measurement Range": f"'{sensor_Setra_Model_278_Barometer.get('Max Measurement Range')}" if sensor_Setra_Model_278_Barometer else "",
        "Setra Model 278 Barometer Accuracy": f"'{sensor_Setra_Model_278_Barometer.get('Accuracy')}" if sensor_Setra_Model_278_Barometer else "",
        # "Setra Model 278 Barometer description": f"'{sensor_Setra_Model_278_Barometer.get('description')}" if sensor_Setra_Model_278_Barometer else "",       
        
        "Campbell Scientific 034B-L Wind Monitor Name" : sensor_Campbell_Scientific_034B_L_Wind_Monitor.get("name") if sensor_Campbell_Scientific_034B_L_Wind_Monitor else "",
        "Campbell Scientific 034B-L Wind Monitor Observation Method": sensor_Campbell_Scientific_034B_L_Wind_Monitor.get("Observation Method") if sensor_Campbell_Scientific_034B_L_Wind_Monitor else "",
        "Campbell Scientific 034B-L Wind Monitor Min Measurement Range": f"'{sensor_Campbell_Scientific_034B_L_Wind_Monitor.get('Min Measurement Range')}" if sensor_Campbell_Scientific_034B_L_Wind_Monitor else "",
        "Campbell Scientific 034B-L Wind Monitor Max Measurement Range": f"'{sensor_Campbell_Scientific_034B_L_Wind_Monitor.get('Max Measurement Range')}" if sensor_Campbell_Scientific_034B_L_Wind_Monitor else "",
        "Campbell Scientific 034B-L Wind Monitor Accuracy": f"'{sensor_Campbell_Scientific_034B_L_Wind_Monitor.get('Accuracy')}" if sensor_Campbell_Scientific_034B_L_Wind_Monitor else "",
        # "Campbell Scientific 034B-L Wind Monitor description": f"'{sensor_Campbell_Scientific_034B_L_Wind_Monitor.get('description')}" if sensor_Campbell_Scientific_034B_L_Wind_Monitor else "",
        
        "Campbell Scientific BaroVue 10 Barometer Name" : sensor_Campbell_Scientific_BaroVue_10_Barometer.get("name") if sensor_Campbell_Scientific_BaroVue_10_Barometer else "",
        "Campbell Scientific BaroVue 10 Barometer Observation Method": sensor_Campbell_Scientific_BaroVue_10_Barometer.get("Observation Method") if sensor_Campbell_Scientific_BaroVue_10_Barometer else "",
        "Campbell Scientific BaroVue 10 Barometer Min Measurement Range": f"'{sensor_Campbell_Scientific_BaroVue_10_Barometer.get('Min Measurement Range')}" if sensor_Campbell_Scientific_BaroVue_10_Barometer else "",
        "Campbell Scientific BaroVue 10 Barometer Max Measurement Range": f"'{sensor_Campbell_Scientific_BaroVue_10_Barometer.get('Max Measurement Range')}" if sensor_Campbell_Scientific_BaroVue_10_Barometer else "",
        "Campbell Scientific BaroVue 10 Barometer Accuracy": f"'{sensor_Campbell_Scientific_BaroVue_10_Barometer.get('Accuracy')}" if sensor_Campbell_Scientific_BaroVue_10_Barometer else "",
        # "Campbell Scientific BaroVue 10 Barometer description": f"'{sensor_Campbell_Scientific_BaroVue_10_Barometer.get('description')}" if sensor_Campbell_Scientific_BaroVue_10_Barometer else "",
        
        
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Name" : sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor.get("name") if sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor else "",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Observation Method": sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor.get("Observation Method") if sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor else "",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Min Measurement Range": f"'{sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor.get('Min Measurement Range')}" if sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor else "",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Max Measurement Range": f"'{sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor.get('Max Measurement Range')}" if sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor else "",
        "Campbell Scientific SnowVue 10 Snow Depth Sensor Accuracy": f"'{sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor.get('Accuracy')}" if sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor else "",
        # "Campbell Scientific SnowVue 10 Snow Depth Sensor description": f"'{sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor.get('description')}" if sensor_Campbell_Scientific_SnowVue_10_Snow_Depth_Sensor else "",        
        
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Name" : sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor.get("name") if sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor else "",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Observation Method": sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor.get("Observation Method") if sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor else "",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Min Measurement Range": f"'{sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor.get('Min Measurement Range')}" if sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor else "",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Max Measurement Range": f"'{sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor.get('Max Measurement Range')}" if sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor else "",
        "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor Accuracy": f"'{sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor.get('Accuracy')}" if sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor else "",
        # "Campbell Scientific SoilVue 10 Soil Water Content/Temperature Sensor description": f"'{sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor.get('description')}" if sensor_Campbell_Scientific_SoilVue_10_Soil_Water_Content_Temperature_Sensor else "",       
        
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Name" : sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor.get("name") if sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor else "",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Observation Method": sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor.get("Observation Method") if sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor else "",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Min Measurement Range": f"'{sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor.get('Min Measurement Range')}" if sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor else "",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Max Measurement Range": f"'{sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor.get('Max Measurement Range')}" if sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor else "",
        "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor Accuracy": f"'{sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor.get('Accuracy')}" if sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor else "",
        # "Campbell Scientific HygroVue 10 Digital Temperature and Relative Humidity Sensor description": f"'{sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor.get('description')}" if sensor_Campbell_Scientific_HygroVue_10_Digital_Temperature_Relative_Humidity_Sensor else "",       
        
        "R.M. Young Company 04101 Wind Monitor Name" : sensor_R_M_Young_Company_04101_Wind_Monitor.get("name") if sensor_R_M_Young_Company_04101_Wind_Monitor else "",
        "R.M. Young Company 04101 Wind Monitor Observation Method": sensor_R_M_Young_Company_04101_Wind_Monitor.get("Observation Method") if sensor_R_M_Young_Company_04101_Wind_Monitor else "",
        "R.M. Young Company 04101 Wind Monitor Min Measurement Range": f"'{sensor_R_M_Young_Company_04101_Wind_Monitor.get('Min Measurement Range')}" if sensor_R_M_Young_Company_04101_Wind_Monitor else "",
        "R.M. Young Company 04101 Wind Monitor Max Measurement Range": f"'{sensor_R_M_Young_Company_04101_Wind_Monitor.get('Max Measurement Range')}" if sensor_R_M_Young_Company_04101_Wind_Monitor else "",
        "R.M. Young Company 04101 Wind Monitor Accuracy": f"'{sensor_R_M_Young_Company_04101_Wind_Monitor.get('Accuracy')}" if sensor_R_M_Young_Company_04101_Wind_Monitor else "",
        # "R.M. Young Company 04101 Wind Monitor description": f"'{sensor_R_M_Young_Company_04101_Wind_Monitor.get('description')}" if sensor_R_M_Young_Company_04101_Wind_Monitor else "",


    }
    for key, value in data_save.items():
        if value.strip():
            print(f"{key}: {value}")
        else:
            print(f"{key}: Data tidak tersedia")

    # print(data_save)
    save_station_data(data_save)



    # Masukkan ke dalam dict dengan label yang kamu mau
    # data_save = {

    #     "Rain Sensor Name": rain_sensor.get("name") if rain_sensor else " ",
    #     "Rain Sensor Type": rain_sensor.get("Observation Method") if rain_sensor else " ",
    #     "Rain Sensor Min Range": rain_sensor.get("Min Measurement Range") if rain_sensor else " ",
    #     "Rain Sensor Max Range": rain_sensor.get("Max Measurement Range") if rain_sensor else " ",
    #     "Rain Sensor Accuracy": rain_sensor.get("Accuracy") if rain_sensor else " ",
    #     "Rain Sensor Description": rain_sensor.get("description") if rain_sensor else " ",
    #     "Rain Sensor Image": rain_sensor.get("image") if rain_sensor else " "
    # }
    # for key, value in data_save.items():
    #     if value.strip():
    #         print(f"{key}: {value}")
    #     else:
    #         print(f"{key}: Data tidak tersedia")

    # print(data_save)
    # save_station_data(data_save)


    # sensor_name = list(sensor_data.keys())
    # sensor_info = sensor_data[sensor_name]

    # data = {
    #     "Sensor Type": sensor_info.get("Sensor Type", " "),
    #     "Brand": sensor_info.get("Brand", " "),
    #     "Model": sensor_info.get("Model", " "),
    #     "Install Date": f"'{sensor_info.get('Install Date', ' ')}",
    #     "Sensor Height from Station Base": sensor_info.get("Sensor Height from Station Base", " "),
    #     "Sensor Height AGL": sensor_info.get("Sensor Height AGL", " ")
    # }
    # print(data)




def main():
    html = get_html(BASE_URL)
    if not html:
        print("Failed to retrieve HTML.")
        return

    sensor_links = extract_sensor_links(html)
    process_sensor_links(sensor_links)

    station_urls = parse_html(html)
    for url in station_urls:
        station_html = get_html(url)
        if station_html:
            extract_data_from_url(station_html, url)
        # break 


if __name__ == "__main__":
    main()
