#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script containing the API server.
Test match: curl -X POST http://127.0.0.1:8000/match_ingredients/ -H 'Content-Type: application/json' -d '{"ingredients":["apple"]}'
Test properties: curl -X POST http://127.0.0.1:8000/get_properties/ -H 'Content-Type: application/json' -d '{"ingredient_ids":[1]}'
"""

# Import modules
# import time
from typing import List, Union
from fastapi import FastAPI
from pydantic import BaseModel
import src.ingredient_match as ingredient_match

# Create internal response models
class DictIngredients(BaseModel):
    ingredient: str
    id: int
    score: float

class DictProperties(BaseModel):
    id: int
    has_data: bool
    energy: Union[float, None]
    fat: Union[float, None]
    saturated: Union[float, None]
    carbohydrate: Union[float, None]
    fibre: Union[float, None]
    sugar: Union[float, None]
    protein: Union[float, None]
    salt: Union[float, None]
    gluten_wheat: Union[bool, None]
    gluten_rye: Union[bool, None]
    gluten_barley: Union[bool, None]
    gluten_oats:Union[bool, None]
    gluten: Union[bool, None]
    crustaceans: Union[bool, None]
    eggs: Union[bool, None]
    fish: Union[bool, None]
    peanuts: Union[bool, None]
    soya: Union[bool, None]
    milk: Union[bool, None]
    nuts: Union[bool, None]
    nuts_almonds: Union[bool, None]
    nuts_hazelnuts: Union[bool, None]
    nuts_walnuts: Union[bool, None]
    nuts_cashews: Union[bool, None]
    nuts_pecans: Union[bool, None]
    nuts_brazil: Union[bool, None]
    nuts_pistachios: Union[bool, None]
    nuts_macadamia: Union[bool, None]
    sesame_seeds: Union[bool, None]
    sulphur_dioxide: Union[bool, None]
    molluscs: Union[bool, None]
    celery: Union[bool, None]
    mustard: Union[bool, None]
    lupin: Union[bool, None]

# Create body objects
class BodyIngredientsIn(BaseModel):
    ingredients: List[str]

class BodyIngredientsOut(BaseModel):
    response: List[DictIngredients]

class BodyPropertiesIn(BaseModel):
    ingredient_ids: List[int]

class BodyPropertiesOut(BaseModel):
    response: List[DictProperties]
    

# Create application object
app = FastAPI()

@app.get('/dummy/', status_code = 200)
def dummy():

    return {'hello': 'world'}

@app.post('/match_ingredients/', response_model = BodyIngredientsOut, status_code = 200)
def match_ingredients(ingredients: BodyIngredientsIn):

    # print('\nEndpoint called.')
    # TIME_ABS = time.time()
    # TIME = time.time()

    # Extract list
    list_ingredients = ingredients.dict()['ingredients']
    # print(f'Time to list_ingredients: {time.time() - TIME:.2f} s\n')
    # TIME = time.time()

    # Execute functions
    response = ingredient_match.execute_matched_ingredients(list_ingredients)
    # print(f'\nTime to execute_matched_ingredients: {time.time() - TIME:.2f} s')
    
    # print(f'\nTotal execution time: {time.time() - TIME_ABS:.2f} s')

    return {'response': response};

@app.post('/get_properties/', response_model = BodyPropertiesOut, status_code = 200)
def get_properties(ingredient_ids: BodyPropertiesIn):

    # Extract list
    list_ingredient_ids = ingredient_ids.dict()['ingredient_ids']

    # Execute functions
    response = ingredient_match.execute_fill_properties(list_ingredient_ids)

    return {'response': response};

