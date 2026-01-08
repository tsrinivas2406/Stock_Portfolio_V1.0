# import pandas as pd
# import numpy as np
import requests
# using explicit imports to overcome the conflict with time module

import time as md_time
from datetime import time as dt_time
from datetime import datetime, timedelta


# Function to fetch mutual funds data
def get_mutual_funds():
    url = "https://api.mfapi.in/mf"
    response = requests.get(url)
    return response.json()

# Function to fetch historical data
def get_historical_data(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    return response.json()

## Disabled Code Below : Replaced with Enhanced Error Handling Code
# # Function to fetch latest NAV
# def get_latest_nav(scheme_code):
#     url = f"https://api.mfapi.in/mf/{scheme_code}/latest"
#     response = requests.get(url)
#     data = response.json()

#     # Extract the NAV value, convert it to a float, or return NaN if not found
#     nav = data.get('data', [{}])[0].get('nav', 'N/A')
    
#     try:
#         return float(nav)
#     except ValueError:
#         return float('nan')  # Return NaN if conversion fails

def get_latest_nav(code):
    try:
        url = f"https://api.mfapi.in/mf/{code}/latest"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        return float(data['data'][0]['nav'])

    except requests.exceptions.ConnectTimeout:
        print(f"Timeout connecting to API for code {code}")
        return None

    except Exception as e:
        print(f"Error fetching NAV for code {code}: {e}")
        return None   
     
### TEST Function and URL : 
# print(get_latest_nav(117560))
# https://api.mfapi.in/mf/{code}/latest
# https://api.mfapi.in/mf/117560/latest


# Enhanced error handling version
def get_scheme_name(code):
    try:
        url = f"https://api.mfapi.in/mf/{code}/latest"
        r = requests.get(url, timeout=10)

        # validate HTTP response
        if r.status_code != 200:
            print(f"HTTP ERROR {r.status_code} for scheme {code}")
            return "N/A"

        # try JSON decode safely
        try:
            j = r.json()
        except ValueError:
            print(f"JSON decode error for scheme {code} — response was: {r.text[:100]}")
            return "N/A"

        return j.get("meta", {}).get("scheme_name", "N/A")

    except Exception as e:
        print(f"get_scheme_name() Error for {code}: {e}")
        return "N/A"

### Resources 
### Daily NAV Download : https://www.amfiindia.com/spages/NAVAll.txt

### MFAPI Documentation : https://mfapi.in/docs/
mf_name = get_scheme_name(119467)
mf_nav = get_latest_nav(119467)
print(f"Mutual Fund Name: {mf_name}, Latest NAV: {mf_nav}")

