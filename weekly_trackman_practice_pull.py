import pandas as pd
from ftplib import FTP
import datetime as DT

from trackman_utils import handle_trackman_file

# establish FTP connection
ftp = FTP('ftp.trackmanbaseball.com')   # connect to host, default port
ftp.login(user='Michigan', passwd='zW?pV5-tEf')  

# Filepath global variables
FILETYPE = 'CSV'
DEVICE_NO = '21410004'

FILE_PATH = './practice/{}/{}/{}/{}/{}'
base_path = './practice/'

today = DT.date.today() # todays date

# FIX HERE IF YOU WANT TO UPDATE FURTHER BACK
# list of the last 6 days to be inserted (including today)
l6d = [today - DT.timedelta(days=day) for day in range(0,6)]

# keep track of games inserted into DB
game_counter = 0

for day in l6d:

    # clean up dates as strings for FTP
    if day.month < 10:
        month_clean = '0' + str(day.month)
    else:
        month_clean = str(day.month)

    if day.day < 10:
        day_clean = '0' + str(day.day)
    else: 
        day_clean = str(day.day)
    
    # Construct file path with dates
    filled_path = FILE_PATH.format(day.year, month_clean, day_clean, FILETYPE, DEVICE_NO)
    # get all games listed 
    files = ftp.nlst(filled_path)

    # If no games for a given date
    if len(files) == 0:
        continue

    # Insert each game into DB
    for file in files:

        handle_trackman_file(ftp, filled_path + "/" + file, practice=True)

        game_counter +=  1

print(f"{game_counter} practice sessions  inserted from {min(l6d)} to {max(l6d)}")