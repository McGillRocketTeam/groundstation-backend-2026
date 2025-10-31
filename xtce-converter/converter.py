import requests

sheet_id = "1Ukaums3NfbJdVOQL7E1QMyPNoQ7gD5Zxciiz4ucRUrk"
gid = "2140536820"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

response = requests.get(url)

if response.status_code == 200:
    with open("data.csv", "wb") as f:
        f.write(response.content)
