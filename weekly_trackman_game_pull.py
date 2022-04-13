import pandas as pd
from ftplib import FTP
import datetime as DT

from trackman_utils import handle_trackman_file

# establish FTP connection
ftp = FTP('ftp.trackmanbaseball.com')   # connect to host, default port
ftp.login(user='Michigan', passwd='zW?pV5-tEf') # login

# filepath variables to be filled in
FILETYPE = 'CSV'
FILE_PATH = './v3/{}/{}/{}/{}'

today = DT.date.today() # todays date

# FIX HERE IF YOU WANT TO UPDATE FURTHER BACK
# list of the last 6 days to be inserted (including today)
l6d = [today - DT.timedelta(days=day) for day in range(0,6)]

# keep track of games inserted into DB
game_counter = 0
# clean up dates as strings for FTP
for day in l6d:

    if day.month < 10:
        month_clean = '0' + str(day.month)
    else:
        month_clean = str(day.month)

    if day.day < 10:
        day_clean = '0' + str(day.day)
    else: 
        day_clean = str(day.day)
    
    # Construct file path with dates
    filled_path = FILE_PATH.format(day.year, month_clean, day_clean, FILETYPE)
    # get all games listed 
    files = ftp.nlst(filled_path)

    # If no games for a given date
    if len(files) == 0:
        continue

    # Insert each game into DB
    for file in files:

    # insert only verified game files into DB
        if 'unverified' in file:
            continue

        handle_trackman_file(ftp, filled_path + "/" + file, practice=False)

        game_counter +=  1

print(f"{game_counter} games inserted from {min(l6d)} to {max(l6d)}")