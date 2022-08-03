#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 16 17:39:46 2022

@author: rafaelmachado
"""

import os
import pandas as pd
from sqlalchemy import create_engine

# Set constants
CSV_PATH = 'csv/'

# Import DB vars
DB_NAME_PROD = os.environ['DB_NAME_PROD']
DB_HOST_PROD = os.environ['DB_HOST_PROD']
DB_PORT_PROD = os.environ['DB_PORT_PROD']
DB_USERNAME_PROD = os.environ['DB_USERNAME_PROD']
DB_PASSWORD_PROD = os.environ['DB_PASSWORD_PROD']

# Define functions
def extract_data_sql(query, string_conn):
    '''
    Executes a query and stores result in pandas DataFrame

    Parameters
    ----------
    query : SQL string
        Query to be executed in the database. Must follow SQL format.
    string_conn : string
        String containing connection protocol to database.

    Returns
    -------
    DataFrame
        Dataframe containing query results.

    '''
    
    sqlEngine = create_engine(string_conn)
    dbConnection = sqlEngine.connect()
    
    try:
        df = pd.read_sql(query, dbConnection)
        print('Query successfully executed')
        return df;

    except Exception as ex:   
        print(ex)

    finally:
        dbConnection.close()
        
# Read query file
with open('historic_imports.sql', 'r') as F:
    sql_query = F.read()
    
# Read data
STRING_CON = f'mysql+pymysql://{DB_USERNAME_PROD}:{DB_PASSWORD_PROD}@{DB_HOST_PROD}:{DB_PORT_PROD}/{DB_NAME_PROD}'

df_ingredients = extract_data_sql(sql_query, STRING_CON)

# Parse dates and ints
df_ingredients['cutoff_date'] = pd.to_datetime(df_ingredients['created_date'])
df_ingredients['cutoff_date'] = df_ingredients['cutoff_date'].dt.strftime('%Y-%m-01')
df_ingredients['category_id'] = df_ingredients['category_id'].map(int, na_action = 'ignore')

# Group to month
AGG_COLS = ['cutoff_date', 'category_id', 'category']
df_ingredients_agg = df_ingredients[AGG_COLS].groupby(AGG_COLS, as_index = False).size()
df_ingredients_agg.rename(columns = {'size': 'qnt_ingredients'}, inplace = True)
df_ingredients_agg['category_id'] = df_ingredients_agg['category_id'].map(int, na_action = 'ignore')

# Write file
with open(CSV_PATH + 'ingredient_timeseries.csv', 'w') as F:
    df_ingredients_agg.to_csv(F,
                              index = False,
                              sep = ';')
