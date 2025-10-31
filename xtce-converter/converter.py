import requests
import csv

sheet_id = "1Ukaums3NfbJdVOQL7E1QMyPNoQ7gD5Zxciiz4ucRUrk"
gid = "2140536820"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

response = requests.get(url)

if response.status_code == 200:
    with open("data.csv", "wb") as f:
        f.write(response.content)

with open("data.csv", newline="") as f:
    reader = csv.reader(f)
    headers = next(reader)[1:]
    rows = list(reader)

    parameterized_data = {header: [row[i] for row in rows if row[i] != ""]
        for i, header in enumerate(headers, start = 1)
        }