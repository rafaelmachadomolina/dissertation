#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 18:36:11 2022

@author: rafaelmachado

This script executes the matching algorithm between the taxonomy and incoming
ingredients. All data is extracted from the database, except the stopwords
used in the filtering stage (saved in a JSON file).
"""

# Import libraries
import os
import re
import json
import time
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timezone

from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer
SENTENCE_MODEL = SentenceTransformer('paraphrase-mpnet-base-v2')

# Define constants
RANDOM_SEED = 888
SAMPLE_SIZE = 5000
CUT_RATIO = 0.8

CSV_PATH = 'csv/'
JSON_PATH = 'json/'
PARQUET_PATH = 'parquet/'

FILENAME_RAW_TAXONOMY = 'raw_taxonomy'
FILENAME_RAW_INGREDIENTS = 'raw_ingredients'
FILENAME_RAW_INGREDIENTS_SAMPLE = 'raw_ingredients_sample'
FILENAME_STOPWORDS_JSON = 'stopwords'

SAVE_BACKUP = True
COMPUTE_SAMPLE = False

TARGET_TABLE_NAME = 'kp_ingredients_matched'

# Define functions
def get_datetime_str():

    now = datetime.now(tz = timezone.utc)
    
    date = now.strftime("%Y-%m-%d")
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    second = now.strftime("%S")
    
    return f'{date}-{hour}-{minute}-{second}';

def generate_string_connection():
    
    # Retrieve params from env
    DB_HOST = os.environ['DB_HOST_STAGE']
    DB_NAME = os.environ['DB_NAME_STAGE']
    DB_PORT = os.environ['DB_PORT_STAGE']
    DB_USERNAME = os.environ['DB_USERNAME_STAGE']
    DB_PASSWORD = os.environ['DB_PASSWORD_STAGE']
    
    # Create string
    string_conn = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    return string_conn;

def load_df_from_sql(tableName, string_conn):
    
    sqlEngine = create_engine(string_conn)
    dbConnection = sqlEngine.connect()
    
    try:
        df = pd.read_sql_table(tableName, dbConnection)
        print(f'Query successfully executed for table {tableName}')
        return df;

    except Exception as ex:   
        print(ex)

    finally:
        dbConnection.close();
        
def vectorise_sentence(sentence_list, MODEL = SENTENCE_MODEL):
    
    INIT_TIME = time.time()
    
    dict_return = {}
    array_vectors = MODEL.encode(sentence_list)
    
    dict_return['sentence'] = sentence_list
    dict_return['vector'] = array_vectors
    
    FINAL_TIME = time.time() - INIT_TIME
    print(f'Vectorisation finished. Total time: {FINAL_TIME:.2f} seconds')
    
    return dict_return;

def calculate_similarity(dict_taxonomy, dict_ingredients):

    # Calculate similarity
    array_similarity = cosine_similarity(dict_ingredients['vector'], dict_taxonomy['vector'])

    # Get best match
    best_score_idx = np.argmax(array_similarity, axis = 1)

    # Assign ingredient and score to df
    matched_ingredient = [dict_taxonomy['sentence'][i] for i in best_score_idx]
    matched_score = [array_similarity[i][j] for i, j in enumerate(best_score_idx)]

    dict_return = {'ingredient': dict_ingredients['sentence'],
                  'matched_ingredient': matched_ingredient,
                  'matched_score': matched_score}
    
    return dict_return;

def insert_data_sql(df, string_conn, table_name):

    sqlEngine = create_engine(string_conn)
    dbConnection = sqlEngine.connect()

    try:
        df.to_sql(table_name,
                  string_conn,
                  index = False,
                  if_exists = 'append')
        print(f'Query successfully executed. Data inserted into table {table_name}')

    except Exception as ex:
        print('There was an exception inserting new records. Maybe some are already in the table?\n\n')
        print(ex)

    finally:
        dbConnection.close()

########################## Execute script ##########################

# Generate string connection
STRING_CONNECTION = generate_string_connection()

# Import stopwords file
with open(os.path.join(JSON_PATH, f'{FILENAME_STOPWORDS_JSON}.json'), 'r') as F:
    dict_stopwords = json.load(F)

# Import SQL tables
df_raw_taxonomy = load_df_from_sql('kp_ingredient_taxonomy', STRING_CONNECTION)
df_raw_ingredients = load_df_from_sql('kp_ingredients_base_pantry', STRING_CONNECTION)

# Save back ups of training
NOW_STR = get_datetime_str()
if SAVE_BACKUP:
    df_raw_taxonomy.to_parquet(os.path.join(PARQUET_PATH, f'{NOW_STR}_{FILENAME_RAW_TAXONOMY}.parquet'),
                               index = False)
    df_raw_ingredients.to_parquet(os.path.join(PARQUET_PATH, f'{NOW_STR}_{FILENAME_RAW_INGREDIENTS}.parquet'),
                               index = False) #File format reduces from 4.4 MB (csv) to 1.3 MB (parquet)

    
# Generate sample of ingredients if argument is set
if COMPUTE_SAMPLE:
    df_raw_ingredients = df_raw_ingredients.sample(SAMPLE_SIZE, random_state = RANDOM_SEED)
    
    df_raw_ingredients.to_parquet(os.path.join(PARQUET_PATH, f'{NOW_STR}_{FILENAME_RAW_INGREDIENTS_SAMPLE}.parquet'),
                               index = False) #File format reduces from 4.4 MB (csv) to 1.3 MB (parquet)

# Create lists
list_taxonomy = df_raw_taxonomy['ingredient_name'].tolist()
list_ingredient = df_raw_ingredients['ingredient_name'].tolist()

# Pre-process ingredients
LIST_REMOVED_CHARS_INGREDIENTS = [re.sub(r'[^A-Za-z ]+', ' ', i) for i in list_ingredient] # Remove all but letters and spaces
LIST_REMOVED_CHARS_INGREDIENTS = [re.sub(r' +', ' ', i) for i in LIST_REMOVED_CHARS_INGREDIENTS] # Remove double spaces
LIST_REMOVED_CHARS_INGREDIENTS = [i.lower() for i in LIST_REMOVED_CHARS_INGREDIENTS] # lower caps

# Remove stopwords
LIST_DOUBLE_INGREDIENTS = [i.split(' ') for i in LIST_REMOVED_CHARS_INGREDIENTS]
LIST_DOUBLE_INGREDIENTS_SLICED = [[i for i in sublist if i not in dict_stopwords['stopwords']] for sublist in LIST_DOUBLE_INGREDIENTS]

# Reconstruct cleaned list
list_ingredients_clean = [' '.join(i).strip() for i in LIST_DOUBLE_INGREDIENTS_SLICED]

# Encode lists
dict_taxonomy = vectorise_sentence(list_taxonomy)
dict_ingredients_clean = vectorise_sentence(list_ingredients_clean)

dict_similarity = calculate_similarity(dict_taxonomy, dict_ingredients_clean)

# Consolidate dataframe with results
df_results = pd.DataFrame(dict_similarity)
df_results['ingredient_id'] = df_raw_ingredients['ingredient_id'].tolist()
df_results.rename(columns = {'ingredient': 'adapted_ingredient'}, inplace = True)

# Merge with remaining datasets
df_results = pd.merge(df_results,
                      df_raw_ingredients[['ingredient_id', 'category_id', 'ingredient_name']],
                      how = 'left',
                      on = 'ingredient_id')

df_results.rename(columns = {'category_id': 'ingredient_category_id',
                             'ingredient_name': 'original_ingredient_name'}, inplace = True)

df_results = pd.merge(df_results,
                      df_raw_taxonomy[['id', 'ingredient_name', 'category_id']],
                      how = 'left',
                      left_on = 'matched_ingredient',
                      right_on = 'ingredient_name')

df_results.rename(columns = {'id': 'taxonomy_ingredient_id',
                             'category_id': 'taxonomy_category_id'}, inplace = True)
df_results.drop(columns = 'ingredient_name', inplace = True)

# Export table to SQL
insert_data_sql(df_results, STRING_CONNECTION, TARGET_TABLE_NAME)





