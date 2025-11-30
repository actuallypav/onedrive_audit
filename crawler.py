import requests
import csv
from auth import get_access_token

SESSION = requests.Session()
GRAPH = "https://graph.microsoft.com/v1.0"
TOKEN = get_access_token()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}


def list_children(item_id="root"):

    #gathering 999 as paginator likes to default to 200 (speeds things up)
    if item_id == "root":
        url = f"{GRAPH}/me/drive/root/children?$top=999"
    else:
        url = f"{GRAPH}/me/drive/items/{item_id}/children?$top=999"

    while url:
        r = SESSION.get(url, headers=HEADERS)
        print("CALLING:", r.url)
        r.raise_for_status()
        data = r.json()

        for item in data.get("value", []):
            yield item

        next_link = data.get("@odata.nextLink")
        url = next_link if next_link and "graph.microsoft.com" in next_link else None


def walk_drive(item_id="root", path=""):
    for item in list_children(item_id):
        name = item["name"]
        full_path = f"{path}/{name}".lstrip("/")

        if "folder" in item:
            yield from walk_drive(item["id"], full_path)
        else:
            yield {
                "id": item["id"],
                "path": full_path,
                "size": item.get("size", 0),
                "modified": item.get("lastModifiedDateTime"),
                "mime": item.get("file", {}).get("mimeType"),
                "ext": name.split(".")[-1].lower() if "." in name else ""
            }


files = list(walk_drive())

with open("drive_index.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=files[0].keys())
    writer.writeheader()
    writer.writerows(files)

print(f"Indexed {len(files)} files")
