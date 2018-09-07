from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import requests
import unicodedata
import re
import json
import time
from utils.request_retry import requests_retry_session

def fetch_rain_props_and_amounts( soup ):
    rain_props_up = []
    rain_amounts_up = []
    count_helper = 0
    curr_rain_prop = 0
    curr_rain_amount = 0

    for i in range(0, len(soup)):
        txt = soup[i].get_text().replace(' ', '')

        if '%' in txt:
            prop = int(re.sub('\D', '', txt))
            if curr_rain_prop < prop:
                curr_rain_prop = prop

            if i < len(soup) - 1:
                n_txt = soup[i+1].get_text().replace(' ', '')
                if 'l/m' in n_txt:
                    am = float(re.findall('(\d+,*\d*)', n_txt)[0].replace(',','.'))
                    curr_rain_amount = curr_rain_amount + am

            count_helper = count_helper + 1
            if count_helper == 4:
                rain_props_up.append(curr_rain_prop)
                rain_amounts_up.append(round(curr_rain_amount,2))
                count_helper = 0
                curr_rain_prop = 0
                curr_rain_amount = 0

    return( rain_props_up, rain_amounts_up )

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
    max_temps_up = page_content.find_all(class_='wt-color-temperature-max')
    min_temps_up = page_content.find_all(class_='wt-color-temperature-min')
    sun_hours_up = page_content.select('.forecast-day-text')
    rain_props_and_amounts_soup = page_content.select('.forecast-column-rain > .wt-font-semibold')

    #Rain Props and Amounts need extra processing
    rain_props_and_amounts_up = fetch_rain_props_and_amounts(rain_props_and_amounts_soup)
    rain_props_up = rain_props_and_amounts_up[0]
    rain_amounts_up = rain_props_and_amounts_up[1]

    for i in range(1,15):
        try:
            rain_props.append(rain_props_up[i])
        except:
            rain_props.append(None)

    for i in range(1,15):
        try:
            rain_amounts.append(rain_amounts_up[i])
        except:
            rain_amounts.append(None)

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
            txt = sun_hours_up[i].get_text()
            hrs = re.findall('(\d+,*\d*) Sonnenstunden', txt)[0]
            sun_hours.append(hrs)
        except:
            sun_hours.append(None)

    #Return Values
    return ( max_temps, min_temps, rain_props, rain_amounts, sun_hours )
