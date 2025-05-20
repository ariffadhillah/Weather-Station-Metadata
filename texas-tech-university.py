import requests
import json
import csv
import os

BASE_URL = "https://api.mesonet.ttu.edu/mesoweb/sites/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

CSV_FILENAME = "Texas Tech University----.csv"
FIELDNAMES = [ "Station Name", "Mesonet ID / NWSLI ID", "Station ID", "NWS ID", "SHEF ID", "Station address", "County", "State", "Latitude", "Longitude", "Elevation", "Commissioned" ]



def save_station_data(row, filename=CSV_FILENAME):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        
        writer.writerow(row)
        file.flush()


def download_image(image_url, filename):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Gambar disimpan: {filename}")
    except Exception as e:
        print(f"Gagal menyimpan gambar {image_url}: {e}")


def get_json(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()  # langsung ambil JSON, bukan text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def display_json(data_meta):
    results = data_meta.get("results", [])
    
    
    for meta_data in results:
        station_name  = meta_data['name']
        # mesonet_id  = meta_data['nws_li_id']
        mesonet_id  = meta_data['mesonet_id']
        try:
            station_id  = meta_data['station_id']
        except:
            station_id = ''
        try:
            nws_id_1 = meta_data['nws_kid'] 
        except:
            nws_id_1 = ''
        try:
            nws_id_2 = meta_data['nws_xid']
        except:
            nws_id_2 =''
        try:
            nws_id = nws_id_1 +" / "+ nws_id_2 
        except:
            nws_id =''
        try:
            shef_id	= meta_data['shef_id']
        except:
            shef_id =''
        try:    
            location_desc = meta_data['location_desc']
        except:
            location_desc = ''
        try:
            county = meta_data['county']
        except:
            county= ''
        try:
            state = meta_data['state']
        except:
            state =''
        try:
            latitude = meta_data['latitude']
        except:
            latitude = ''
        try:
            longitude = meta_data['longitude']
        except:
            longitude = ''
        try:
            elevation = meta_data['elevation']
        except:
            elevation =''
        try:
            installed = meta_data['installed']
        except:
            installed =''
        # url_image = f"https://api.mesonet.ttu.edu/media/sodar_photo/{mesonet_id}.jpg"
        url_image = f"https://api.mesonet.ttu.edu/media/mesonet_photo/{mesonet_id}.jpg"
        print(url_image)

        image_folder = "Texas Tech University"
        os.makedirs(image_folder, exist_ok=True)
        image_filename = os.path.join(image_folder, f"{mesonet_id}.jpg")
        download_image(url_image, image_filename)

        
        data_save = {
            "Station Name": station_name,
            "Mesonet ID / NWSLI ID" : mesonet_id,        
            "Station ID" : station_id,
            "NWS ID" : nws_id,
            "SHEF ID" : shef_id,
            "Station address" : location_desc,
            "County" : county,
            "State" : state,
            "Latitude" : f"'{latitude}{'°'}",
            "Longitude" : f"'{longitude}{'°'}",
            "Elevation" : f"'{elevation}{' feet'}",
            "Commissioned" : f"'{installed}"
        }
        # Cetak hasil
        for key, value in data_save.items():
            value_str = str(value).strip()
            if value_str:
                print(f"{key}: {value_str}")
            else:
                print(f"{key}: Data tidak tersedia")

        print("=" * 40)

        save_station_data(data_save)


def main():
    json_data = get_json(BASE_URL)
    if not json_data:
        print("Failed to retrieve JSON.")
        return

    display_json(json_data)


if __name__ == "__main__":
    main()
