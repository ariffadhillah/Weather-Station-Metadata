import requests
from bs4 import BeautifulSoup
import csv

def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def extract_table_data(soup):
    table = soup.find('table', class_='table table-striped table-bordered table-hover cols-10 p-2')
    if not table:
        print("❌ Tabel tidak ditemukan.")
        return []

    rows = table.find_all('tr')
    data_list = []

    for row in rows[1:]:  # Skip header
        cols = row.find_all('td')
        if len(cols) < 10:
            continue

        data = {
            "Station Name": cols[0].get_text(strip=True),
            "Symbol": cols[1].get_text(strip=True),
            "Station ID": cols[2].get_text(strip=True),
            "County": cols[3].get_text(strip=True),
            "Latitude": f"'{cols[4].get_text(strip=True)}",
            "Longitude": f"'{cols[5].get_text(strip=True)}",
            "Elevation (ft)": f"'{cols[6].get_text(strip=True)}",
            "Elevation (m)": f"'{cols[7].get_text(strip=True)}",
            "Status": cols[8].get_text(strip=True),
            "Description": cols[9].get_text(strip=True),
        }
        data_list.append(data)

    return data_list

def extract_sensor_info(soup):
    sensor_data = []
    cards = soup.find_all('div', class_='card-body')
    for card in cards:
        section = card.find('h4')
        if section:
            section_name = section.get_text(strip=True)
            info = {"Section": section_name}
            current_label = ""
            for el in section.find_all_next():
                if el.name == 'h4':
                    break  # stop at next section
                elif el.name == 'span':
                    current_label = el.get_text(strip=True).rstrip(":")
                elif el.name == 'br':
                    continue
                elif el.name is None and current_label:
                    value = el.strip()
                    if value:
                        key = f"{current_label} ({section_name})"
                        info[key] = value
                        current_label = ""
            sensor_data.append(info)
    return sensor_data

def parse_station_detail(station_id):
    detail_url = f"https://azmet.arizona.edu/about/station-metadata/{station_id}"
    print(f"🌐 Membuka URL: {detail_url}")
    html = get_html(detail_url)
    if not html:
        return {}
    soup = BeautifulSoup(html, 'html.parser')
    sensor_data = extract_sensor_info(soup)
    
    # Gabungkan semua dictionary dari sensor_data
    combined_data = {}
    for section_data in sensor_data:
        for key, value in section_data.items():
            if key != "Section":
                combined_data[key] = value
    return combined_data

def main():
    url = "https://azmet.arizona.edu/about/station-metadata"
    html = get_html(url)
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')
    stations = extract_table_data(soup)

    full_data = []

    for station in stations:
        station_id = station.get("Station ID")
        detail_data = parse_station_detail(station_id)

        # Gabungkan data tabel + data detail sensor
        combined = {**station, **detail_data}
        full_data.append(combined)

    # Ambil semua kunci untuk header CSV
    all_keys = set()
    for item in full_data:
        all_keys.update(item.keys())

    # Simpan ke CSV
    with open("azmet_station_data.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(full_data)

    print("✅ Data berhasil disimpan ke azmet_station_data.csv")

if __name__ == "__main__":
    main()
