from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import requests
import unicodedata
import re
from math import fmod
import json
import time
from utils.request_retry import requests_retry_session

def get_seven_day_detail(soup):
    seven_day_prop = []
    seven_day_am = []
    curr_prop = 0
    curr_am = 0
    for i in range(0, 28):
        txt = soup[i].get_text()
        txt = re.sub('[^a-zA-Z0-9%,]', '', txt)
        prop = int(re.findall('(\d+)%', txt)[0])
        try:
            am = re.findall('(\d+,*\d*)lm', txt)[0]
            am = float(am.replace(',','.'))
        except:
            am = 0

        if curr_prop < prop:
            curr_prop = prop
        curr_am = curr_am + am

        if fmod(i+1,4) == 0 or i == 27:
            seven_day_am.append(round(curr_am,2))
            seven_day_prop.append(curr_prop)
            curr_prop = 0
            curr_am = 0

    return(seven_day_prop, seven_day_am)

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
    else:
        print('It eventually worked', page_response.status_code)
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
    seven_day_detail_up = page_content.select('.pack__item.weather-strip__3.nowrap > div:nth-of-type(1)')

    #Get details fpor 7 days (better precip prop/amount)
    seven_day_detail = get_seven_day_detail(seven_day_detail_up)

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
            try:
                rain_props.append(seven_day_detail[0][i])
                rain_amounts.append(seven_day_detail[1][i])
            except:
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
