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

def get_bus_routes(agency_url: str, line: str, geometry: bool = False):
    """
    Calls the endpoint that returns the routes for a specific bus line of an agency.
    Parameters:
    - agency_url: full agency URL
    - line: line name/number (as required by the API)
    - geometry: whether to include route geometry in the response
    """
    url = f"{TPL_BASE_URL}/bus-routes/"
    params = {"agency": agency_url, "line": line, "geometry": str(bool(geometry)).lower()}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_bus_stops(route_url: str, geometry: bool = False):
    """
    Calls the endpoint that returns the stops for a specific route.
    Parameters:
    - route_url: full route URL
    - geometry: whether to include stop geometry in the response
    """
    url = f"{TPL_BASE_URL}/bus-stops/"
    params = {"route": route_url, "geometry": str(bool(geometry)).lower()}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()