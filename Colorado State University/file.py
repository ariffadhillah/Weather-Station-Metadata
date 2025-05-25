import requests

url = "https://coagmet.colostate.edu/data/metadata.json?units=m&instruments=yes&sponsors=yes"
response = requests.get(url)

with open("metadata_raw.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ File metadata_raw.txt berhasil disimpan.")
