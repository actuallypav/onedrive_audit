import requests
from auth import get_access_token

#test if drive exists and graph can access
t = get_access_token()
r = requests.get(
    "https://graph.microsoft.com/v1.0/me/drive/root/children",
    headers={"Authorization": f"Bearer {t}"}
)
print(r.status_code, r.text)
