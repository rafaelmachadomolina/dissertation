#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Config file to store or retrieve credentials and constants."""

# Import libraries
import os

from sentence_transformers import SentenceTransformer
SENTENCE_MODEL = SentenceTransformer('paraphrase-mpnet-base-v2')

# Define consants
STOPWORDS_SQL_TABLE = 'pantry__stopwords'
TAXONOMY_VECTOR_SQL_TABLE = 'pantry__taxonomy_vector'
PROPERTIES_SQL_TABLE = 'pantry__taxonomy_ref_values'

# Define functions
def get_mysql_params():
    """
    Generates dict to connect to MySQL database.

    Returns
    ----------
    params (dict): dictionary containing connection parameters
    """

    # Retrieve names
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'kafoodle')
    DB_PORT = int(os.environ.get('DB_PORT', '3306'))
    DB_USERNAME = os.environ.get('DB_USERNAME', 'servuser')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')

    dict_out = {'DB_HOST': DB_HOST,
                'DB_NAME': DB_NAME,
                'DB_PORT': DB_PORT,
                'DB_USERNAME': DB_USERNAME,
                'DB_PASSWORD': DB_PASSWORD}
    
    return dict_out;