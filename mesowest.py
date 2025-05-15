import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://mesowest.utah.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
COOKIES = {
    'cookie': '_ga=GA1.1.747400015.1747097706; _ga_9H9H5K3K29=GS2.1.s1747100058$o1$g0$t1747100060$j0$l0$h0; _ga_S86FS8V059=deleted; _ga_S86FS8V059=GS2.1.s1747264885$o7$g1$t1747265301$j0$l0$h0'
}

def get_states():
    response = requests.get(BASE_URL, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')
    form_search = soup.find("form", id="masterform")
    select = form_search.find("select", id="state")
    options = select.find_all("option")
    
    states = [option["value"] for option in options]
    print(f"🔢 Jumlah state ditemukan: {len(states)}")
    return states

def get_station_ids(state):
    url_state = f"{BASE_URL}cgi-bin/droman/raws_ca_monitor.cgi?state={state}&rawsflag=3"
    print(f"🌐 Memproses state: {state} - URL: {url_state}")
    
    response = requests.get(url_state, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all("table", attrs={"width": "800", "border": "1"})
    
    station_ids = []
    for idx, table in enumerate(tables, 1):
        print(f"\n📄 Tabel #{idx}")
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            for col in cols:
                link = col.find("a")
                if link and link.has_attr("href"):
                    href = link["href"]
                    parsed = urlparse(href)
                    query_params = parse_qs(parsed.query)
                    station_id = query_params.get("stn", [""])[0]
                    if station_id:
                        station_ids.append(station_id)
        print(f"✅ Tabel #{idx} selesai diproses.")
    
    print(f"\n🔢 Jumlah kode station ditemukan: {len(station_ids)}")
    return station_ids

def get_station_info(station_id):
    url_station = f"{BASE_URL}cgi-bin/droman/station_total.cgi?stn={station_id}&unit=0"
    print(f"➡️ Memproses Station ID: {station_id} - URL: {url_station}")
    
    response = requests.get(url_station, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.content, 'html.parser')

    def get_value(label):
        tag = soup.find("b", string=label)
        if tag:
            value_td = tag.find_parent("td").find_next_sibling("td")
            return value_td.get_text(strip=True) if value_td else None
        return None

    station_name = get_value("Station Name:")
    station_id_text = get_value("Station ID:")
    county_text = get_value("County:")
    state_text = get_value("State:")
    country_text = get_value("Country:")
    timezone_text = get_value("Timezone:")
    local_Region_Category_text = get_value("Local Region Category:")


    print(f"🛰️ Station Name: {station_name}")
    print(f"🛰️ Station ID: {station_id_text}")
    print(f"🛰️ County: {county_text}")
    print(f"🛰️ State: {state_text}")
    print(f"🛰️ Country: {country_text}")
    print(f"🛰️ Timezone: {timezone_text}")
    print(f"🛰️ Local Region Category: {local_Region_Category_text}")
    print()

def main():
    states = get_states()
    for i, state in enumerate(states, start=1):
        print(f"\n🗺️ [{i}] Memproses state: {state}")
        station_ids = get_station_ids(state)
        
        for j, station_id in enumerate(station_ids, start=1):
            print(f"\n🔍 [{j}] Info Station:")
            get_station_info(station_id)
        
        break  # hapus ini jika ingin proses semua state

if __name__ == "__main__":
    main()
