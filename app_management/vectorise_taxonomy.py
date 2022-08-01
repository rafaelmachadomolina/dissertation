#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update the taxonomy and vectorised taxonomy tables in MySQL database.
Only manual step requires downloading the Google Sheets file with the provided link.
"""

# Import modules
import numpy as np
np.set_printoptions(suppress = True, linewidth = None)

import pandas as pd
import config_env
import kafoodle_pantry as kp

import nltk
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
from nltk.stem import WordNetLemmatizer

import warnings
warnings.filterwarnings('ignore')

# Define constants
TAXONOMY_SQL_TABLE = 'pantry__taxonomy'
TAXONOMY_VECTOR_SQL_TABLE = 'pantry__taxonomy_vector'

STRING_CONN = config_env.get_mysql_uri()

# Define functions
def get_singulars(df):

    # Create lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Generate lists
    list_taxonomy = df['ingredient_name'].tolist()
    list_taxonomy = [i.split('-') for i in list_taxonomy]

    # Identify singulars
    list_taxonomy_singular = [[lemmatizer.lemmatize(j) for j in i] for i in list_taxonomy]
    list_taxonomy_singular = ['-'.join(i) for i in list_taxonomy_singular]

    # Create new df to return
    df_new = df.copy()
    df_new['ingredient_name_singular'] = list_taxonomy_singular

    return df_new;

#############################################################
###################### Execute script #######################
#############################################################

print('\nBeginning script execution...')

# Retrieve taxonomy table
df_taxonomy = kp.retrieve_sql_table(TAXONOMY_SQL_TABLE, STRING_CONN)
df_vector_taxonomy_ref = kp.retrieve_sql_table(TAXONOMY_VECTOR_SQL_TABLE, STRING_CONN)

# Compute singular forms
df_taxonomy_names = df_taxonomy[['id', 'ingredient_name']]
df_taxonomy_singular = get_singulars(df_taxonomy_names)

# Create long vector form
LIST_TO_CONCAT = [df_taxonomy_singular[['id', 'ingredient_name']], df_taxonomy_singular[['id', 'ingredient_name_singular']].rename(columns = {'ingredient_name_singular': 'ingredient_name'})]
df_taxonomy_long = pd.concat(LIST_TO_CONCAT, ignore_index = True)
df_taxonomy_long.drop_duplicates(inplace = True)

# Check new ingredients
df_new_ingredients = kp.identify_new_rows(df_taxonomy_long, df_vector_taxonomy_ref, 'ingredient_name')

# Vectorise sentences
list_names = df_new_ingredients['ingredient_name'].tolist()
array_vectorised_names = kp.vectorise_ingredients(list_names)

# Create table
list_vectorised_names = [np.array2string(i.round(5), precision = 5, separator = ',', floatmode = 'fixed') for i in array_vectorised_names]
list_vectorised_names = [i.replace('\n', '') for i in list_vectorised_names] # Remove line breaks
list_vectorised_names = [i.replace(' ', '') for i in list_vectorised_names] # Remove whitespace

df_new_ingredients['vector_representation'] = list_vectorised_names
df_new_ingredients.rename(columns = {'id': 'taxonomy_id'}, inplace = True)

# Check if new ingredients are added
new_ingredients = kp.check_new_records(df_new_ingredients)

# Append to database if new records are found
if new_ingredients:
    # Insert to database
    kp.insert_data_sql(df_new_ingredients, STRING_CONN, TAXONOMY_VECTOR_SQL_TABLE)

    print('\nEverything went well. See you around next time!')

else:
    print('\nLooks like there are not any new words. Append was not executed.')