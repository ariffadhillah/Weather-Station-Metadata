import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from random import uniform
from urllib.parse import urlparse, parse_qs


url = "https://mesowest.utah.edu/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
cookies = {
    'cookie': '_ga=GA1.1.747400015.1747097706; _ga_9H9H5K3K29=GS2.1.s1747100058$o1$g0$t1747100060$j0$l0$h0; _ga_S86FS8V059=deleted; _ga_S86FS8V059=GS2.1.s1747264885$o7$g1$t1747265301$j0$l0$h0'
}
response = requests.get(url, headers=headers, cookies=cookies)
soup = BeautifulSoup(response.content, 'html.parser')

form_search = soup.find("form", id="masterform")

select = form_search.find("select", id="state")
options = select.find_all("option")
print("Daftar State:")

data_state = []
id_station = []
for option in options:
    value = option["value"]
    data_state.append(value)

print(f"🔢 Jumlah state ditemukan: {len(data_state)}")

for i, state in enumerate(data_state, start=1):
    url_state = f"https://mesowest.utah.edu/cgi-bin/droman/raws_ca_monitor.cgi?state={state}&rawsflag=3"
    print(f"➡️ [{i}] URL: {url_state}")
    response_state = requests.get(url_state, headers=headers, cookies=cookies)
    soup_state = BeautifulSoup(response_state.content, 'html.parser')

    tables_Region = soup_state.find_all("table", attrs={"width": "800", "border": "1"}) 
    for idx, table_Region in enumerate(tables_Region, 1):
        print(f"\n📄 Tabel #{idx}")
        rows_Region = table_Region.find_all("tr")
        for row_Region in rows_Region:
            cols_Region = row_Region.find_all("td")
            for col_region in cols_Region:
                link_region = col_region.find("a")
                if link_region and link_region.has_attr("href"):
                    href_region = link_region['href']
                    # id_station.append(href_region)
                    parsed_region = urlparse(href_region)
                    query_params_region = parse_qs(parsed_region.query)
                    station_id = query_params_region.get("stn", [""])[0]
                    id_station.append(station_id)
                    # if station_id:
                    #     print(f"🏷️ Kode Station: {station_id}")
        print(f"✅ Tabel #{idx} selesai diproses.")

    # print(f"\n🔢 url kode station: {(id_station)}")
    print(f"\n🔢 Jumlah kode station ditemukan: {len(id_station)}")
    break  # hentikan setelah iterasi pertama

for x_station, station in enumerate(id_station, start=1):    
    url_station = f"https://mesowest.utah.edu/cgi-bin/droman/station_total.cgi?stn={station}&unit=0"
    print(f"➡️ [{x_station}] URL: {url_station}")
    response_station = requests.get(url_station, headers=headers, cookies=cookies)
    soup_station = BeautifulSoup(response_station.content, 'html.parser')

    station_name_td = soup_station.find("b", string="Station Name:")
    if station_name_td:
        station_value_name_td = station_name_td.find_parent("td").find_next_sibling("td")
        if station_value_name_td:
            station_name = station_value_name_td.get_text(strip=True)

    station_id_td = soup_station.find("b", string="Station ID:")
    if station_id_td:
        station_value_id_td = station_id_td.find_parent("td").find_next_sibling("td")
        if station_value_id_td:
            station_name_id = station_value_id_td.get_text(strip=True)
    
    print(f"🛰️ Station Name: {station_name}")
    print(f"🛰️ Station ID: {station_name_id}")