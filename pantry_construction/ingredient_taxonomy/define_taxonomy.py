#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 16 23:41:16 2022

@author: rafaelmachado
"""

# Import packages
import json

# Define constants
ENGLISH_ONLY = True
JSON_PATH = 'json/'

# Define functions
def eliminate_nonenglish(data, is_dict = True, active = ENGLISH_ONLY):
    '''
    Removes all elements starting different from 'en' in a dict

    Parameters
    ----------
    data : dict or list
        Dict or list to remove elements from.
    is_dict : bool, optional
        indicates if data is dict, otherwise is list. The default is True.
    active : bool, optional
        Variable to activate functions. The default is ENGLISH_ONLY.

    Returns
    -------
    TYPE
        Returns dict (or list) without elements different than English.

    '''
    
    if (is_dict & active):
        return {key: content for key, content in data.items() if key.startswith('en')};
    elif active:
        return [key for key in data if key.startswith('en')];
    else:
        return data;

def get_superparents(data):
    '''
    Indicates which elements are super parents, meaning they have children and 
    no parent at all

    Parameters
    ----------
    data : dict
        Dict containing elements to evaluate.

    Returns
    -------
    dict
        dict of super parents.

    '''
    
    # Get entries with no parents
    dict_parents = {i: data[i] for i in data.keys() if 'parents' not in data[i].keys()}
    
    # Eliminate entries with no children
    dict_parents = {i: dict_parents[i] for i in dict_parents.keys() if 'children' in dict_parents[i].keys()}
    
    # Filter unwanted elements
    KEYS = ['name', 'children']
    
    dict_parents_filtered = {key: {i: y for i, y in content.items() if i in KEYS} for key, content in dict_parents.items()}
    
    return dict_parents_filtered;

def get_onlychildren(data):
    '''
    Indicates which elements are children only, meaning they have a partent
    and no additional element below

    Parameters
    ----------
    data : dict
        dict containing elements to evaluate.

    Returns
    -------
    dict
        dict of children only.

    '''
    
    # Get entries with no children
    dict_children = {i: data[i] for i in data.keys() if 'children' not in data[i].keys()}
    
    # Eliminate entries with no parents
    dict_children = {i: dict_children[i] for i in dict_children.keys() if 'parents' in dict_children[i].keys()}

    # Filter unwanted elements
    KEYS = ['name', 'parents']
    
    dict_children_filtered = {key: {i: y for i, y in content.items() if i in KEYS} for key, content in dict_children.items()}

    return dict_children_filtered;

def prune_tree(data):
    '''
    Remove elements different than parents and children. Also adds the max_levels
    list

    Parameters
    ----------
    data : dict
        Dict to remove elements from.

    Returns
    -------
    dict
        Pruned tree with fewer elements remaining.

    '''
    
    KEYS = ['parents', 'children']

    dict_filtered = {key: {i: y for i, y in content.items() if i in KEYS} for key, content in data.items()}
    dict_filtered = {key: content | {'max_levels': []} for key, content in dict_filtered.items()}

    return dict_filtered;

def build_taxonomy(tree_obj, superParent, onlyChildren, base_level = 0):
    '''
    Creates a nested taxonomy from elements. Function is recurrent.

    Parameters
    ----------
    tree_obj : dict
        Dict of elements to be concatenated together in a tree structure.
    superParent : dict
        Dict containing super parent elements.
    onlyChildren : dict
        Dict containing children elements only.
    base_level : int, optional
        Base level of elements nested. The default is 0.

    Returns
    -------
    dict
        Taxonomy in a single dict object.

    '''

    # Define base level
    return_taxonomy = {'level': base_level}    

    for key, content in superParent.items():
        
        
        # Add base_level
        content['level'] = base_level
        
        current_level = base_level + 1
        
        # Check if key is not only children
        if key in onlyChildren.keys():
            content['level'] = current_level
            tree_obj[key]['max_levels'] += [current_level]
            return_taxonomy[key] = content
            continue;
    
        children = eliminate_nonenglish(content['children'], is_dict = False)
        
        next_level_children = {child: tree_obj[child] for child in children}
        next_level_dict = build_taxonomy(tree_obj, next_level_children, onlyChildren, current_level)
        
        # Update level
        for child_key in next_level_children.keys():
            tree_obj[child_key]['max_levels'] += [current_level]
        
        # Append to taxonomy
        return_taxonomy[key] = next_level_dict
            
    return return_taxonomy;

def trim_taxonomy(data, onlyChildren):
    '''
    Eliminates ingredients repeated in the taxonomy, based on their level. This
    works only for children elements.

    Parameters
    ----------
    data : dict
        Taxonomy to trim.
    onlyChildren : dict
        Dict containing only children elements.

    Returns
    -------
    None.

    '''
    
    current_level = data['level']
    taxonomy_iter = data.copy()
    
    for key, child in taxonomy_iter.items():
        
        if key == 'level':
            # Do nothing key is 'level'
            continue
        
        if key in onlyChildren.keys():
            
            # child_level = child['level']
            child_level = max(child['max_levels'])
            if child_level != (current_level + 1): # Means ingredient goes below in taxonomy
                del data[key]
                
        else:
            trim_taxonomy(child, onlyChildren)
            
def check_childs(data, onlyChildren):
    '''
    Checks if a given element has at least one child in the lineage

    Parameters
    ----------
    data : dict
        Taxonomy tree to check.
    onlyChildren : dict
        Dict with children only elements.

    Returns
    -------
    bool
        If True, element has at least one child, False otherwise.

    '''
    
    checks = []
    
    for key, content in data.items():

        if key in onlyChildren.keys():
            return True;
        
        
        elif isinstance(content, dict):
            checks.append(check_childs(content, onlyChildren))
                  
    if (True in checks):
        return True
    else:
        return False;
    
def drop_childless(data, onlyChildren):
    '''
    Eliminates elements with no childs

    Parameters
    ----------
    data : dict
        Taxonomy tree to remove objects from.
    onlyChildren : dict
        Dict containing only childrens.

    Returns
    -------
    None.

    '''
    
    taxonomy_iter = data.copy()
    
    for key, content in taxonomy_iter.items():
        
        if not isinstance(content, dict):
            continue
            
        if key in onlyChildren.keys():
            continue
        
        elif not check_childs(content, onlyChildrens):
            del data[key]
            
        else:
            drop_childless(content, onlyChildren);
            
def remove_max_level(data):
    '''
    Remove max_level list from taxonomy

    Parameters
    ----------
    data : dict
        Taxonomy containing ingredients and max_level lists.

    Returns
    -------
    None.

    '''
    
    for key, content in data.items():
        
        if isinstance(content, dict):
        
            if 'max_levels' in content.keys():
                del content['max_levels']
            
            else:
                remove_max_level(content);
                
def remove_lang(data):
    '''
    Remove language string from each element

    Parameters
    ----------
    data : dict
        Taxonomy to be trimmed.

    Returns
    -------
    None.

    '''
    
    taxonomy_iter = data.copy()
    
    for key, content in taxonomy_iter.items():
        
        if ':' in key:
              newKey = key.split(':')[1]
              data[newKey] = content
              del data[key]
              
        if isinstance(content, dict):
            remove_lang(content);
    
###############################################################################
###############################################################################
###############################################################################

# Read Robotoff file
with open(JSON_PATH + 'robotoff_taxonomy.json', 'r', encoding = 'utf-8') as F:
    robotoff_taxonomy_raw = json.loads(F.read())
    
data = eliminate_nonenglish(robotoff_taxonomy_raw)
    
# Identify super parents and only children entities
superParents = get_superparents(data)
onlyChildrens = get_onlychildren(data)

# Delete irrelevant information for the taxonomy
tree = prune_tree(data)
        
# Compute taxonomy
taxonomy = build_taxonomy(tree, superParents, onlyChildrens);

# Trim tree
trim_taxonomy(taxonomy, onlyChildrens)
drop_childless(taxonomy, onlyChildrens)
remove_max_level(taxonomy)
remove_lang(taxonomy)

# Export taxonomy
# with open(JSON_PATH + 'pantry_taxonomy.json', 'w') as F:
#     json.dump({'Kafoodle pantry': taxonomy}, F)
    