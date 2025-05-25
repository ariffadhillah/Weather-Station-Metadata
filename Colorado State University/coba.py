import requests
import json
import re

# url = "https://coagmet.colostate.edu/data/metadata.json?units=m&instruments=yes&sponsors=yes"
url = "https://coagmet.colostate.edu/data/nw/metadata.json?dateFmt=us&instruments=yes&sponsors=yes"

try:
    response = requests.get(url)
    response.raise_for_status()
    raw_text = response.text

    # Perbaiki JSON: tambahkan koma setelah "owner": "..." sebelum "sponsors"
    # Pola ini mencari "owner": "some text" langsung diikuti oleh "sponsors": tanpa koma,
    # lalu menambahkan koma di antara keduanya.
    fixed_text = re.sub(r'("owner":\s*".*?")(\s*"sponsors":)', r'\1,\2', raw_text)

    data = json.loads(fixed_text)

    all_data = []

    for station_id, info in data.items():
        data_save = {
            'Station Name': info.get("name", ""),
            'Station ID': info.get("station", ""),
            'Location': info.get("location", ""),
            'Latitude': f"'{info.get('lat', '')}",
            'Longitude': f"'{info.get('lon', '')}",
            'Elevation': f"'{info.get('elevation', '')}",
            'Anemometer Height': f"'{info.get('anemometerHeight', '')}",
            'First obs': info.get("firstObs", ""),
            'Last obs': info.get("lastObs", ""),
            'Irrigation': info.get("irrigation", ""),
            'Status': info.get("active", ""),
            'Time step': f"'{info.get('timestep', '')}",
            'Network': info.get("network", ""),
            'Unit': info.get("units", ""),
            'Logger': info.get("logger", ""),
            'TempRH': info.get("tempRH", ""),
            'Anemometer': info.get("anemometer", ""),
            'Soil Thermometer': info.get("soilThermometer", ""),
            'Rain Gauge': info.get("rainGauge", ""),
            'Owner': info.get("owner", ""),
            'Sponsors': ", ".join(info.get("sponsors", [])) if isinstance(info.get("sponsors"), list) else info.get("sponsors", "")
        }
        all_data.append(data_save)

    # Contoh simpan ke CSV
    import pandas as pd
    df = pd.DataFrame(all_data)
    df.to_csv("Northern Water--Colorado State University-sponsor.csv", index=False)
    print("✅ Data berhasil diperbaiki dan disimpan ke Northern Water--Colorado State University-sponsor.csv")

except requests.exceptions.RequestException as e:
    print("❌ Gagal mengambil data dari URL:", e)

except json.JSONDecodeError as e:
    print("❌ Gagal parsing JSON meskipun sudah diperbaiki:", e)
