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

def get_bus_lines(agency_url: str):
    """
    Calls the endpoint that returns the bus lines for a specific agency.
    The parameter must be the full agency URL (as returned by get_agencies()).
    """
    url = f"{TPL_BASE_URL}/bus-lines/"
    params = {"agency": agency_url}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()