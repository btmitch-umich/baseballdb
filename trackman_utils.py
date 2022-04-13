import pandas as pd
import mysql.connector
import numpy as np
from sqlalchemy import create_engine


# insert duplicates workaround from https://github.com/pandas-dev/pandas/issues/15988
def table_column_names(table, cur) -> str:
    """
    Get column names from database table

    Parameters
    ----------
    table : str
        name of the table

    Returns
    -------
    str
        names of columns as a string so we can interpolate into the SQL queries
    """
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
    cur.execute(query)
    rows = cur.fetchall()
    dirty_names = [i[0] for i in rows]
    clean_names = '`' + '`, `'.join(map(str, dirty_names)) + '`'
    return clean_names

def insert_db(df, tablename):
    """Handles Database insertion given a tablename and a dataframe"""

    # setup credentials for connection
    hostname="webapps4-db.miserver.it.umich.edu"
    dbname="notitia"
    uname="notitia"
    pwd="B453B4lL_2018"

    mydb = mysql.connector.connect(
        host=hostname,
        user=uname,
        password=pwd,
        database=dbname
    )

    cur = mydb.cursor()
     # create a connection engine for pandas to_sql to use
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))

    temp_table = 'TEMP_TRACKMAN'

    try:
        # create temp table with new data
        df.to_sql(name = temp_table, con = engine, if_exists = 'replace', index = False)

        # get columns of temp table (same as existing table)
        columns = table_column_names(temp_table, cur)

        # Insert ignore from temp table into NCAA_trackman to prevent duplicates
        insert_query = f'INSERT IGNORE INTO {tablename}({columns}) SELECT {columns} FROM `{temp_table}`'
        cur.execute(insert_query)

    except Exception as e:
        print(e)

    # drop temp table
    drop_query = f'DROP TABLE IF EXISTS `{temp_table}`'
    cur.execute(drop_query)

    # commit
    mydb.commit()


def handle_trackman_file(ftp, fpath, practice=True):
    """Processes a file given an FTP connection and filepath"""

    # If function is called with path to a game file (pass practice=False)
    if practice==False:

        # open a temporary file to write file downloaded from FTP
        with open('./tmp/tmp_game.csv', "wb") as file:

            # Command for Downloading the file "RETR filename"
            ftp.retrbinary(f"RETR {fpath}", file.write)

        file.close()

        # read in written temp file
        df = pd.read_csv('./tmp/tmp_game.csv')

        # fill nans with None for MySQL
        df = df.replace({np.nan: None})

        # These column names have to be replaced for MySQL reasons
        df.rename(columns={'Top/Bottom': 'ToporBottom', 'System': 'Sys'}, inplace=True)

        # Get times into correct format
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

        insert_db(df, 'NCAA_trackman')

    # Practice Files
    else:

        # Pitching practice file sent to pitching table in DB
        if 'Pitching' in fpath:

            # open temp file to write download from FTP
            with open('./tmp/tmp_pitching.csv', "wb") as file:

                # Command for Downloading the file "RETR filename"
                ftp.retrbinary(f"RETR {fpath}", file.write)

            file.close()

            # read in data from temp file
            df = pd.read_csv('./tmp/tmp_pitching.csv')

            # Get times into correct format
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            insert_db(df, 'TRACKMAN_PRACTICE_PITCHING')

        # Hitting practice file sent to hitting table in DB
        elif 'Hitting' in fpath:

            # Open temp file to write downloaded hitting file
            with open('./tmp/tmp_hitting.csv', "wb") as file:

                # Command for Downloading the file "RETR filename"
                ftp.retrbinary(f"RETR {fpath}", file.write)

            file.close()

            # read in data from temp file
            df = pd.read_csv('./tmp/tmp_hitting.csv')

            # Get times into correct format
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

            insert_db(df, 'TRACKMAN_PRACTICE_HITTING')
