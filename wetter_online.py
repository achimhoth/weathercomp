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
    headers = {'User-Agent': generate_user_agent(device_type="smartphone")}

    #Fetch url
    t0 = time.time()
    try:
        page_response = requests_retry_session().get(
            url, timeout=30, headers=headers
        )
    except Exception as x:
        print('It failed :(', x.__class__.__name__)
    else:
        print('It eventually worked', page_response.status_code)
    finally:
        t1 = time.time()
        print('Took', t1 - t0, 'seconds')

    #Create Soup
    page_content = BeautifulSoup(page_response.content, "html.parser")

    #Process Values
    max_temps_up = page_content.select('.daily.temperatures > div:nth-of-type(1) > span:nth-of-type(2)')
    min_temps_up = page_content.select('.daily.temperatures > div:nth-of-type(2) > span:nth-of-type(2)')
    sun_hours_up = page_content.select('.suntimes.sunicon')
    rain_props_up = page_content.select('.daily.elements > .pop')
    rain_amounts_up = page_content.select('.daily_weather.tooltips')

    for i in range(1, 16):
        try:
            parsed_json = json.loads(rain_amounts_up[i]["data-tt-args"])
            am = parsed_json["precipitation_amount"]
            if '-' in am:
                v1 = float(re.findall('(\d+,*\d*)-(\d+,*\d*)', am)[0][0].replace(',', '.'))
                v2 = float(re.findall('(\d+,*\d*)-(\d+,*\d*)', am)[0][1].replace(',', '.'))
                am = round(((v1 + v2) / 2), 2)
            rain_amounts.append(float(am))
        except:
            rain_amounts.append(None)

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
            rain_props.append(int(re.sub('[^0-9]','', rain_props_up[i].get_text())))
        except:
            rain_props.append(None)

    #Return Values
    return ( max_temps, min_temps, rain_props, rain_amounts, sun_hours )
