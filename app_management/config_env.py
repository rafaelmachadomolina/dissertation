#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Config file to retrieve credentials."""

# Import libraries
import os

# Define consants
STOPWORDS_FILENAME = 'Algorithm stopwords - stopwords'
TAXONOMY_FILENAME = 'Ingredient taxonomy - taxonomy'
EXTRACT_INGREDIENTS_QUERY_FILENAME = 'extract_ingredients'
INGREDIENT_PROPERTIES_QUERY_FILENAME = 'extract_properties'
BI_DATA_FILENAME = 'dashboard_data'

CONV_FACTORS = {'mg': 1.0/1000,
                'kj': 1.0/4.184}
CONV_UNITS = {'mg': 'g',
              'kj': 'kcal'}

# Define functions
def get_mysql_uri():
    """
    Generates URI to connect to MySQL database.

    Returns
    ----------
    uri (str): string formatted to connect to the database
    """

    # Retrieve names
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'kafoodle')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USERNAME = os.environ.get('DB_USERNAME', 'servuser')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
    return f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}';

def get_gs_params():
    """
    Retrieves Google Sheets documents ids and ranges to perform operations.

    Returns
    ----------
    gs_params (dict): dict containing the string ids as keys.
    """

    STOPWORDS_ID = os.environ.get('GS_STOPWORDS_ID')
    TAXONOMY_ID = os.environ.get('GS_TAXONOMY_ID')

    gs_params = {'GS_STOPWORDS_ID': STOPWORDS_ID,
                  'GS_TAXONOMY_ID': TAXONOMY_ID}

    return gs_params;
