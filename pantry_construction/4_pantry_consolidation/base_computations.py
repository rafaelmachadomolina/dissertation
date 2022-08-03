#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 12:00:13 2022

@author: rafaelmachado
"""

### Import libraries
import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import warnings
warnings.filterwarnings("ignore")

### Define constants
NUTRITION_TABLE = 'kp_ingredients_nutrition'
CATEGORY_TABLE = 'ste__ingredient_categories'
TAXONOMY_TABLE = 'kp_ingredient_taxonomy'
BI_TABLE = 'kp_bi_pantry_quality'

DATA_SOURCE = 'kafoodle_pantry'
PATH_PARQUET = 'parquet/'
PATH_CSV = 'csv/'

COL_GROUPS = {'index': ['ingredient_id', 'original_ingredient_name', 'matched_ingredient', 'matched_score', 'ingredient_category_id', 'taxonomy_category_id', 'nutrition_id', 'has_nutrition_data'],
              'prop_quantity': ['energy_quantity', 'fibre_quantity', 'protein_quantity', 'salt_quantity', 'fat_quantity', 'saturated_fat_quantity', 'carbohydrate_quantity', 'sugar_quantity'],
              'prop_unit': ['energy_unit', 'fibre_unit', 'protein_unit', 'salt_unit', 'fat_unit', 'saturated_fat_unit', 'carbohydrate_unit', 'sugar_unit'],
              'allergens': ['GLUTEN', 'GLUTEN_WHEAT', 'GLUTEN_RYE', 'GLUTEN_BARLEY', 'GLUTEN_OATS', 'CRUSTACEANS', 'EGGS', 'FISH', 'PEANUTS', 'SOYA', 'MILK', 'NUTS', 'NUTS_ALMONDS', 'NUTS_HAZELNUTS', 'NUTS_WALNUTS', 'NUTS_CASHEWS', 'NUTS_PECANS', 'NUTS_BRAZIL', 'NUTS_PISTACHIOS', 'NUTS_MACADAMIA', 'SESAME_SEEDS', 'SULPHUR_DIOXIDE', 'MOLLUSCS', 'CELERY', 'MUSTARD', 'LUPIN']}

TABULAR_COLS = ['product_name', 'category', 'gluten_wheat', 'gluten_rye',
                'gluten_barley', 'gluten_oats', 'crustaceans', 'eggs', 'fish',
                'peanuts', 'soya', 'milk', 'nuts_almonds', 'nuts_hazelnuts',
                'nuts_walnuts', 'nuts_cashews', 'nuts_pecans', 'nuts_brazil',
                'nuts_pistachios', 'nuts_macadamia', 'sesame_seeds',
                'sulphur_dioxide', 'molluscs', 'celery', 'mustard', 'lupin',
                'energy', 'fat', 'saturated', 'carbohydrate', 'fibre',
                'sugar', 'protein', 'salt']

DICT_ALLERGEN_ENCODE = {0: 'N', 1: 'Y'}

CONV_FACTORS = {'mg': 1.0/1000,
                'kj': 1.0/4.184}
CONV_UNITS = {'mg': 'g',
              'kj': 'kcal'}

### Define functions
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

def load_df_from_sql(tableName: str, string_conn: str):
    
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

def insert_data_sql(df, string_conn: str, table_name: str):

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
        
def filter_dataframe(df, threshold):
    
    df['matched_score'] = pd.to_numeric(df['matched_score'])
    
    return df[df['matched_score'] >= threshold];

def transform_dataframe(df, col_groups = COL_GROUPS, data_source: str = DATA_SOURCE):
    
    # Define id vars
    ID_VARS = ['ingredient_id', 'matched_ingredient']
    COLS_CONCAT = ID_VARS + ['property', 'value', 'unit', 'property_type']
    
    # Extract dataframes
    df_scores = df[COL_GROUPS['index']]
    df_quantity = df[COL_GROUPS['index'] + COL_GROUPS['prop_quantity']]
    df_unit = df[COL_GROUPS['index'] + COL_GROUPS['prop_unit']]
    df_allergen = df[COL_GROUPS['index'] + COL_GROUPS['allergens']]
    
    # Prepare match dataframe
    df_scores.rename(columns = {'matched_score': 'value'}, inplace = True)
    df_scores['property'] = 'score'
    df_scores['unit'] = None
    df_scores['property_type'] = 'score'
    
    # Unpivot dataframes
    df_quantity = pd.melt(df_quantity,
                          id_vars = ID_VARS,
                          value_vars = COL_GROUPS['prop_quantity'],
                          var_name = 'name',
                          value_name = 'value')
    df_unit = pd.melt(df_unit,
                      id_vars = ID_VARS,
                      value_vars = COL_GROUPS['prop_unit'],
                      var_name = 'name',
                      value_name = 'unit')
    df_allergen = pd.melt(df_allergen,
                          id_vars = ID_VARS,
                          value_vars = COL_GROUPS['allergens'],
                          var_name = 'property',
                          value_name = 'value')
    
    # Create dataframe with quantities and units
    df_quantity['property'] = df_quantity['name'].str.split('_', expand = True)[0]
    df_unit['property'] = df_unit['name'].str.split('_', expand = True)[0]
    
    df_properties = pd.merge(df_quantity,
                             df_unit,
                             how = 'left',
                             on = ID_VARS + ['property'])
    
    df_properties.dropna(inplace = True)
    df_properties['property_type'] = 'macro_nutrient'
    
    # Drop nulls and add empty units to allergens
    df_allergen.dropna(inplace = True)
    df_allergen['unit'] = None
    df_allergen['property_type'] = 'allergen'
    
    # Concat datasets
    df_scores = df_scores[COLS_CONCAT]
    df_properties = df_properties[COLS_CONCAT]
    df_allergen =df_allergen[COLS_CONCAT]
    
    df_out = pd.concat([df_scores, df_properties, df_allergen])
    df_out['value'] = pd.to_numeric(df_out['value'], errors = 'coerce')
    df_out['property'] = df_out['property'].str.lower()
    df_out['data_source'] = data_source
    df_out.reset_index(drop = True, inplace = True)
    
    return df_out;

def convert_units(df, conv_factors = CONV_FACTORS, conv_units = CONV_UNITS):
    
    COLS = df.columns.tolist()
    df_return = df.copy()
    
    # Make conversions
    df_return['conv_factor'] = df_return['unit'].map(CONV_FACTORS)
    df_return['new_value'] = df_return['value'] * df_return['conv_factor']
    df_return['new_unit'] = df_return['unit'].map(conv_units)
    
    # Replace values
    df_return.loc[df_return['conv_factor'].notnull(), 'value'] = df_return['new_value']
    df_return.loc[df_return['conv_factor'].notnull(), 'unit'] = df_return['new_unit']
    
    return df_return[COLS];

def rank_df(df):
    
    df_rank = df.copy()
    
    df_rank['rank'] = df_rank.groupby(['matched_ingredient', 'property'])['value'].rank(method='first')
    
    return df_rank;
    
def compute_long_dataframe(df, threshold: float):
    
    # Retain only high matched rows
    df_filtered = filter_dataframe(df, threshold)
    
    # Transform dataframe
    df_transformed = transform_dataframe(df_filtered)
    df_transformed_units = convert_units(df_transformed)
    df_rank = rank_df(df_transformed_units)
    
    return df_rank;

def compute_mad(df_main, df_reference, cols):
    
    df_mad = pd.merge(df_main, df_reference[['reference_value']], how = 'left',
                           left_on = cols, right_index = True)
    df_mad['absolute_deviation'] = np.abs(df_mad['reference_value'] - df_mad['value'])
    
    df_mad = df_mad[cols + ['absolute_deviation']].groupby(cols).agg(['size', 'sum']).droplevel(0, axis = 1)
    df_mad['mean_absolute_deviation'] = df_mad['sum'] / (df_mad['size'] - 1)
    df_mad.loc[df_mad['size'] == 1, 'mean_absolute_deviation'] = 0
    
    return df_mad;

def compute_mean_properties(df):
    
    # Define constants
    GROUP_COLS = ['matched_ingredient', 'property_type', 'property']
    RELEVANT_COLS = GROUP_COLS + ['value']
    
    # Filter irrelevant columns out
    df_compute = df[RELEVANT_COLS]
    
    # Slice datased
    df_mean = df_compute[df_compute['property_type'] == 'score']
    df_median = df_compute[df_compute['property_type'] == 'macro_nutrient']
    df_mode = df_compute[df_compute['property_type'] == 'allergen']
    
    # Summarise datasets
    df_mean_grouped = df_mean.groupby(GROUP_COLS).agg(['size', 'mean']).droplevel(0, axis = 1)
    df_mean_grouped.rename(columns = {'size': 'n_rows', 'mean': 'reference_value'}, inplace = True)
    
    df_median_grouped = df_median.groupby(GROUP_COLS).agg(['size', 'median']).droplevel(0, axis = 1)
    df_median_grouped.rename(columns = {'size': 'n_rows', 'median': 'reference_value'}, inplace = True)
    
    df_mode_grouped = df_mode.groupby(GROUP_COLS).agg(['size', 'median']).droplevel(0, axis = 1)
    df_mode_grouped.rename(columns = {'size': 'n_rows', 'median': 'reference_value'}, inplace = True)
    
    # Compute mean absolute deviation
    df_mean_mad = compute_mad(df_mean, df_mean_grouped, GROUP_COLS)
    df_median_mad = compute_mad(df_median, df_median_grouped, GROUP_COLS)  
    df_mode_mad = compute_mad(df_mode, df_mode_grouped, GROUP_COLS)  
    
    # Merge deviations
    df_mean_grouped_merge = pd.merge(df_mean_grouped, df_mean_mad[['mean_absolute_deviation']], how = 'left', left_index = True, right_index = True)
    df_median_grouped_merge = pd.merge(df_median_grouped, df_median_mad[['mean_absolute_deviation']], how = 'left', left_index = True, right_index = True)
    df_mode_grouped_merge = pd.merge(df_mode_grouped, df_mode_mad[['mean_absolute_deviation']], how = 'left', left_index = True, right_index = True)
    
    # Concat and return
    df_return = pd.concat([df_mean_grouped_merge, df_median_grouped_merge, df_mode_grouped_merge])
    df_return.reset_index(inplace = True)
    
    return df_return;

def get_tabular_data(df, df_categories, df_taxonomy, order_cols = TABULAR_COLS, dict_allergen_encode = DICT_ALLERGEN_ENCODE):

    # Process long dataframe
    df_long = df[['matched_ingredient', 'property_type', 'property', 'reference_value']]
    df_long.rename(columns = {'matched_ingredient': 'product_name'}, inplace = True)
    df_long.loc[df_long['property_type'] == 'allergen', 'reference_value'] = np.ceil(df_long['reference_value'])
    
    # Names of allergen ingredients
    list_allergens = df[df['property_type'] == 'allergen']['property'].unique()

    # Pivot table
    df_properties_tabular = pd.pivot_table(df_long,
                                           index = 'product_name',
                                           values = 'reference_value',
                                           columns = ['property'],
                                           aggfunc = 'sum').reset_index()
    
    # Encode allergens
    for COL in list_allergens:
        df_properties_tabular[COL] = df_properties_tabular[COL].map(dict_allergen_encode)
    
    # Process complementary tables
    df_taxonomy_mid = df_taxonomy[['ingredient_name', 'category_id']].rename(columns = {'ingredient_name': 'product_name'})
    df_cats = df_categories[['id', 'name']].rename(columns = {'id': 'category_id', 'name': 'category'})
    
    # Merge with tables
    df_properties = pd.merge(df_properties_tabular, df_taxonomy_mid, how = 'left', on = 'product_name')
    df_properties = pd.merge(df_properties, df_cats, how = 'left', on = 'category_id')
    
    return df_properties[order_cols];

########################## Execute script ##########################

# Define connection
string_conn = generate_string_connection()

# Retrieve table
df_raw = load_df_from_sql(NUTRITION_TABLE, string_conn)
df_categories = load_df_from_sql(CATEGORY_TABLE, string_conn)
df_taxonomy = load_df_from_sql(TAXONOMY_TABLE, string_conn)

# Compute long dataframes for comparison
df_75 = compute_long_dataframe(df_raw, 0.75)
df_80 = compute_long_dataframe(df_raw, 0.80)

# Compute mean properties
df_properties_75 = compute_mean_properties(df_75)
df_properties_80 = compute_mean_properties(df_80)

# Pivot properties dataframe
df_properties_tabular = get_tabular_data(df_properties_80, df_categories, df_taxonomy)

# Save long df to parquet
# df_properties_75.to_parquet(f'{PATH_PARQUET}pantry_data_threshold_75.parquet', index = False)
# df_properties_80.to_parquet(f'{PATH_PARQUET}pantry_data_threshold_80.parquet', index = False)

# Save tabular data to parquet
# df_properties_tabular.to_parquet(f'{PATH_PARQUET}pantry_data_tabular.parquet', index = False)

# Insert dataframe to database for BI purposes
df_bi_properties = pd.merge(df_properties_80,
                            df_taxonomy[['id', 'ingredient_name']],
                            how = 'left',
                            left_on = 'matched_ingredient',
                            right_on = 'ingredient_name')

df_bi_properties.rename(columns = {'id': 'matched_ingredient_id',
                                   'n_rows': 'number_data_points'}, inplace = True)

df_bi_properties.drop(columns = ['matched_ingredient', 'ingredient_name'], inplace = True)
df_bi_properties['data_source'] = DATA_SOURCE

# insert_data_sql(df_bi_properties, string_conn, BI_TABLE)

# Combine to a single source
df_bi_properties_complete = pd.merge(df_bi_properties,
                                     df_taxonomy[['id', 'ingredient_name', 'category_id']],
                                     how = 'left',
                                     left_on = 'matched_ingredient_id',
                                     right_on = 'id')

df_bi_properties_complete.drop(columns = ['matched_ingredient_id', 'id'], inplace = True)

df_bi_properties_complete = pd.merge(df_bi_properties_complete,
                                     df_categories[['id', 'name']],
                                     how = 'left',
                                     left_on = 'category_id',
                                     right_on = 'id')

df_bi_properties_complete.drop(columns = ['category_id', 'id'], inplace = True)

# Save BI tables copy
# df_bi_properties.to_csv(f'{PATH_CSV}bi_properties.csv', index = False)
# df_taxonomy.to_csv(f'{PATH_CSV}taxonomy.csv', index = False)
# df_categories.to_csv(f'{PATH_CSV}categories.csv', index = False)
# df_bi_properties_complete.to_csv(f'{PATH_CSV}full_table.csv', index = False)