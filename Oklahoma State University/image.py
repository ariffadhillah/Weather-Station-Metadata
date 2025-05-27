import requests
import json
import time
import csv
import os
BASE_URL = "https://api.prod.mesonet.org/index.php/meta/sites/status/active/vars/stid,name,lat,lon,wfo"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}


# def save_station_data(row, filename=CSV_FILENAME):
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
#         writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
#         if not file_exists or os.stat(filename).st_size == 0:
#             writer.writeheader()
        
#         writer.writerow(row)
#         file.flush()


def get_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"⚠️ Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error saat ambil data: {e}")
    return None

# def parse_json(html):
#     try:
#         parsed = json.loads(html)
#         stations = parsed["response"]
#         station_ids = [station.get("stid") for station in stations.values() if station.get("stid")]
#         print(station_ids)
#         return station_ids
#     except Exception as e:
#         print(f"❌ Error saat parsing JSON: {e}")
#         return []

def parse_json(html):
    try:
        parsed = json.loads(html)
        stations = parsed["response"]
        # Konversi ke huruf besar (uppercase)
        station_ids = [station.get("stid").upper() for station in stations.values() if station.get("stid")]
        # print(station_ids)
        return station_ids
    except Exception as e:
        print(f"❌ Error saat parsing JSON: {e}")
        return []



def json_page(station_id):
    time.sleep(2)
    detail_url = f"https://content.prod.mesonet.org/repos/meta-site-photos-json/mesonet/{station_id}.json"
    time.sleep(1)
    print(f"🔍 Mengakses detail URL: {detail_url}")

    html = get_url(detail_url)
    if not html:
        print("❌ Gagal mendapatkan data detail.")
        return

    try:
        detail_json = json.loads(html)  # Tanpa indent di sini
        # Cetak dengan indent untuk melihat struktur dengan rapi
        # meta_data = json.dumps(detail_json, indent=4)
        # print(meta_data)
        detail_info__station = detail_json["site_images"]['small']
        url_image = detail_info__station['profile']
        download_image = "https://content.prod.mesonet.org/meta-imagery/mesonet" + url_image
        print(f"🔍 Mengakses detail: {download_image}")

        # Membuat folder jika belum ada
        os.makedirs("Image Station", exist_ok=True)
        image_path = os.path.join("Image Station", f"{station_id}.jpg")

        try:
            img_response = requests.get(download_image, headers=HEADERS, timeout=10)
            if img_response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    img_file.write(img_response.content)
                print(f"✅ Gambar disimpan: {image_path}")
            else:
                print(f"❌ Gagal download gambar, status code: {img_response.status_code}")
        except Exception as e:
            print(f"❌ Error saat download gambar: {e}")


        # save_station_data(data_save)

    except json.JSONDecodeError as e:
        print("❌ Gagal parsing JSON:", e)
        return
    
def main():
    base_html = get_url(BASE_URL)
    if not base_html:
        print("❌ Gagal mendapatkan data.")
        return
    station_ids = parse_json(base_html)
    for station_id in station_ids:
        json_page(station_id)

if __name__ == "__main__":
    main()
