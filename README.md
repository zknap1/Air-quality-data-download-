# Downloading air quality data

Select the correct options at https://discomap.eea.europa.eu/map/fme/AirQualityExport.htm and paste request URL to the configuration file. Update 'min_year' in configuration file with the minimum year. 'csv_files_path' contains path to the folder where csv files will be downloaded, 'database_path_daily' and 'database_backup_path_daily' contain paths to excel files.

Requirements:
bs4==0.0.1
urllib3==1.26.2
pandas==1.4.2
