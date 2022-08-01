#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing all required functions to operate the backend of the pantry system. This is completely
independent of the automated system, although some functions may be the same.

To be used only by dev team to manage the tables and sources for the application's requirements.
"""

# Import modules
import os
import re
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer
SENTENCE_MODEL = SentenceTransformer('paraphrase-mpnet-base-v2')

# Define constants
PATH_CSV = 'csv/'
CWD = os.getcwd()

# Define functions
def retrieve_gs_link(id_str: str):

    # Build URL with param
    string_url = f'https://docs.google.com/spreadsheets/d/{id_str}/export?format=csv&gid=0'

    return string_url;

def check_file(filename: str, url_str: str, path_csv: str = PATH_CSV, cwd: str = CWD):

    # Check if json dir exists. if not, create it
    cwd = os.getcwd()
    path = os.path.join(cwd, path_csv)

    dir_exists = os.path.isdir(path)

    if not dir_exists:
        os.mkdir(path)

    file_path = os.path.join(path, f'{filename}.csv')
    file_exists = os.path.isfile(file_path)

    if not file_exists:
        exceptionString = f'{filename}.csv does not exist in directory. Please add it to continue.\n\nFile can be downloaded pasting the following URL in a browser --> {url_str}\n\nScript ended execution.'
        raise Exception(exceptionString)

    else:
        print('File found in path. Continuing execution.');

def load_data_from_file(filename: str, path_csv: str = PATH_CSV, cwd: str = CWD):

    # Create path to file
    path = os.path.join(cwd, path_csv, filename)

    # Load file
    with open(f'{path}.csv', 'r') as f:
        df = pd.read_csv(f)

    return df;

def retrieve_sql_table(table_name: str, string_conn: str):

    sqlEngine = create_engine(string_conn)
    dbConnection = sqlEngine.connect()

    try:
        df = pd.read_sql_table(table_name, dbConnection)
        print(f'Successfully retrieved table {table_name}')
        return df;

    except Exception as ex:
        print(ex)
        raise Exception('Execution terminated by exception.')

    finally:
        dbConnection.close();

def retrieve_sql_query(query: str, string_conn: str):

    sqlEngine = create_engine(string_conn)
    dbConnection = sqlEngine.connect()

    try:
        df = pd.read_sql(query, dbConnection)
        print(f'Successfully executed query.')
        return df;

    except Exception as ex:
        print(ex)
        raise Exception('Execution terminated by exception.')

    finally:
        dbConnection.close();

def insert_data_sql(df, string_conn: str, table_name: str, append: bool = True):

    sqlEngine = create_engine(string_conn)
    dbConnection = sqlEngine.connect()

    if append:
        insert_mode = 'append'
    else:
        insert_mode = 'replace'

    try:
        df.to_sql(table_name,
                  string_conn,
                  index = False,
                  if_exists = insert_mode)
        print('Append successfully executed')

    except Exception as ex:
        print('There was an exception inserting new records. Maybe some are already in the table?\n\n')
        print(ex)
        raise Exception('Execution terminated by exception.')

    finally:
        dbConnection.close();

def identify_new_rows(df_file, df_db, column_name: str):

    DF_FILE_COLS = df_file.columns
    df_merge = pd.merge(df_file,
                        df_db[[column_name]],
                        how = 'left',
                        on = column_name,
                        indicator = True)

    df_merge = df_merge[df_merge['_merge'] == 'left_only']

    return df_merge[DF_FILE_COLS];

def check_new_records(df):

    nrows = df.shape[0]

    if nrows == 0:
        return False

    else:
        return True;

def delete_file(filename: str, path_csv: str = PATH_CSV, cwd: str = CWD, extension: str = 'csv'):

    # Create path to file
    path = os.path.join(cwd, path_csv, f'{filename}.{extension}')

    # Check if file exists
    file_exists = os.path.isfile(path)

    # Delete file if exists
    if file_exists:
        os.remove(path);

def remove_all_special_chars(sentences: list):
    """
    Gets a list and only retains letters (lowercaps) and spaces using regex

    Parameters
    ----------
    sentences (list): a list containing text to be processed

    Returns
    ----------
    sentences_out (list): list with str elements containing letters and spaces

    Exception
    ----------
    If the 'sentences' parameter is not list type
    """
    
    # Check argument is list type
    if not isinstance(sentences, list):
        raise TypeError('Argument is not list type')

    processed_sentences = [re.sub('[^A-Za-z ]+', ' ', i) for i in sentences]
    processed_sentences = [i.lower() for i in processed_sentences]

    return processed_sentences;

def remove_double_spaces(sentences: list):
    """
    Gets a list and removes all additional whitespaces

    Parameters
    ----------
    sentences (list): a list containing text to be processed

    Returns
    ----------
    sentences_out (list): list with single spaces only

    Exception
    ----------
    If the 'sentences' parameter is not list type
    """
    
    # Check argument is list type
    if not isinstance(sentences, list):
        raise TypeError('Argument is not list type')

    processed_sentences = [re.sub(' +', ' ', i) for i in sentences]
    processed_sentences = [i.strip() for i in processed_sentences]

    return processed_sentences;

def remove_stopwords(sentences: list, stopwords: list):
    """
    Removes all words matched with the stopword list from the sentences

    Parameters
    ----------
    sentences (list): a list containing text to be processed
    stopwords (list) OPTIONAL: list with words to be removed. Default STOPWORDS['stopwords']

    Returns
    ----------
    list_ingredients_clean (list): list without undesired words from the stopwords list

    Exception
    ----------
    If the 'sentences' parameter is not list type
    """

    # Check argument is list type
    if not isinstance(sentences, list):
        raise TypeError('Argument is not list type')

    # Remove stopwords
    list_double_ingredients = [i.split(' ') for i in sentences]
    list_double_ingredients_sliced = [[i for i in sublist if i not in stopwords] for sublist in list_double_ingredients]

    # Reconstruct cleaned list
    list_ingredients_clean = [' '.join(i).strip() for i in list_double_ingredients_sliced]

    return list_ingredients_clean;

def vectorise_ingredients(sentences: list, model = SENTENCE_MODEL):
    """
    Uses Huggingface model to vectorise the list of words

    Parameters
    ----------
    sentences (list): a list containing text to be processed with N elements
    model (class sentence_transformer) OPTIONAL: model to encode the sentences. Default SENTENCE_MODEL

    Returns
    ----------
    vectorised_sentences (numpy.array): Numpy array of shape Nx768 containing numerical representations.

    Exception
    ----------
    If the 'sentences' parameter is not list type
    """

    # Check argument is list type
    if not isinstance(sentences, list):
        raise TypeError('Argument is not list type')

    # Apply model
    vectorised_sentences = model.encode(sentences, normalize_embeddings = True)

    return vectorised_sentences;

def extract_taxonomy_from_df(df):

    # Extract list and convert to float
    list_vector = df['vector_representation']
    list_vector = [i.strip('] [').split(',') for i in list_vector]

    array_vector = np.array(list_vector)
    array_vector = array_vector.astype(np.float32)

    return array_vector;

def compute_scores(array_ingredients, array_taxonomy, list_ids):
    """
    
    """

    # Compute scores
    array_scores = cosine_similarity(array_ingredients, array_taxonomy)

    # Get best match
    best_score_idx = np.argmax(array_scores, axis = 1)

    # Assign ingredient and score to df
    matched_ingredient = [list_ids[i] for i in best_score_idx]
    matched_score = [np.round(array_scores[i][j], 5) for i, j in enumerate(best_score_idx)]

    return matched_ingredient, matched_score;