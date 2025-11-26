import msal
import json

CLIENT_ID = ""
TENANT = "consumers"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT}"

SCOPES = [
    "Files.Read",
    "User.Read"
    ]

app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

flow = app.initiate_device_flow(scopes=SCOPES)
print(flow)

result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    with open("token.json", "w") as f:
        json.dump(result, f)
    print("Login successful — token saved.")
else:
    print(result)