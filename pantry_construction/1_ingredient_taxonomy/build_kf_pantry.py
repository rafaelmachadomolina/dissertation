#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 25 12:38:53 2022

@author: rafaelmachado
"""

# Import libraries
import json
import pandas as pd

# Import modules
import rmm_taxonomy as rmm_tx

# Define constants
JSON_PATH = 'json/'
EXCEL_PATH = 'excel/'
CSV_PATH = 'csv/'
PLOT_PATH = 'taxonomy_plots/'

# Import files
with open(JSON_PATH + 'pantry_taxonomy.json', 'r') as F:
    dict_taxonomy = json.load(F)
    
with open(CSV_PATH + 'ingredient_timeseries.csv', 'r') as F:
    df_kf_groups = pd.read_csv(F, sep = ';')
    
# Process top categories
df_categories = df_kf_groups[['category_id', 'category', 'qnt_ingredients']].groupby(['category_id', 'category'], as_index = False).sum()
df_categories.sort_values(by = 'qnt_ingredients', ascending = False, inplace = True)
df_categories.reset_index(drop = True, inplace = True)

# Convert taxonomy to df and export to excel
df_taxonomy = rmm_tx.dict_to_df(dict_taxonomy)

# df_taxonomy.to_excel(EXCEL_PATH + 'taxonomy.xlsx', index = False, sheet_name = 'raw_taxonomy')

# Read and plot taxonomy
df_kafoodle = pd.read_excel(EXCEL_PATH + 'taxonomy.xlsx', sheet_name = 'kafoodle_taxonomy')
df_kafoodle = df_kafoodle.where(pd.notnull(df_kafoodle), None)
dict_kafoodle_taxonomy = rmm_tx.df_to_dict(df_kafoodle)

rmm_tx.plot_taxonomy(dict_kafoodle_taxonomy, PLOT_PATH + 'complete_taxonomy.html')

# Plot taxonomy by ingredient groups
for key, content in dict_kafoodle_taxonomy['Kafoodle pantry'].items():
    
    if not isinstance(content, dict):
        continue
    
    cat_name = key.split(':')[1]
    file_name = PLOT_PATH + cat_name + '.html'
    
    # Generate plot
    rmm_tx.plot_taxonomy({cat_name: content}, file_name)

