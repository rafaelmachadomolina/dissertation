#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 10:00:30 2022

@author: rafaelmachado
"""

# Import packages
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# Constants
EXCEL_PATH = 'excel/'
PARENT_PATH = os.path.normpath(os.getcwd() + os.sep + os.pardir)
TAXONOMY_PATH = PARENT_PATH + '/ingredient_taxonomy/' + EXCEL_PATH

# Import DB vars
DB_NAME_STAGE = os.environ['DB_NAME_STAGE']
DB_HOST_STAGE = os.environ['DB_HOST_STAGE']
DB_PORT_STAGE = os.environ['DB_PORT_STAGE']
DB_USERNAME_STAGE = os.environ['DB_USERNAME_STAGE']
DB_PASSWORD_STAGE = os.environ['DB_PASSWORD_STAGE']

TABLE_NAME = 'kp_ingredient_taxonomy'

STRING_CON = f'mysql+pymysql://{DB_USERNAME_STAGE}:{DB_PASSWORD_STAGE}@{DB_HOST_STAGE}:{DB_PORT_STAGE}/{DB_NAME_STAGE}'

# Define functions
def import_data_sql(df, string_conn, table_name = TABLE_NAME):
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
        df.to_sql(table_name,
                  string_conn,
                  index = False,
                  if_exists = 'append')
        print('Query successfully executed')

    except Exception as ex:   
        print(ex)

    finally:
        dbConnection.close()

# Read file
df_taxonomy_raw = pd.read_excel(EXCEL_PATH + 'taxonomy.xlsx', sheet_name = 'kafoodle_taxonomy')

# Create table template to db
df_taxonomy = df_taxonomy_raw[1].str.split(':', expand = True)
df_taxonomy.rename(columns = {0: 'category_id', 1: 'category_name'}, inplace = True)
df_taxonomy['category_id'] = pd.to_numeric(df_taxonomy['category_id'])

# Retrieve ingredient and path
df_ingredient = df_taxonomy_raw.copy()
df_ingredient[1] = df_ingredient[1].str.split(':', expand = True)[1]
df_ingredient[0] = df_ingredient[0].str.replace(' ', '-')
df_ingredient[0] = df_ingredient[0].str.lower()

list_taxonomy = df_ingredient.values.tolist()
list_taxonomy = [[j for j in i if j is not np.nan] for i in list_taxonomy]

list_ingredients = [i[-1] for i in list_taxonomy]
list_path = [':'.join(i[:-1]) for i in list_taxonomy]

# Merge df with lists
df_taxonomy['ingredient_name'] = list_ingredients
df_taxonomy['taxonomy'] = list_path

df_taxonomy = df_taxonomy[['ingredient_name', 'category_id', 'category_name', 'taxonomy']]

# Insert to db
import_data_sql(df_taxonomy, STRING_CON)
