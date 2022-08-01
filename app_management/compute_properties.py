#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create table with reference data based on matched ingredients.
Each one of 34 properties (per ingredient) follows a statistical approach.
"""

# Import modules
import os
import numpy as np
import pandas as pd
import config_env
import kafoodle_pantry as kp

import warnings
warnings.filterwarnings('ignore')

# Define constants
PATH_SQL = 'sql/'
PATH_CSV = 'csv/'
PROPERTIES_SQL_TABLE = 'pantry__taxonomy_ref_values'
SUMMARY_SQL_TABLE = 'pantry__summary'
TAXONOMY_SQL_TABLE = 'pantry__taxonomy'
CATEGORIES_SQL_TABLE = 'ste__ingredient_categories'

STRING_CONN = config_env.get_mysql_uri()
PROPERTIES_FILENAME = config_env.INGREDIENT_PROPERTIES_QUERY_FILENAME
BI_DATA_FILENAME = config_env.BI_DATA_FILENAME
CONV_FACTORS = config_env.CONV_FACTORS
CONV_UNITS = config_env.CONV_UNITS


THRESHOLD = 0.8
DATA_SOURCE = 'kafoodle_pantry'

COL_GROUPS = {'index': ['ingredient_id', 'taxonomy_id', 'matched_score', 'nutrition_id', 'has_nutrition_data'],
              'prop_quantity': ['energy_quantity', 'fibre_quantity', 'protein_quantity', 'salt_quantity', 'fat_quantity', 'saturated_fat_quantity', 'carbohydrate_quantity', 'sugar_quantity'],
              'prop_unit': ['energy_unit', 'fibre_unit', 'protein_unit', 'salt_unit', 'fat_unit', 'saturated_fat_unit', 'carbohydrate_unit', 'sugar_unit'],
              'allergens': ['GLUTEN', 'GLUTEN_WHEAT', 'GLUTEN_RYE', 'GLUTEN_BARLEY', 'GLUTEN_OATS', 'CRUSTACEANS', 'EGGS', 'FISH', 'PEANUTS', 'SOYA', 'MILK', 'NUTS', 'NUTS_ALMONDS', 'NUTS_HAZELNUTS', 'NUTS_WALNUTS', 'NUTS_CASHEWS', 'NUTS_PECANS', 'NUTS_BRAZIL', 'NUTS_PISTACHIOS', 'NUTS_MACADAMIA', 'SESAME_SEEDS', 'SULPHUR_DIOXIDE', 'MOLLUSCS', 'CELERY', 'MUSTARD', 'LUPIN']}

TABULAR_COLS = ['taxonomy_id', 'product_name', 'category', 'number_data_points',
                'energy', 'fat', 'saturated', 'carbohydrate', 'fibre',
                'sugar', 'protein', 'salt', 'gluten_wheat', 'gluten_rye',
                'gluten_barley', 'gluten_oats', 'crustaceans', 'eggs', 'fish',
                'peanuts', 'soya', 'milk', 'nuts_almonds', 'nuts_hazelnuts',
                'nuts_walnuts', 'nuts_cashews', 'nuts_pecans', 'nuts_brazil',
                'nuts_pistachios', 'nuts_macadamia', 'sesame_seeds',
                'sulphur_dioxide', 'molluscs', 'celery', 'mustard', 'lupin']

BI_COLS = ['taxonomy_id', 'property_type', 'property', 'n_rows', 'reference_value', 'mean_absolute_deviation', 'data_source', 'ingredient_name', 'category']

DICT_ALLERGEN_ENCODE = {0: 'N', 1: 'Y'}

# Define functions
def transform_dataframe(df, col_groups = COL_GROUPS, data_source: str = DATA_SOURCE):
    
    # Define id vars
    ID_VARS = ['ingredient_id', 'taxonomy_id']
    COLS_CONCAT = ID_VARS + ['property', 'value', 'unit', 'property_type']
    
    # Extract dataframes
    df_scores = df[col_groups['index']]
    df_quantity = df[col_groups['index'] + col_groups['prop_quantity']]
    df_unit = df[col_groups['index'] + col_groups['prop_unit']]
    df_allergen = df[col_groups['index'] + col_groups['allergens']]
    
    # Prepare match dataframe
    df_scores.rename(columns = {'matched_score': 'value'}, inplace = True)
    df_scores['property'] = 'score'
    df_scores['unit'] = None
    df_scores['property_type'] = 'score'
    
    # Unpivot dataframes
    df_quantity = pd.melt(df_quantity,
                          id_vars = ID_VARS,
                          value_vars = col_groups['prop_quantity'],
                          var_name = 'name',
                          value_name = 'value')
    df_unit = pd.melt(df_unit,
                      id_vars = ID_VARS,
                      value_vars = col_groups['prop_unit'],
                      var_name = 'name',
                      value_name = 'unit')
    df_allergen = pd.melt(df_allergen,
                          id_vars = ID_VARS,
                          value_vars = col_groups['allergens'],
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
    df_return['conv_factor'] = df_return['unit'].map(conv_factors)
    df_return['new_value'] = df_return['value'] * df_return['conv_factor']
    df_return['new_unit'] = df_return['unit'].map(conv_units)
    
    # Replace values
    df_return.loc[df_return['conv_factor'].notnull(), 'value'] = df_return['new_value']
    df_return.loc[df_return['conv_factor'].notnull(), 'unit'] = df_return['new_unit']
    
    return df_return[COLS];

def rank_df(df):
    
    df_rank = df.copy()
    
    df_rank['rank'] = df_rank.groupby(['taxonomy_id', 'property'])['value'].rank(method='first')
    
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
    GROUP_COLS = ['taxonomy_id', 'property_type', 'property']
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

    # Round values to 4 decimal places
    df_return['reference_value'] = np.round(df_return['reference_value'], 4)
    df_return['mean_absolute_deviation'] = np.round(df_return['mean_absolute_deviation'], 4)
    
    return df_return;

def get_tabular_data(df, df_categories, df_taxonomy, order_cols = TABULAR_COLS, dict_allergen_encode = DICT_ALLERGEN_ENCODE):

    # Process long dataframe
    df_long = df[['taxonomy_id', 'property_type', 'property', 'reference_value']]
    df_long.loc[df_long['property_type'] == 'allergen', 'reference_value'] = np.ceil(df_long['reference_value'])
    
    # Names of allergen ingredients
    list_allergens = df[df['property_type'] == 'allergen']['property'].unique()

    # Pivot table
    df_properties_tabular = pd.pivot_table(df_long,
                                           index = 'taxonomy_id',
                                           values = 'reference_value',
                                           columns = ['property'],
                                           aggfunc = 'sum').reset_index()
    
    # Encode allergens
    for COL in list_allergens:
        df_properties_tabular[COL] = df_properties_tabular[COL].map(dict_allergen_encode)
    
    # Process complementary tables
    df_taxonomy_mid = df_taxonomy[['id', 'ingredient_name', 'category_id']].rename(columns = {'ingredient_name': 'product_name', 'id': 'taxonomy_id'})
    df_cats = df_categories[['id', 'name']].rename(columns = {'id': 'category_id', 'name': 'category'})
    df_data_points = df[df['property'] == 'score'][['taxonomy_id', 'n_rows']]
    df_data_points.rename(columns = {'n_rows': 'number_data_points'}, inplace = True)
    
    # Merge with tables
    df_properties = pd.merge(df_properties_tabular, df_taxonomy_mid, how = 'left', on = 'taxonomy_id')
    df_properties = pd.merge(df_properties, df_cats, how = 'left', on = 'category_id')
    df_properties = pd.merge(df_properties, df_data_points, how = 'left', on = 'taxonomy_id')
    
    return df_properties[order_cols];

#############################################################
###################### Execute script #######################
#############################################################

print('\nBeginning script execution...')

# Load query
try:
    PATH = os.path.join(PATH_SQL, PROPERTIES_FILENAME)

    with open(f'{PATH}.sql', 'r') as F:
        query = F.read()

except:
    raise FileNotFoundError('There was an error loading the query. Please try again.')

# Include threshold in the query
query_threshold = query.replace('?', str(THRESHOLD))

# Extract data from query
df_properties = kp.retrieve_sql_query(query_threshold, STRING_CONN)

# Retrieve categories and taxonomy
df_categories = kp.retrieve_sql_table(CATEGORIES_SQL_TABLE, STRING_CONN)

# Compute long form of dataframe
df_properties_long = transform_dataframe(df_properties)

# Convert units and rank properties (rank is needed to compute median values)
df_properties_long_normalised = convert_units(df_properties_long)
df_properties_long_normalised = rank_df(df_properties_long_normalised)

# Compute aggregated properties
df_properties_aggregated = compute_mean_properties(df_properties_long_normalised)

# Insert to database
kp.insert_data_sql(df_properties_aggregated, STRING_CONN, PROPERTIES_SQL_TABLE, append = False)

print('\nProperty table created succesfully! Continuing to second stage.')

# Retrieve SQL tables
df_categories = kp.retrieve_sql_table(CATEGORIES_SQL_TABLE, STRING_CONN)
df_taxonomy = kp.retrieve_sql_table(TAXONOMY_SQL_TABLE, STRING_CONN)
df_properties = kp.retrieve_sql_table(PROPERTIES_SQL_TABLE, STRING_CONN)

df_tabular = get_tabular_data(df_properties, df_categories, df_taxonomy)

# Insert to database
kp.insert_data_sql(df_tabular, STRING_CONN, SUMMARY_SQL_TABLE, append = False)

print('\nSummary table created succesfully! Continuing to third stage.')

# Merge with taxonomy and properties
df_bi = pd.merge(df_properties,
                df_taxonomy[['id', 'ingredient_name', 'category_id']].rename(columns = {'id': 'taxonomy_id'}),
                how = 'left',
                on = 'taxonomy_id')

df_bi = pd.merge(df_bi,
                df_categories[['id', 'name']].rename(columns = {'id': 'category_id', 'name': 'category'}),
                how = 'left',
                on = 'category_id')

# Add source
df_bi['data_source'] = 'kafoodle_pantry'

# Organise columns
df_bi = df_bi[BI_COLS]

# Export to csv
try:
    PATH = os.path.join(PATH_CSV, BI_DATA_FILENAME)
    
    # Export file
    df_bi.to_csv(f'{PATH}.csv', index = False)
    print('File written successfully! Script finalised.')

except:
    raise Exception(f'Could not write csv file in path {PATH}.csv')