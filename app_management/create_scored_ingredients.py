#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to compute matching scores for reference. Script is based on extract_ingredients.sql query.
"""

# Import modules
import os
import config_env
import kafoodle_pantry as kp

import warnings
warnings.filterwarnings('ignore')

# Define constants
PATH_SQL = 'sql/'
MATCHED_INGREDIENTS_SQL_TABLE = 'pantry__ingredients_scored'
TAXONOMY_VECTOR_SQL_TABLE = 'pantry__taxonomy_vector'
STOPWORDS_SQL_TABLE = 'pantry__stopwords'

QUERY_FILENAME = config_env.EXTRACT_INGREDIENTS_QUERY_FILENAME
STRING_CONN = config_env.get_mysql_uri()

#############################################################
###################### Execute script #######################
#############################################################

print('\nBeginning script execution...')

# Load query
try:
    PATH = os.path.join(PATH_SQL, QUERY_FILENAME)

    with open(f'{PATH}.sql', 'r') as F:
        query = F.read()

except:
    raise FileNotFoundError('There was an error loading the query. Please try again.')

# Extract data from query
df_ingredients = kp.retrieve_sql_query(query, STRING_CONN)

# Retrieve vectoried taxonomy and stopwords
df_vect_taxonomy = kp.retrieve_sql_table(TAXONOMY_VECTOR_SQL_TABLE, STRING_CONN)
df_stopwords = kp.retrieve_sql_table(STOPWORDS_SQL_TABLE, STRING_CONN)

# Prepare stopwords
list_stopwords = df_stopwords['stopword'].tolist()

# Prepare list of ingredients
list_ingredients = df_ingredients['ingredient_name'].tolist()
list_ingredients = kp.remove_all_special_chars(list_ingredients)
list_ingredients = kp.remove_double_spaces(list_ingredients)
list_ingredients = kp.remove_stopwords(list_ingredients, list_stopwords)

array_vector_ingredients = kp.vectorise_ingredients(list_ingredients)

# Prepare taxonomy
array_vector_taxonomy = kp.extract_taxonomy_from_df(df_vect_taxonomy)
list_taxonomy_ids = df_vect_taxonomy['taxonomy_id'].tolist()

# Match ingredients
list_matched_ingredients, list_matched_scores = kp.compute_scores(array_vector_ingredients, array_vector_taxonomy, list_taxonomy_ids)

# Build final result
df_ingredients_scored = df_ingredients.copy()
df_ingredients_scored['taxonomy_id'] = list_matched_ingredients
df_ingredients_scored['matched_score'] = list_matched_scores

# Insert to database
kp.insert_data_sql(df_ingredients_scored, STRING_CONN, MATCHED_INGREDIENTS_SQL_TABLE, append = False)

print('\nTable created succesfully! Script finalised.')