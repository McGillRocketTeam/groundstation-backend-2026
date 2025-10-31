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
    rows = [row for row in reader]
    parameters = []

    for col in range(1, len(headers)+1):
        column = []
        for row in rows:
            if row[col] != "":
                column.append(row[col])
        parameters.append(column)

    parameterized_data = dict(zip(headers, parameters))
    print(parameterized_data)