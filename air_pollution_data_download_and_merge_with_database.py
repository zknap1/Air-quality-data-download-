
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import os
from datetime import datetime
import json
import pandas as pd
import shutil
import sys


# load configuration file
try:
    config = open('configuration_file.json', encoding='utf8', errors='ignore')
    config_dict = json.load(config)
except FileNotFoundError:
    print('The file configuration_file.json was not found.')
except:
    print('The file configuration_file.json could not be opened.')


path = config_dict['csv_files_path']
database_path = config_dict['database_path_daily']
database_backup_path = config_dict['database_backup_path_daily']
url = config_dict['url_link']

if not os.path.exists(path):
    print('The path for CSV files in configuration file does not exist.')
    sys.exit()
if not os.path.exists(database_path):
    print('The database path in configuration file does not exist.')
    sys.exit()

min_year = config_dict['min_year']

# create list containing years to consider
currentDateTime = datetime.now()
date = currentDateTime.date()
year = int(date.strftime("%Y"))

years = []
for i in range(int(min_year), year+1):
    years.append(str(i))

# open url and save links to all csv files

html = urlopen(url).read()
soup = BeautifulSoup(html, features="html.parser")

if os.path.exists("weblinks.txt"):
    os.remove("weblinks.txt")


with open('weblinks.txt', 'a') as f:
    f.write(str(soup))


weblinks = []
for line in open('weblinks.txt', 'r'):
    if line != "\n":
        weblinks.append(line.replace('\n', ''))

# download csv files
for y in years:
    for i in weblinks:
        if i.__contains__(y):
            urlretrieve(
                i, path+str(i.split('/')[-1]))


# create table and merge it with database

date_list = []
concentration_list = []

for folder, subfolder, file in os.walk(path):
    for filename in file:
        # nacitanie dat
        df = pd.read_csv(os.path.join(folder, filename))

        df['Date'] = pd.to_datetime(df['DatetimeBegin'])
        df['Date'] = df['Date'].dt.date

        date_list = [df['Date'][i] for i in range(df.shape[0])]
        concentration_list = [df['Concentration'][i]
                              for i in range(df.shape[0])]


data_tuples = list(zip(date_list, concentration_list))

df_total = pd.DataFrame(data_tuples, columns=[
                        'Date', 'air_pollution_average_concentration'])

df_avg = df_total['air_pollution_average_concentration'].groupby(
    df_total['Date']).mean().reset_index()

df_avg['Date'] = pd.to_datetime(df_avg['Date'])

df_import = pd.read_excel(database_path)

df_final = pd.merge(df_import, df_avg, on='Date', how='left')


# create backup of excel file
shutil.copyfile(database_path, database_backup_path)

# save updated table to excel
datatoexcel = pd.ExcelWriter(database_path)

df_final.to_excel(datatoexcel, index=False)

datatoexcel.save()
