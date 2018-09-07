import csv
import time
import wetter_com
import wetter_de
import wetter_online
import weather_com
from utils.send_mail import send_mail
from urls import weather_urls
from datetime import datetime
from datetime import timedelta
import mysql.connector

def write_data_to_db( req, data ):

    mydb = mysql.connector.connect(
      host="tombadil.mysql.pythonanywhere-services.com",
      user="tombadil",
      passwd="vialytics",
      database="tombadil$weather"
    )
    mycursor = mydb.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    for i in range(0, len(data[0])):
        date = datetime.now() + timedelta(days=i+1)
        pred_date = date.strftime("%Y-%m-%d")

        sql = "INSERT INTO predictions (service, city, curr_date, pred_date, \
            temp_max, temp_min, precip_prop, precip_amount, sun_hours) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)\
            ON DUPLICATE KEY UPDATE temp_max = %s, temp_min = %s, precip_prop = %s, precip_amount = %s, sun_hours = %s"
        val = (
            req["service"], req["city"], today, pred_date,
            data[0][i], data[1][i], data[2][i], data[3][i], data[4][i],
            data[0][i], data[1][i], data[2][i], data[3][i], data[4][i]
        )
        mycursor.execute(sql, val)
        mydb.commit()

for req in weather_urls:
    service = req["service"]

    try:
        print("Fetching " + req["city"] + " from service " + req["service"])

        if service == "wetter_com":
            data = wetter_com.fetch_city(req["url"])
        elif service == "wetter_de":
            data = wetter_de.fetch_city(req["url"])
        elif service == "wetter_online":
            data = wetter_online.fetch_city(req["url"])
        elif service == "weather_com":
            data = weather_com.fetch_city(req["url"])

        print("Fetched successfully");

        write_data_to_db(req, data)
        print("Saved to database")

        print("")
    except:
        print("Error fetching " + req["city"] + " from service " + req["service"])
        send_mail("Scraping Error", "Error fetching " + req["city"] + " from service " + req["service"])
        print("")

    time.sleep(1)
