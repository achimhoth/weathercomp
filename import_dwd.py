import csv
from urllib.request import urlopen
import zipfile
import os
import mysql.connector
import datetime

urls = [
{'city': 'Frankfurt', 'url': 'ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_01420_akt.zip'},
{'city': 'Biberach', 'url': 'ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_04189_akt.zip'},
{'city': 'Hannover', 'url': 'ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_02014_akt.zip'},
{'city': 'Berlin', 'url': 'ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_00433_akt.zip'},
{'city': 'Muenchen', 'url': 'ftp://ftp-cdc.dwd.de/pub/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_03379_akt.zip'}
]

# check for extraction directories existence
if not os.path.isdir('downloaded'):
    os.makedirs('downloaded')

if not os.path.isdir('extracted'):
    os.makedirs('extracted')

def download_extract_zip(city, url):
    outputFilename = "downloaded/"+city+".zip"
    response = urlopen(url)
    zippedData = response.read()

    # save data to disk
    print('Saving to ' + outputFilename)
    output = open(outputFilename,'wb')
    output.write(zippedData)
    output.close()

    # extract the data
    zfobj = zipfile.ZipFile(outputFilename)
    for name in zfobj.namelist():
        if 'produkt_klima_tag' in name:
            uncompressed = zfobj.read(name)
            uncompressed_string = uncompressed.decode("utf-8")
            uncompressed_string = uncompressed_string.replace(' ', '')
            uncompressed = uncompressed_string.encode()
            outputFilename = "extracted/" + city + '.csv'
            print('Saving extracted file to ' + outputFilename)
            output = open(outputFilename,'wb')
            output.write(uncompressed)
            output.close()

def dwd_mess_datum_to_date_string(dwd):
    if len(dwd) == 8:
        y = dwd[0:4]
        m = dwd[4:6]
        d = dwd[6:8]
        return y+'-'+m+'-'+d

def csv_to_mysql(city):
    print('Exporting ' + city + ' to MySQL')

    mydb = mysql.connector.connect(
      host="tombadil.mysql.pythonanywhere-services.com",
      user="tombadil",
      passwd="vialytics",
      database="tombadil$weather"
    )
    mycursor = mydb.cursor()

    with open('extracted/'+city+'.csv', 'r') as csvfile:
        fieldnames = ['station', 'date']
        reader = csv.DictReader(csvfile, delimiter=';')

        max_date = datetime.date(2018,8,1)

        for row in reader:
            temp_max = float(row['TXK'])
            temp_min = float(row['TNK'])
            sun_hours = float(row['SDK'])
            precip_amount = float(row['RSK'])
            date_string = dwd_mess_datum_to_date_string(row['MESS_DATUM'])

            #Only save younger than August 2018
            mess_datum = datetime.date(int(date_string.split('-')[0]),int(date_string.split('-')[1]),int(date_string.split('-')[2]))
            if mess_datum > max_date:
                sql = "INSERT INTO measurements (city, date, temp_max, temp_min, precip_amount, sun_hours) \
                    VALUES (%s, %s, %s, %s, %s, %s)\
                    ON DUPLICATE KEY UPDATE temp_max = %s, temp_min = %s, precip_amount = %s, sun_hours = %s"
                val = (city, date_string,
                    temp_max, temp_min, precip_amount, sun_hours,
                    temp_max, temp_min, precip_amount, sun_hours)
                mycursor.execute(sql, val)
                mydb.commit()

for url in urls:
    download_extract_zip(url['city'], url['url'])
    csv_to_mysql(url['city'])
