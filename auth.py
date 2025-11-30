import msal
import os
import json
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.environ["ONEDRIVE_CLIENT_ID"]
TENANT = "consumers"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT}"

SCOPES = [
    "Files.Read"
    ]

CACHE_FILE = "msal_cache.bin"
def get_access_token():
    #load cache if it exists
    cache = msal.SerializableTokenCache()
    
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())

    #create app with cache
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    result = None
    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    #failback to device login
    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        print(flow)
        result = app.acquire_token_by_device_flow(flow)

    #save cache for next run
    with open(CACHE_FILE, "w") as f:
        f.write(cache.serialize())

    if "access_token" in result:
        print("Authenticated (cache saved)")
    else:
        print("Auth failed: ", result)

    print("Scopes in token:", result.get("scope"))

    return result["access_token"]