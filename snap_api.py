import requests

# Base URL of the TPL portal
TPL_BASE_URL = "https://www.snap4city.org/superservicemap/api/v1/tpl"

def get_agencies():
    """
    Calls the endpoint that returns the bus agencies.
    """
    url = f"{TPL_BASE_URL}/agencies"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()