#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update the taxonomy and vectorised taxonomy tables in MySQL database.
Only manual step requires downloading the Google Sheets file with the provided link.
"""

# Import modules
import os
import pandas as pd
import config_env
import kafoodle_pantry as kp

import warnings
warnings.filterwarnings('ignore')

# Define constants
PATH_CSV = 'csv/'
TAXONOMY_SQL_TABLE = 'pantry__taxonomy'
CATEGORIES_SQL_TABLE = 'ste__ingredient_categories'

CURRENT_PATH = os.getcwd()
GS_IDS = config_env.get_gs_params()
GS_TAXONOMY_ID = GS_IDS['GS_TAXONOMY_ID']
FILENAME = config_env.TAXONOMY_FILENAME
STRING_CONN = config_env.get_mysql_uri()

#############################################################
###################### Execute script #######################
#############################################################

print('\nBeginning script execution...')

# Create file URL
url_link = kp.retrieve_gs_link(GS_TAXONOMY_ID)

# Check if file exists
kp.check_file(FILENAME, url_link)

# Load data from csv file and SQL
df_from_file = kp.load_data_from_file(FILENAME)
df_current_taxonomy = kp.retrieve_sql_table(TAXONOMY_SQL_TABLE, STRING_CONN)
df_categories = kp.retrieve_sql_table(CATEGORIES_SQL_TABLE, STRING_CONN)

# Process new ingredients
df_new_ingredients = kp.identify_new_rows(df_from_file, df_current_taxonomy, 'ingredient_name')

# Add taxonomy to new ingredients
df_new_ingredients = pd.merge(df_new_ingredients,
                              df_categories,
                              how = 'left',
                              left_on = 'category_id',
                              right_on = 'id')

# Format current category name to adapt to taxonomy format
df_new_ingredients['name'] = df_new_ingredients['name'].str.replace(' & ', '-') # Replace ampersand with hyphen
df_new_ingredients['name'] = df_new_ingredients['name'].str.replace('(', '') # Eliminate left parenthesis
df_new_ingredients['name'] = df_new_ingredients['name'].str.replace(')', '') # Eliminate right parenthesis
df_new_ingredients['name'] = df_new_ingredients['name'].str.replace(',', '') # Eliminate commas
df_new_ingredients['name'] = df_new_ingredients['name'].str.lower() # Convert to lowercaps
df_new_ingredients['name'] = df_new_ingredients['name'].str.replace(' ', '-') # Replace whitespaces with hyphens

# Add taxonomy format
df_new_ingredients['new_taxonomy'] = 'kafoodle-pantry:' + df_new_ingredients['name']
df_new_ingredients.loc[df_new_ingredients['taxonomy'].notnull(), 'new_taxonomy'] = df_new_ingredients['new_taxonomy'] + ':'
df_new_ingredients['new_taxonomy'] = df_new_ingredients['new_taxonomy'] + df_new_ingredients['taxonomy'].fillna('')

df_new_ingredients = df_new_ingredients[['ingredient_name', 'category_id', 'new_taxonomy']]
df_new_ingredients.rename(columns = {'new_taxonomy': 'taxonomy'}, inplace = True)

# Check if new ingredients are added
new_ingredients = kp.check_new_records(df_new_ingredients)

# Append to database if new records are found
if new_ingredients:
    # Insert to database
    kp.insert_data_sql(df_new_ingredients, STRING_CONN, TAXONOMY_SQL_TABLE)

    # Delete file
    kp.delete_file(FILENAME)

    print('\nAppend finalised succesfully!')

else:
    print('\nLooks like there are not any new words. Append was not executed.')