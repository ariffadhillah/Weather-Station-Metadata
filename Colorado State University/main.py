import requests
import csv

url = "https://coagmet.colostate.edu/data/metadata.json"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Tentukan header tetap sesuai urutan data_save
    headers = [
        'Station Name',
        'Station ID',
        'Location',
        'Latitude',
        'Longitude',
        'Elevation',
        'Anemometer Height',
        'First obs',
        'Last obs',
        'Irrigation',
        'Status',
        'Time step',
        'Network',
        'Unit'
    ]

    all_data = []

    for station_id, info in data.items():
        name = info.get("name")
        station = info.get("station")
        location = info.get("location")
        lat = info.get("lat")
        lon = info.get("lon")
        elevation = info.get("elevation")
        anemometerHeight = info.get("anemometerHeight")
        active = info.get("active")
        irrigation = info.get("irrigation")
        firstObs = info.get("firstObs")
        lastObs = info.get("lastObs")
        timestep = info.get("timestep")
        network = info.get("network")
        units = info.get("units")

        data_save = {
            'Station Name': name,
            'Station ID': station,
            'Location': location,
            'Latitude': f"'{lat}",
            'Longitude': f"'{lon}",
            'Elevation': f"'{elevation}",
            'Anemometer Height': f"'{anemometerHeight}",
            'First obs': firstObs,
            'Last obs': lastObs,
            'Irrigation': irrigation,
            'Status': active,
            'Time step': f"'{timestep}",
            'Network': network,
            'Unit': units
        }

        all_data.append(data_save)

    # Tulis ke file CSV
    filename = 'Colorado State University.csv'
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Data berhasil disimpan ke {filename}")

except requests.exceptions.RequestException as e:
    print(f"Terjadi kesalahan saat mengakses data: {e}")
