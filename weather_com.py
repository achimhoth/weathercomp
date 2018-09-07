from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import requests
import unicodedata
import re
import json
import time
from utils.request_retry import requests_retry_session

def fetch_city( url ):
    #Here's what we are looking for
    max_temps = []
    min_temps = []
    rain_props = []
    rain_amounts = []
    sun_hours = []

    #Set Headers and load page
    headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}

    #Fetch url
    t0 = time.time()
    try:
        page_response = requests_retry_session().get(
            url, timeout=30, headers=headers
        )
    except Exception as x:
        print('It failed :(', x.__class__.__name__)
    finally:
        t1 = time.time()
        print('Fetched in ', t1 - t0, 'seconds')

    #Create Soup
    page_content = BeautifulSoup(page_response.content, "html.parser")

    #Process Values
    max_temps_up = page_content.select('td.temp > div > span:nth-of-type(1)')
    min_temps_up = page_content.select('td.temp > div > span:nth-of-type(3)')
    rain_props_up = page_content.select('td.precip > div > span:nth-of-type(2)')

    for i in range(1, 15):
        try:
            max_temps.append(int(re.sub('[^0-9]','', max_temps_up[i].get_text())))
        except:
            max_temps.append(None)

    for i in range(1, 15):
        try:
            min_temps.append(int(re.sub('[^0-9]','', min_temps_up[i].get_text())))
        except:
            min_temps.append(None)

    for i in range(1, 15):
        try:
            rain_props.append(int(re.sub('[^0-9]','', rain_props_up[i].get_text())))
        except:
            rain_props.append(None)

    for i in range(1, 15):
        rain_amounts.append(None)
        sun_hours.append(None)

    #Return Values
    return ( max_temps, min_temps, rain_props, rain_amounts, sun_hours )
