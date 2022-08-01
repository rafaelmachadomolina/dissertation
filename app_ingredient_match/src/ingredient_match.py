#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module with all functions to compute the similarity score between
ingredients and the stored taxonomy."""

# Import modules
import re
import time
import pymysql
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import src.config_env as config_env

# Define constants
DB_PARAMS = config_env.get_mysql_params()
SENTENCE_MODEL = config_env.SENTENCE_MODEL

STOPWORDS_SQL_TABLE = config_env.STOPWORDS_SQL_TABLE
TAXONOMY_VECTOR_SQL_TABLE = config_env.TAXONOMY_VECTOR_SQL_TABLE
PROPERTIES_SQL_TABLE = config_env.PROPERTIES_SQL_TABLE

SQL_TABLE_FIELDS = ['taxonomy_id', 'property_type', 'property', 'reference_value']

LIST_RESPONSE_KEYS = ['ingredient_ids', 'has_data', 'energy', 'fat', 'saturated', 'carbohydrate', 'fibre',
                    'sugar', 'protein', 'salt', 'gluten_wheat', 'gluten_rye',
                    'gluten_barley', 'gluten_oats', 'gluten', 'crustaceans', 'eggs', 'fish',
                    'peanuts', 'soya', 'milk', 'nuts', 'nuts_almonds', 'nuts_hazelnuts',
                    'nuts_walnuts', 'nuts_cashews', 'nuts_pecans', 'nuts_brazil',
                    'nuts_pistachios', 'nuts_macadamia', 'sesame_seeds',
                    'sulphur_dioxide', 'molluscs', 'celery', 'mustard', 'lupin'] # Defines the amount of lists (arrays) in the response

#############################################################
#################### Preload functions ######################
#############################################################

def retrieve_sql_table(tablename: str, db_params: dict = DB_PARAMS):
    """
    Retrieves a complete table from the database.

    Parameters
    ----------
    tablename (str): the name of the table. Does not include db_name or schema
    db_params (dict) OPTIONAL: dictionary containing the connectrion parameters (like host, username, etc.). Default stored in config

    Returns
    ----------
    rows (tuple): tuple containing all rows from the table

    Exception
    ----------
    If there is a problem interacting with the database (could be connection or bad query)
    """
    # Create connection
    connectionObject = pymysql.connect(host = db_params['DB_HOST'],
                                        port = db_params['DB_PORT'],
                                        db = db_params['DB_NAME'],
                                        user = db_params['DB_USERNAME'],
                                        password = db_params['DB_PASSWORD'])

    # Attempt connection
    try:

        # Create a cursor object
        cursorObject = connectionObject.cursor() 
        
        # SQL query string
        sqlQuery = f'SELECT * FROM {tablename}'
        
        # Execute the query
        cursorObject.execute(sqlQuery)
        
        #Fetch all the rows
        rows = cursorObject.fetchall()

        return rows;

    except Exception as e:
        raise Exception("Exeception occured:{}".format(e))

    finally:
        connectionObject.close();

def retrieve_sql_table_filtered(tablename: str, set_ids: set, select_fields: list = SQL_TABLE_FIELDS, db_params: dict = DB_PARAMS):
    """
    Retrieves selected fields from a table in the db, choosing ids pased as a parameter.

    Parameters
    ----------
    tablename (str): the name of the table. Does not include db_name or schema
    set_ids (set): unique ingredient ids to retrieve. This avoids calling all the table.
    select_fields (list) OPTIONAL: list of columns to retrieve. Default stored in SQL_TABLE_FIELDS constant
    db_params (dict) OPTIONAL: dictionary containing the connectrion parameters (like host, username, etc.). Default stored in config

    Returns
    ----------
    rows (tuple): tuple containing all rows from the table, with selected fields.

    Exception
    ----------
    If there is a problem interacting with the database (could be connection or bad query)
    """

    # Create connection
    connectionObject = pymysql.connect(host = db_params['DB_HOST'],
                                        port = db_params['DB_PORT'],
                                        db = db_params['DB_NAME'],
                                        user = db_params['DB_USERNAME'],
                                        password = db_params['DB_PASSWORD'])

    # Process ids to filter
    string_ids = str(set_ids).strip('}{')

    # Process fields
    select_cols = str(select_fields).strip('][')
    select_cols = select_cols.replace("'", '')

    # Attempt connection
    try:

        # Create a cursor object
        cursorObject = connectionObject.cursor() 
        
        # SQL query string
        sqlQuery = f'''SELECT {select_cols}
                        FROM {tablename}
                        WHERE taxonomy_id in ({string_ids})
                            AND property_type <> "score"''' # Get only needed columns, filter out mean score (not needed)
        
        # Execute the query
        cursorObject.execute(sqlQuery)
        
        #Fetch all the rows
        rows = cursorObject.fetchall()

        return rows;

    except Exception as e:
        raise Exception("Exeception occured:{}".format(e))

    finally:
        connectionObject.close();

def parse_stopwords(tuple_from_sql: tuple):
    """
    Parses the tuples from the DB query to a list of stopwords

    Parameters
    ----------
    tuple_from_sql (tuple): a tuple with the stopwords in the second element

    Returns
    ----------
    list_stopwords (list): list with the elements of the tuple
    """

    # Extract stopwords to list
    list_stopwords = [i[1] for i in tuple_from_sql]

    return list_stopwords;

def parse_taxonomy(tuple_from_sql: tuple):
    """
    Parses the tuples from the DB query to a dict containing table id (unique) as the key, and
        taxonomy_id (non unique - plurals and singulars) and vector form.

    Parameters
    ----------
    tuple_from_sql (tuple): a tuple with the ids in the first element, taxonomy_ids in the second, and vectors in the fourth.

    Returns
    ----------
    dict_return (ddict): dictionary containing the organised vector representations of the taxonomy
    """

    # Create lists
    list_ids = [i[0] for i in tuple_from_sql]
    list_taxonomy_ids = [i[1] for i in tuple_from_sql]
    list_vectors = [i[3].strip('] [').split(',') for i in tuple_from_sql]

    # Convert vector text to numpy
    array_vector = np.array(list_vectors)
    array_vector = array_vector.astype(np.float32)

    # Create return dict
    dict_return = {key: {'id':list_taxonomy_ids[pos], 'vector': array_vector[pos]} for pos, key in enumerate(list_ids)}

    return dict_return;

def preprocess_taxonomy(taxonomy: dict):
    """
    Parses the vectorised taxonomy into a list of integers (ids) and a numpy array of vectors

    Parameters
    ----------
    taxonomy (dict) OPTIONAL: a dict containing the taxonomy ids as keys, and vector representation as values. Default TAXONOMY_VECT

    Returns
    ----------
    taxonomy_list (list): list of integers containind the ids
    taxonomy_vector (numpy.array): Numpy array of shape Nx768 containing numerical representations.

    Exception
    ----------
    If the 'taxonomy' parameter is not dict type
    """

    # Check argument is dict type
    if not isinstance(taxonomy, dict):
        raise TypeError('Argument is not dict type')

    taxonomy_list = [int(i['id']) for i in taxonomy.values()]
    taxonomy_vector = np.array([i['vector'] for i in taxonomy.values()], dtype = np.float32)

    return taxonomy_list, taxonomy_vector;

# Store data in memory - stopwords
TUPLE_STOPWORDS = retrieve_sql_table(STOPWORDS_SQL_TABLE)
LIST_STOPWORDS = parse_stopwords(TUPLE_STOPWORDS)

# Store data in memory - taxonomy
TUPLE_VECT_TAXONOMY = retrieve_sql_table(TAXONOMY_VECTOR_SQL_TABLE)
DICT_TAXONOMY = parse_taxonomy(TUPLE_VECT_TAXONOMY)
LIST_TAXONOMY, ARRAY_TAXONOMY = preprocess_taxonomy(DICT_TAXONOMY)

#############################################################
##################### Define functions ######################
#############################################################

def convert_list_elements_str(sentences: list):
    """
    Gets a list as a parameter and returns all elements as string.

    Parameters
    ----------
    sentences (list): a list containing text or numbers

    Returns
    ----------
    sentences_out (list): list with only str elements

    Exception
    ----------
    If the 'sentences' parameter is not list type
    """

    # Check argument is list type
    if not isinstance(sentences, list):
        raise TypeError('Argument is not list type')

    return [str(i) for i in sentences];

def convert_list_elements_int(sentences: list):
    """
    Gets a list as a parameter and returns all elements as int.

    Parameters
    ----------
    sentences (list): a list containing text or numbers

    Returns
    ----------
    sentences_out (list): list with only int elements

    Exception
    ----------
    If the 'sentences' parameter is not list type
    If some of the elements are not convertible to int
    """

    # Check argument is list type
    if not isinstance(sentences, list):
        raise TypeError('Argument is not list type')

    try:
        return [int(i) for i in sentences];

    except:
        raise TypeError('Some of the elements are not convertible to int')

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

def remove_stopwords(sentences: list, stopwords: list = LIST_STOPWORDS):
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
    


def compute_scores(ingredients_array, list_taxonomy: list = LIST_TAXONOMY, array_taxonomy = ARRAY_TAXONOMY):
    """
    Computes similarity scores for ingredients and taxonomy data

    Parameters
    ----------
    ingredients_array (numpy.array): vector representation of the incoming ingredients.
    dict_taxonomy (dict): a dict containing the taxonomy ids as keys, and vector representation as values. Default TAXONOMY_VECT

    Returns
    ----------
    matched_ingredient (list): list of matched taxonomy's ids
    matched_score (list): scores of cosine similarity for each match
    """

    # Obtain ids and vector forms from taxonomy
    

    # Compute scores
    array_scores = cosine_similarity(ingredients_array, array_taxonomy)

    # Get best match
    best_score_idx = np.argmax(array_scores, axis = 1)

    # Assign ingredient and score to df
    matched_ingredient = [list_taxonomy[i] for i in best_score_idx]
    matched_score = [np.round(array_scores[i][j], 5) for i, j in enumerate(best_score_idx)]

    return matched_ingredient, matched_score;

def encode_allergens(tuple_values: tuple):
    """
    Encodes allergen information into T(rue) and F(alse) values.

    Parameters
    ----------
    tuple_values (tuple): tuple containing the results from the SQL query.

    Returns
    ----------
    tuple_out (tuple): tuple with the same elements as the input, but the allergen values are encoded True and False, rather than 1 and 0
    """

    # Convert to list to edit
    list_values = [[j for j in i] for i in tuple_values]

    # Encode variables
    list_values_edited = []

    for i in list_values:

        if i[1] == 'allergen':
            if i[3] == 0:
                i[3] = False
            else:
                i[3] = True
            
            list_values_edited.append(i)

        else:
            list_values_edited.append(i)

    # Reverse to tuple
    tuple_out = tuple([tuple([j for j in i]) for i in list_values_edited])

    return tuple_out;

def parse_reference_values(tuple_values: tuple):
    """
    Parses the results from the SQL query into a dictionary, with taxonomy_ids as keys and properties as values.

    Parameters
    ----------
    tuple_values (tuple): tuple containing the results from the SQL query. Could be encoded or not.

    Returns
    ----------
    dict_out (dict): dictionary with taxonomy_ids as keys, and properties (energy, nuts, etc.) as values.
    """

    # Generate unique taxonomy ids
    set_ids = set([i[0] for i in tuple_values])

    # Create response dict
    dict_out = {i: {j[2]: j[3] for j in tuple_values if j[0] == i} for i in set_ids}

    return dict_out;

def insert_properties(list_ids: list, dict_values: dict, KEYS: list = LIST_RESPONSE_KEYS):
    """
    Combines the input and the properties into a dictionary formatted to the API response.

    Parameters
    ----------
    list_ids (list): list of original ids passed as input
    dict_values (dict): dictionary containing properties retrieved from the database
    KEYS (list) OPTIONAL: list containing the keys for the response. Default is LIST_RESPONSE_KEYS stored as constant

    Returns
    ----------
    list_out (list): list containing the response, including null values if ids/properties are not found.
    """
    # Define response item
    list_out = [{'id': i} for i in list_ids]
    PROPERTIES = KEYS[2:]

    # Fill out dict keys
    for pos, ing_id in enumerate(list_ids):

       # Validate data and include in response
        has_data = True if ing_id in dict_values.keys() else False
        list_out[pos]['has_data'] = has_data

        # Select element of current ingredient
        dict_data = dict_values[ing_id] if has_data else {i: None for i in PROPERTIES}

        # Complement missing fields with None
        dict_data_full = {i: dict_data.get(i) for i in PROPERTIES}

        # Fill out data to response
        for property in PROPERTIES:
            list_out[pos][property] = dict_data_full[property]

    return list_out;

def create_response_match_ingredients(sentences: list, matched_ingredients: list, matched_score: list):
    """
    Receives the original ingredients and the results to zip them into an organised dictionary.

    Parameters
    ----------
    sentences (list): list of original ingredients
    matched_ingredients (list): list of ids of best-matched ingredients
    matched_score (list): list of scores for the best-matched ingredients

    Returns
    ----------
    dict_response (list): list object with a dict per input ingredient. Dict contains name, id matched and score as keys: values

    Exception
    ----------
    If the lists are of different length.
    """

    # Check length of lists
    len_sentences = len(sentences)
    len_matched_ings = len(matched_ingredients)
    len_score = len(matched_score)

    if len_sentences != len_matched_ings or len_matched_ings != len_score:
        raise Exception('Lists are not the same length.')

    # Convert scores to float with precision 4
    matched_score_rounded = [round(float(i), 4) for i in matched_score]

    list_response = [{'ingredient': x, 'id': y, 'score': z} for x, y, z in zip(sentences, matched_ingredients, matched_score_rounded)]
    # dict_response = {'ingredients': sentences,
    #                 'matched_ids': matched_ingredients,
    #                 'matching_score': matched_score}

    return list_response;

#############################################################
#################### Endpoint functions #####################
#############################################################

def execute_matched_ingredients(ingredient_list: list):
    """
    Executes all chained functions required to process the ingredients.

    Parameters
    ----------
    ingredient_list (list): a list of all ingredients to be matched

    Returns
    ----------
    list_response (list): list object for the response. Contains dicts per each ingredients passed.
    """
    # TIME = time.time()
    # Execute sequentially the functions to return the match
    ingredients = convert_list_elements_str(ingredient_list)
    # print(f'Time to convert_list_elements_str: {time.time() - TIME:.2f} s')
    # TIME = time.time()

    ingredients = remove_all_special_chars(ingredients)
    # print(f'Time to remove_all_special_chars: {time.time() - TIME:.2f} s')
    # TIME = time.time()

    ingredients = remove_double_spaces(ingredients)
    # print(f'Time to remove_double_spaces: {time.time() - TIME:.2f} s')
    # TIME = time.time()

    ingredients = remove_stopwords(ingredients)
    # print(f'Time to remove_stopwords: {time.time() - TIME:.2f} s')
    # TIME = time.time()

    array_vector = vectorise_ingredients(ingredients)
    # print(f'Time to vectorise_ingredients: {time.time() - TIME:.2f} s')
    # TIME = time.time()

    matched_ingredients, matched_scores = compute_scores(array_vector)
    # print(f'Time to compute_scores: {time.time() - TIME:.2f} s')
    # TIME = time.time()

    list_response = create_response_match_ingredients(ingredient_list, matched_ingredients, matched_scores)
    # print(f'Time to create_response_match_ingredients: {time.time() - TIME:.2f} s')

    return list_response;

def execute_fill_properties(list_ingredient_ids: list):
    """
    Executes all chained functions required to process the property match.

    Parameters
    ----------
    list_ingredient_ids (list): a list of all ingredient_ids (from taxonomy) to be matched

    Returns
    ----------
    list_response (list): list object containing dicts with elements and their properties
    """
    # Format input
    list_ids = convert_list_elements_int(list_ingredient_ids)
    set_ids = set(list_ids) # set() discards ducplicate ids

    # Extract properties from db
    tuple_properties = retrieve_sql_table_filtered(PROPERTIES_SQL_TABLE, set_ids)

    # Parse properties
    tuple_properties = encode_allergens(tuple_properties)

    dict_properties = parse_reference_values(tuple_properties)

    list_response = insert_properties(list_ids, dict_properties)

    return list_response;