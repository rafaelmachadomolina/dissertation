#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 18 10:30:55 2022

@author: rafaelmachado

- Credit for df_to_dict algorithm: https://stackoverflow.com/questions/7653726/how-to-turn-a-list-into-nested-dict-in-python
"""

# Import packages
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Define constants
COLOURS = {'0': '#8fb05c',
           '1': '#97c3fc',
           'child': '#ed7d31',
           'default': '#97c3fc'}

# Define functions
def create_df_from_json(dict_data):

    rows = []

    for key, content in dict_data.items():

        if isinstance(content, dict):

            current_level = content['level']

            newRows = [(key, i, current_level) for i, y in content.items() if isinstance(y, dict)]
            rows.extend(newRows)
            rows.extend(create_df_from_json(content))

    return rows;


def is_child(dict_data):
    '''
    Function that receives a dict and determines if it is a child or not.
    This is based on the following definitio: a dict is no child if it contains
    another dict within.

    Parameters
    ----------
    dict_data : dict
        element in question to be child or not.

    Returns
    -------
    bool
        Whether the dict is child or not

    '''

    checklist = [1 for key, content in dict_data.items() if isinstance(content, dict)]

    if len(checklist) == 0:
        return True
    else:
        return False;


def get_weights(dict_data):
    '''
    Calculates the weight of each element in the dict.
    The weight is the number of children each element has. By definition, a
    child has weight = 1

    Parameters
    ----------
    dict_data : dict
        Element whose weights are to be computed.

    Returns
    -------
    dict
        Dict containint name: weight as key pairs.

    '''

    weights = {}

    for key, content in dict_data.items():

        if not isinstance(content, dict):
            continue

        if is_child(content):
            weights[key] = 1

        else:
            child_weight = get_weights(content)

            weights = weights | child_weight

            total_weight = len([j for j in child_weight.values()])
            weights[key] = total_weight

    return weights;


def get_colours(dict_data, BASE_LEVEL = 0, COLOURS = COLOURS):
    '''
    Function to assign a colour to each element of a dict.
    Colours depend on the level [0, 1] and if an element is a child.

    Parameters
    ----------
    dict_data : dict
        Dict element to compute colours
    BASE_LEVEL : int, optional
        Base to compute the subsequent levels of elements. The default is 0.
    COLOURS : dict, optional
        Cict containing default colours in hex. The default is COLOURS.

    Returns
    -------
    dict
        Dict containing name: colour for each key-value pair.

    '''

    colours = {}

    for key, content in dict_data.items():

        if not isinstance(content, dict):
            continue

        if is_child(content):
            colours[key] = COLOURS['child']

        else:
            if BASE_LEVEL <= 1:
                colours[key] = COLOURS[str(BASE_LEVEL)]

            else:
                colours[key] = COLOURS['default']

            BASE_LEVEL += 1
            new_colours = get_colours(content, BASE_LEVEL = BASE_LEVEL)
            colours = colours | new_colours

    return colours;


def plot_taxonomy(dict_taxonomy, PATH = 'network_plot.html', LEVEL = -1):
    '''
    Plots the taxonomy as a network in an HTML file

    Parameters
    ----------
    dict_taxonomy : dict
        Taxonomy to plot. Must contain a single node in level 0.
    PATH : string, optional
        Name of file to save plots. The default is 'network_plot.html'.
    LEVEL : int, optional
        Trims plot to LEVEL layers. The default is -1 (all layers).

    Returns
    -------
    None.

    '''

    # Get weights
    dict_weights = get_weights(dict_taxonomy)
    dict_weights = {key: (content ** (1/2)) for key, content in dict_weights.items()}

    # Get colours
    dict_colours = get_colours(dict_taxonomy)

    # Convert to df the dict object
    tuples = create_df_from_json(dict_taxonomy)
    df_taxonomy = pd.DataFrame(tuples, columns = ['source', 'target', 'level'])

    if LEVEL >= 0:
        df_taxonomy = df_taxonomy[df_taxonomy['level'] <= LEVEL]

    # Create nx object
    G = nx.from_pandas_edgelist(df_taxonomy,
                                source = 'source',
                                target = 'target')

    # Set node attributes
    nx.set_node_attributes(G, dict_weights, 'size')
    nx.set_node_attributes(G, dict_colours, 'color')

    # Plot network using nx object
    net = Network(height = '100%', width = '100%')
    net.from_nx(G)
    net.show(PATH);


def dict_to_df(dict_data, BASE_LIST = []):
    '''
    Converts a dict into a dataframe

    Parameters
    ----------
    dict_data : dict
        Dict element to convert
    BASE_LIST : list, optional
        List as a base to append elements. The default is [].

    Returns
    -------
    Dataframe
        df containing the taxonomy.

    '''

    item_list = []
    initial_level = len(BASE_LIST)

    for key, content in dict_data.items():

        if not isinstance(content, dict):
            continue

        inner_list = BASE_LIST.copy()
        inner_list.append(key)
        # print('Inner list', inner_list)

        if is_child(content):
            item_list.append(inner_list)

        else:
            new_element = dict_to_df(content, inner_list)
            item_list.extend(new_element)

    if initial_level > 0:
        return item_list;

    else:
        return  pd.DataFrame(item_list);


def df_to_dict(df_data):
    '''
    Converts a dataframe to a dict object

    Parameters
    ----------
    df_data : DataFrame
        df element to be converted.

    Returns
    -------
    dict
        Dict element containing the taxonomy.

    '''

    # Define empty list and dict
    list_return = []
    dict_taxonomy = {}

    # Extract values from df
    list_df = df_data.values.tolist()

    # Remove null values
    for ingredient in list_df:

        ingredients_trimmed = [i for i in ingredient if i is not None]
        list_return.append(ingredients_trimmed)

    # Create dict
    for path in list_return:
        current_level = dict_taxonomy
        for level, part in enumerate(path):
            if part not in current_level:
                current_level[part] = {'level': level + 1}
            current_level = current_level[part]

    # Add level 0
    dict_taxonomy['level'] = 0

    return dict_taxonomy;

###############################################################################
###############################################################################
###############################################################################
