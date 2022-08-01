#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update the stopwords table in MySQL database.
Only manual step requires downloading the Google Sheets file with the provided link.
"""

# Import modules
import os
import pandas as pd
import config_env
import kafoodle_pantry as kp

# Define constants
PATH_CSV = 'csv/'
STOPWORDS_SQL_TABLE = 'pantry__stopwords'

CURRENT_PATH = os.getcwd()
GS_IDS = config_env.get_gs_params()
GS_STOPWORDS_ID = GS_IDS['GS_STOPWORDS_ID']
FILENAME = config_env.STOPWORDS_FILENAME
STRING_CONN = config_env.get_mysql_uri()

# Define functions
def preprocess_stopwords(df, column_name: str = 'stopword'):

    # From dataframe to list
    list_words = df[column_name].tolist()

    # Process lists
    list_processed = kp.remove_all_special_chars(list_words)
    list_processed = kp.remove_double_spaces(list_processed)

    # Flatten list
    list_split = [i.split(' ') for i in list_processed]
    list_flat = [i for list_semi in list_split for i in list_semi]

    # Create df and drop duplicates to return
    df_out = pd.DataFrame({column_name: list_flat})
    df_out.drop_duplicates(inplace = True)

    return df_out;

#############################################################
###################### Execute script #######################
#############################################################

print('\nBeginning script execution...')

# Create file URL
url_link = kp.retrieve_gs_link(GS_STOPWORDS_ID)

# Check if file exists
kp.check_file(FILENAME, url_link)

# Load data from csv file and SQL
df_from_file = kp.load_data_from_file(FILENAME)
df_current_stopwords = kp.retrieve_sql_table(STOPWORDS_SQL_TABLE, STRING_CONN)

# Preprocess stopwords
df_processed_stopwords = preprocess_stopwords(df_from_file)

# Process new stopwords
df_new_words = kp.identify_new_rows(df_processed_stopwords, df_current_stopwords, 'stopword')

# Check if new words are added
new_words = kp.check_new_records(df_new_words)

# Append to database if new records are found
if new_words:
    # Insert to database
    kp.insert_data_sql(df_new_words, STRING_CONN, STOPWORDS_SQL_TABLE)

    # Delete file
    kp.delete_file(FILENAME)

    print('\nScript finished succesfully!')

else:
    print('\nLooks like there are not any new words. Append was not executed.')
