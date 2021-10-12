import os 
import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import url

from .config import *


driver = '{ODBC Driver 17 for SQL Server}'
server= dbServer
database= dbName
username = sqldbUsername
password = sqldbPassword

connection_string = f'DRIVER={driver};SERVER={server};'
connection_string += f'DATABASE={database};'
connection_string += f'UID={username};'
connection_string += f'PWD={password}'


# create sqlalchemy engine connection URL
connection_url =  sqlalchemy.engine.url.URL(
    "mssql+pyodbc", query={"odbc_connect": connection_string})

def get_user_list(connection_url):
    engine = create_engine(connection_url, echo=False)
    con= engine.connect()
    user_table = pd.read_sql('app_user', con)
    valid_emails = user_table['email'].tolist()
    print(valid_emails)
    return valid_emails