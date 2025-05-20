# import os
# from bs4 import BeautifulSoup

# # Ganti dengan path file lokal kamu
# HTML_FILE = "data/index.html"


# def get_html_from_file(file_path):
#     """Membaca HTML dari file lokal"""
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             return f.read()
#     except Exception as e:
#         print(f"❌ Gagal membaca file {file_path}: {e}")
#         return None

# def parse_station_info_table(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     data = []

#     wrapper = soup.find('div', id='active_wrapper')
#     if not wrapper:
#         print("❌ <div id='active_wrapper'> tidak ditemukan.")
#         return data

#     table = wrapper.find('table')
#     if not table:
#         print("❌ Tabel tidak ditemukan dalam <div id='active_wrapper'>.")
#         return data

#     rows = table.find_all('tr')
#     for row in rows:
#         cols = row.find_all('td')
#         if not cols:
#             continue

#         try:
#             link_tag = cols[0].find('a')
#             station_name = link_tag.get_text(strip=True) if link_tag else ""
#             station_link = link_tag['href'] if link_tag else ""

#             row_data = {
#                 # "Station Link": station_link,
#                 "Station Name": station_name,
#                 "Code": cols[1].get_text(strip=True),
#                 "Full Name": cols[2].get_text(strip=True),
#                 "County": cols[3].get_text(strip=True),
#                 "Date": cols[4].get_text(strip=True),
#                 "Latitude": cols[5].get_text(strip=True),
#                 "Longitude": cols[6].get_text(strip=True),
#                 "Elevation": cols[7].get_text(strip=True),
#                 "UTC Offset": cols[8].get_text(strip=True)
#             }
#             data.append(row_data)
#         except IndexError:
#             print("⚠️ Kolom tidak lengkap di baris ini.")
#             continue

#     return data


# def extract_data_from_url(html, source=None):
#     """Menampilkan hasil data yang diambil dari HTML"""
#     station_data = parse_station_info_table(html)
#     print(station_data)

# def main():
#     html = get_html_from_file(HTML_FILE)
#     if not html:
#         print("❌ Gagal membaca HTML dari file lokal.")
#         return

#     extract_data_from_url(html, HTML_FILE)

# if __name__ == "__main__":
#     main()


import os
import csv
from bs4 import BeautifulSoup

# Ganti dengan path file lokal kamu
HTML_FILE = "data/index.html"
CSV_FILE = "data/South Dakota State University-inactive_wrapper.csv"  # File hasil CSV


def get_html_from_file(file_path):
    """Membaca HTML dari file lokal"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Gagal membaca file {file_path}: {e}")
        return None


def parse_station_info_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    wrapper = soup.find('div', id='inactive_wrapper')
    if not wrapper:
        print("❌ <div id='active_wrapper'> tidak ditemukan.")
        return data

    table = wrapper.find('table')
    if not table:
        print("❌ Tabel tidak ditemukan dalam <div id='active_wrapper'>.")
        return data

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if not cols or len(cols) < 10:
            continue

        try:
            # Kolom pertama bisa berisi <a> atau hanya teks
            link_tag = cols[0].find('a')
            if link_tag:
                station_name = link_tag.get_text(strip=True)
                station_link = link_tag['href']
            else:
                station_name = cols[0].get_text(strip=True)
                station_link = ""

            row_data = {
                # "Station Link": station_link,
                "Station Name": station_name,
                "Full Name": cols[2].get_text(strip=True),
                "Station ID": cols[1].get_text(strip=True),
                "County": cols[3].get_text(strip=True),
                "Date Start": f"'{cols[4].get_text(strip=True)}",
                "Date End": f"'{cols[5].get_text(strip=True)}",
                "Latitude": f"'{cols[6].get_text(strip=True)}",
                "Longitude": f"'{cols[7].get_text(strip=True)}",
                "Elevation": f"'{cols[8].get_text(strip=True)}",
                "UTC Offset": f"'{cols[9].get_text(strip=True)}"
            }
            # row_data = {
            #     # "Station Link": station_link,
            #     "Station Name": station_name,
            #     "Full Name": cols[2].get_text(strip=True),
            #     "Station ID": cols[1].get_text(strip=True),
            #     "County": cols[3].get_text(strip=True),
            #     "Date": f"'{cols[4].get_text(strip=True)}",
            #     "Latitude": f"'{cols[5].get_text(strip=True)}",
            #     "Longitude": f"'{cols[6].get_text(strip=True)}",
            #     "Elevation": f"'{cols[7].get_text(strip=True)}",
            #     "UTC Offset": f"'{cols[8].get_text(strip=True)}"
            # }
            data.append(row_data)
        except IndexError:
            print("⚠️ Kolom tidak lengkap di baris ini.")
            continue

    return data

def save_to_csv(data, filename):
    """Menyimpan data ke file CSV"""
    if not data:
        print("❌ Tidak ada data yang akan disimpan.")
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    headers = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Data berhasil disimpan ke {filename}")


def extract_data_from_url(html, source=None):
    """Memproses dan menyimpan data ke CSV"""
    station_data = parse_station_info_table(html)
    if station_data:
        save_to_csv(station_data, CSV_FILE)


def main():
    html = get_html_from_file(HTML_FILE)
    if not html:
        print("❌ Gagal membaca HTML dari file lokal.")
        return

    extract_data_from_url(html, HTML_FILE)


if __name__ == "__main__":
    main()
