from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import requests
import unicodedata
import re
from math import fmod
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
        print('Took', t1 - t0, 'seconds')

    #Create Soup
    page_content = BeautifulSoup(page_response.content, "html.parser")

    #Process Values
    max_temps_up = page_content.find_all(lambda tag: tag.name == 'span' and tag.get('class') == ['temp-max'])
    min_temps_up = page_content.find_all(lambda tag: tag.name == 'span' and tag.get('class') == ['temp-min'])
    sun_hours_up = page_content.select('.weather-grid-item > dl > dd:nth-of-type(2)')
    rain_props_up = page_content.select('.weather-grid-item > dl > dd:nth-of-type(1)')

    for i in range(1, 16):
        try:
            max_temps.append(int(re.sub('[^0-9]','', max_temps_up[i].get_text())))
        except:
            max_temps.append(None)

    for i in range(1, 16):
        try:
            min_temps.append(int(re.sub('[^0-9]','', min_temps_up[i].get_text())))
        except:
            min_temps.append(None)

    for i in range(1, 16):
        try:
            sun_hours.append(int(re.sub('[^0-9]','', sun_hours_up[i].get_text())))
        except:
            sun_hours.append(None)

    for i in range(1, 16):
        try:
            txt = re.sub(r'[^a-zA-Z0-9,/%]','', rain_props_up[i].get_text())
            rain_prop = int(txt[0:txt.index('%')])
            rain_props.append(rain_prop)

            if 'l/m' in txt:
                rain_amount = txt[txt.index('%')+1:txt.index('l/m')]
                rain_amount = rain_amount.replace(",", ".")
                rain_amounts.append(float(rain_amount))
            else:
                rain_amounts.append(float(0))
        except:
            rain_props.append(None)
            rain_amounts.append(None)

    #Return Values
    return ( max_temps, min_temps, rain_props, rain_amounts, sun_hours )
