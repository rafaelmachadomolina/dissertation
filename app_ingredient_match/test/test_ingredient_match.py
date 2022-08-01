#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testing for module 'ingredient_match'.
To execute, type in the command line: python -m unittest test/test_ingredient_match.py
"""

# Import modules
import unittest
import numpy as np

import src.ingredient_match as moduleTest

# Import only to obtain DB parameters
import src.config_env as config_env
DB_PARAMS = config_env.get_mysql_params()

# Create class
class Test_ingredient_match(unittest.TestCase):

    def test_convert_list_elements_str(self):
        print('\nTesting convert_list_elements_str...')

        self.assertEqual(moduleTest.convert_list_elements_str(['alpha', 'Beta', 3, None, '']), ['alpha', 'Beta', '3', 'None', ''])
        self.assertEqual(moduleTest.convert_list_elements_str([]), [])
        self.assertIsInstance(moduleTest.convert_list_elements_str(['a']), list)

        with self.assertRaises(TypeError):
            moduleTest.convert_list_elements_str(0)

    def test_convert_list_elements_int(self):
        print('\nTesting convert_list_elements_int...')

        self.assertEqual(moduleTest.convert_list_elements_int(['3', 2]), [3, 2])
        self.assertEqual(moduleTest.convert_list_elements_int([]), [])
        self.assertIsInstance(moduleTest.convert_list_elements_int([1, 2, 3]), list)

        with self.assertRaises(TypeError):
            moduleTest.convert_list_elements_int(0)

        with self.assertRaises(TypeError):
            moduleTest.convert_list_elements_int(['a'])

    def test_remove_all_special_chars(self):
        print('\nTesting remove_all_special_chars...')

        self.assertEqual(moduleTest.remove_all_special_chars(['a', 'b']), ['a', 'b'])
        self.assertEqual(moduleTest.remove_all_special_chars(['a&', 'b.1']), ['a ', 'b '])
        self.assertEqual(moduleTest.remove_all_special_chars(['Alpha', 'BETA 55']), ['alpha', 'beta  '])
        self.assertIsInstance(moduleTest.remove_all_special_chars(['a']), list)

        with self.assertRaises(TypeError):
            moduleTest.remove_all_special_chars(0)

    def test_remove_double_spaces(self):
        print('\nTesting remove_double_spaces...')

        self.assertEqual(moduleTest.remove_double_spaces(['a', 'b c']), ['a', 'b c'])
        self.assertEqual(moduleTest.remove_double_spaces([' a     ', 'b  c']), ['a', 'b c'])
        self.assertIsInstance(moduleTest.remove_double_spaces(['a']), list)

        with self.assertRaises(TypeError):
            moduleTest.remove_double_spaces(0)

    def test_remove_stopwords(self):
        print('\nTesting remove_stopwords...')

        STOPWORDS = ['dog', 'cat']

        self.assertEqual(moduleTest.remove_stopwords(['a', 'b'], STOPWORDS), ['a', 'b'])
        self.assertEqual(moduleTest.remove_stopwords(['a big dog', 'cat and dog'], STOPWORDS), ['a big', 'and'])
        self.assertIsInstance(moduleTest.remove_stopwords(['a'], STOPWORDS), list)

        with self.assertRaises(TypeError):
            moduleTest.remove_stopwords(0, STOPWORDS)

    def test_vectorise_ingredients(self):
        print('\nLoading sentence_transformers module for the test')
        from sentence_transformers import SentenceTransformer
        SENTENCE_MODEL = SentenceTransformer('paraphrase-mpnet-base-v2')
        
        MODEL_COMPONENTS = 768

        print('\nTesting vectorise_ingredients...')

        # Test only for the paraphrase-mpnet-base-v2 model. Other models may have a different number of components
        self.assertEqual(moduleTest.vectorise_ingredients(['a', 'b'], SENTENCE_MODEL).shape, (2, MODEL_COMPONENTS))

        with self.assertRaises(TypeError):
            moduleTest.vectorise_ingredients(0, SENTENCE_MODEL)

    def test_preprocess_taxonomy(self):
        print('\nTesting preprocess_taxonomy...')

        TAXONOMY = {'1': {'id': 1, 'vector': np.array([3/5, 4/5])},
                    '2': {'id': 2, 'vector': np.array([3/5, -4/5])},
                    '3': {'id': 2, 'vector': np.array([1, 1])}}

        self.assertEqual(len(moduleTest.preprocess_taxonomy(TAXONOMY)), 2)
        self.assertIsInstance(moduleTest.preprocess_taxonomy(TAXONOMY), tuple)
        self.assertIsInstance(moduleTest.preprocess_taxonomy(TAXONOMY)[0], list)

        self.assertEqual(moduleTest.preprocess_taxonomy(TAXONOMY)[0], [1, 2, 2])
        self.assertEqual(moduleTest.preprocess_taxonomy(TAXONOMY)[1].shape, (3, 2))

        with self.assertRaises(TypeError):
            moduleTest.preprocess_taxonomy(0)

    def test_compute_scores(self):
        print('\nImport required modules')
        import numpy as np

        array_ingredients = np.array([[1, 1], [3/5, 4/5]])
        LIST_TAXONOMY = [1, 2, 2]
        ARRAY_TAXONOMY = np.array([[3/5, 4/5], [1, 0], [1, 1]], dtype = np.float32)

        print('\nTesting compute_scores...')

        self.assertEqual(len(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)), 2)
        self.assertEqual(len(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)[0]), 2)
        self.assertEqual(len(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)[1]), 2)

        self.assertIsInstance(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY), tuple)
        self.assertIsInstance(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)[0], list)
        self.assertIsInstance(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)[1], list)
        
        self.assertEqual(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)[0], [2, 1]) # Ingredients
        self.assertEqual(moduleTest.compute_scores(array_ingredients, LIST_TAXONOMY, ARRAY_TAXONOMY)[1], [1, 1]) # Score

    def test_create_response_match_ingredients(self):
        print('\nTesting create_response...')

        list_a = ['ing_1', 'ing_2']
        list_b = [2, 1]
        list_b_long = [2, 1, 3]
        list_c = [0.8, 0.9]
        
        self.assertIsInstance(moduleTest.create_response_match_ingredients(list_a, list_b, list_c), list)
        self.assertIsInstance(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[0], dict)

        self.assertEqual(len(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)), 2)
        self.assertEqual(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[0]['ingredient'], 'ing_1')
        self.assertEqual(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[1]['ingredient'], 'ing_2')

        self.assertEqual(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[0]['id'], 2)
        self.assertEqual(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[1]['id'], 1)

        self.assertEqual(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[0]['score'], 0.8)
        self.assertEqual(moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[1]['score'], 0.9)

        with self.assertRaises(Exception):
            moduleTest.create_response_match_ingredients(list_a, list_b_long, list_c)

        with self.assertRaises(IndexError):
            moduleTest.create_response_match_ingredients(list_a, list_b, list_c)[2]

    def test_retrieve_sql_table(self):
        print('\nTesting retrieve_sql_table...')

        # A word of advice: this test is dependant on the state (and connection) to the db. If they fail, it is important to understand if the tables changed.

        tablename = 'pantry__taxonomy'
        tablename_b = 'pantry__stopwords'
        tablename_fail = 'pantry__taxonomy_2'

        self.assertIsInstance(moduleTest.retrieve_sql_table(tablename, db_params = DB_PARAMS), tuple)
        self.assertIsInstance(moduleTest.retrieve_sql_table(tablename_b, db_params = DB_PARAMS), tuple)
        self.assertIsInstance(moduleTest.retrieve_sql_table(tablename, db_params = DB_PARAMS)[0], tuple)
        self.assertIsInstance(moduleTest.retrieve_sql_table(tablename, db_params = DB_PARAMS)[0][0], int)

        with self.assertRaises(Exception):
            moduleTest.retrieve_sql_table(tablename_fail, db_params = DB_PARAMS)

    def test_retrieve_sql_table_filtered(self):
        print('\nTesting retrieve_sql_table_filtered...')

        # A word of advice: this test is dependant on the state (and connection) to the db. If they fail, it is important to understand if the tables changed.

        tablename = 'pantry__taxonomy_ref_values'
        tablename_fail = 'pantry__taxonomy_2'
        set_ids = {1, 2, 3}
        set_ids_empty = {-1}
        select_fields = ['taxonomy_id', 'property_type', 'property', 'reference_value']
        select_fields_short = ['taxonomy_id', 'reference_value']

        self.assertIsInstance(moduleTest.retrieve_sql_table_filtered(tablename, set_ids, select_fields, db_params = DB_PARAMS), tuple)
        self.assertIsInstance(moduleTest.retrieve_sql_table_filtered(tablename, set_ids, select_fields, db_params = DB_PARAMS)[0], tuple)
        self.assertIsInstance(moduleTest.retrieve_sql_table_filtered(tablename, set_ids, select_fields, db_params = DB_PARAMS)[0][0], int)

        self.assertEqual(len(moduleTest.retrieve_sql_table_filtered(tablename, set_ids, select_fields, db_params = DB_PARAMS)[0]), 4)
        self.assertEqual(len(moduleTest.retrieve_sql_table_filtered(tablename, set_ids, select_fields_short, db_params = DB_PARAMS)[0]), 2)
        self.assertEqual(len(moduleTest.retrieve_sql_table_filtered(tablename, set_ids_empty, select_fields, db_params = DB_PARAMS)), 0)

        with self.assertRaises(Exception):
            moduleTest.retrieve_sql_table_filtered(tablename_fail, set_ids, select_fields, db_params = DB_PARAMS)

    def test_parse_stopwords(self):
        print('\nTesting parse_stopwords...')

        tuple_result = ((1, 'alpha'), (2, 'beta'), (3, 'gamma'))
        tuple_wrong = (1, 2)

        self.assertIsInstance(moduleTest.parse_stopwords(tuple_result), list)
        self.assertIsInstance(moduleTest.parse_stopwords(tuple_result)[2], str)

        self.assertEqual(len(moduleTest.parse_stopwords(tuple_result)), 3)
        self.assertEqual(moduleTest.parse_stopwords(tuple_result)[0], 'alpha')
        self.assertEqual(moduleTest.parse_stopwords(tuple_result)[2], 'gamma')

        with self.assertRaises(TypeError):
            moduleTest.parse_stopwords(tuple_wrong)

    def test_parse_taxonomy(self):
        print('\nTesting parse_taxonomy...')

        tuple_taxonomy = ((1, 1, 'crab', '[1, 0]'),
                        (2, 2, 'lobster', '[0.6, 0.8]'),
                        (3, 1, 'crabs', '[1, 1]'))

        self.assertIsInstance(moduleTest.parse_taxonomy(tuple_taxonomy), dict)
        self.assertIsInstance(moduleTest.parse_taxonomy(tuple_taxonomy)[1], dict)
        self.assertIsInstance(moduleTest.parse_taxonomy(tuple_taxonomy)[1]['id'], int)

        self.assertTrue(1 in moduleTest.parse_taxonomy(tuple_taxonomy).keys())
        self.assertFalse(0 in moduleTest.parse_taxonomy(tuple_taxonomy).keys())
        self.assertTrue('id' in moduleTest.parse_taxonomy(tuple_taxonomy)[1].keys())

        self.assertEqual(moduleTest.parse_taxonomy(tuple_taxonomy)[3]['id'], 1)
        self.assertEqual(moduleTest.parse_taxonomy(tuple_taxonomy)[1]['id'], 1)
        self.assertEqual(len(moduleTest.parse_taxonomy(tuple_taxonomy)[2]['vector']), 2)

    def test_encode_allergens(self):
        print('\nTesting encode_allergens...')

        tuple_in = ((1, 'allergen', 'nuts', 1),
                    (1, 'allergen', 'celery', 0),
                    (2, 'macro_nutrient', 'energy', 5))

        self.assertIsInstance(moduleTest.encode_allergens(tuple_in), tuple)
        self.assertIsInstance(moduleTest.encode_allergens(tuple_in)[0], tuple)
        self.assertIsInstance(moduleTest.encode_allergens(tuple_in)[0][0], int)
        self.assertIsInstance(moduleTest.encode_allergens(tuple_in)[0][1], str)
        self.assertIsInstance(moduleTest.encode_allergens(tuple_in)[0][2], str)
        self.assertIsInstance(moduleTest.encode_allergens(tuple_in)[0][3], bool)
        self.assertIsInstance(moduleTest.encode_allergens(tuple_in)[2][3], int)

        self.assertEqual(moduleTest.encode_allergens(tuple_in)[0], (1, 'allergen', 'nuts', True))
        self.assertEqual(moduleTest.encode_allergens(tuple_in)[1], (1, 'allergen', 'celery', False))
        self.assertEqual(moduleTest.encode_allergens(tuple_in)[2], (2, 'macro_nutrient', 'energy', 5))

        self.assertEqual(len(moduleTest.encode_allergens(tuple_in)), 3)
        self.assertEqual(len(moduleTest.encode_allergens(tuple_in)[0]), 4)

    def test_parse_reference_values(self):
        print('\nTesting parse_reference_values...')

        tuple_in = ((1, 'allergen', 'nuts', 1),
                    (1, 'allergen', 'celery', 0),
                    (2, 'macro_nutrient', 'energy', 5))

        self.assertIsInstance(moduleTest.parse_reference_values(tuple_in), dict)
        self.assertIsInstance(moduleTest.parse_reference_values(tuple_in)[1], dict)
        self.assertIsInstance(moduleTest.parse_reference_values(tuple_in)[2], dict)

        self.assertEqual(moduleTest.parse_reference_values(tuple_in)[2], {'energy': 5})
        self.assertEqual(len(moduleTest.parse_reference_values(tuple_in)[1].keys()), 2)

        self.assertTrue(1 in moduleTest.parse_reference_values(tuple_in).keys())
        self.assertFalse(0 in moduleTest.parse_reference_values(tuple_in).keys())

        self.assertTrue('nuts' in moduleTest.parse_reference_values(tuple_in)[1].keys())
        self.assertTrue('celery' in moduleTest.parse_reference_values(tuple_in)[1].keys())
        self.assertFalse('energy' in moduleTest.parse_reference_values(tuple_in)[1].keys())
        self.assertFalse('celery' in moduleTest.parse_reference_values(tuple_in)[2].keys())

    def test_insert_properties(self):
        print('\nTesting insert_properties...')

        list_ids = [1, 2, 3, 2]
        dict_values = {1: {'energy': 5, 'nuts': 0, 'carbs': 3},
                    2: {'energy': 2, 'nuts': 1}}
        KEYS = ['ingredient_ids', 'has_data', 'energy', 'nuts', 'carbs']

        self.assertIsInstance(moduleTest.insert_properties(list_ids, dict_values, KEYS), list)
        self.assertIsInstance(moduleTest.insert_properties(list_ids, dict_values, KEYS)[0], dict)

        self.assertEqual(len(moduleTest.insert_properties(list_ids, dict_values, KEYS)[0].keys()), 5)
        self.assertEqual(moduleTest.insert_properties(list_ids, dict_values, KEYS)[0]['id'], 1)
        self.assertEqual(moduleTest.insert_properties(list_ids, dict_values, KEYS)[1]['id'], 2)
        self.assertEqual(moduleTest.insert_properties(list_ids, dict_values, KEYS)[3]['id'], 2)

        self.assertTrue(moduleTest.insert_properties(list_ids, dict_values, KEYS)[0]['has_data'])
        self.assertFalse(moduleTest.insert_properties(list_ids, dict_values, KEYS)[2]['has_data'])

        self.assertEqual(moduleTest.insert_properties(list_ids, dict_values, KEYS)[0]['energy'], 5)
        self.assertEqual(moduleTest.insert_properties(list_ids, dict_values, KEYS)[1]['energy'], 2)
        self.assertIsNone(moduleTest.insert_properties(list_ids, dict_values, KEYS)[2]['energy'])

        self.assertEqual(moduleTest.insert_properties(list_ids, dict_values, KEYS)[0]['carbs'], 3)
        self.assertIsNone(moduleTest.insert_properties(list_ids, dict_values, KEYS)[1]['carbs'])

    def test_execute_matched_ingredients(self):
        print('\nTesting test_execute_matched_ingredients...')

        ingredient_list = ['Crab BB X1kg', 'Aubergines tractor 500g', 'Oil from avocado']
        expected_ids = [1, 201, 631]

        self.assertIsInstance(moduleTest.execute_matched_ingredients(ingredient_list), list)
        self.assertIsInstance(moduleTest.execute_matched_ingredients(ingredient_list)[0], dict)

        self.assertEqual(len(moduleTest.execute_matched_ingredients(ingredient_list)), 3)
        self.assertEqual(moduleTest.execute_matched_ingredients(ingredient_list)[0]['ingredient'], ingredient_list[0])
        self.assertEqual(moduleTest.execute_matched_ingredients(ingredient_list)[1]['ingredient'], ingredient_list[1])
        self.assertEqual(moduleTest.execute_matched_ingredients(ingredient_list)[2]['id'], expected_ids[2])
        self.assertEqual(moduleTest.execute_matched_ingredients(ingredient_list)[1]['id'], expected_ids[1])
        self.assertTrue(moduleTest.execute_matched_ingredients(ingredient_list)[2]['score'] > 0.9)

        with self.assertRaises(IndexError):
            moduleTest.execute_matched_ingredients(ingredient_list)[3]

    def test_execute_fill_properties(self):
        print('\nTesting execute_fill_properties...')

        list_ingredient_ids = [1, 66, 117, 631, 0] # True, True, False, True, False

        self.assertIsInstance(moduleTest.execute_fill_properties(list_ingredient_ids), list)
        self.assertIsInstance(moduleTest.execute_fill_properties(list_ingredient_ids)[0], dict)
        self.assertIsInstance(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['id'], int)
        self.assertIsInstance(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['has_data'], bool)
        self.assertIsInstance(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['energy'], float)
        self.assertIsInstance(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['fish'], bool)

        self.assertEqual(len(moduleTest.execute_fill_properties(list_ingredient_ids)), 5)
        self.assertEqual(len(moduleTest.execute_fill_properties(list_ingredient_ids)[0].keys()), 36)

        self.assertEqual(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['id'], list_ingredient_ids[0])
        self.assertEqual(moduleTest.execute_fill_properties(list_ingredient_ids)[1]['id'], list_ingredient_ids[1])
        self.assertEqual(moduleTest.execute_fill_properties(list_ingredient_ids)[2]['id'], list_ingredient_ids[2])

        self.assertTrue(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['has_data'])
        self.assertTrue(moduleTest.execute_fill_properties(list_ingredient_ids)[1]['has_data'])
        self.assertFalse(moduleTest.execute_fill_properties(list_ingredient_ids)[2]['has_data'])

        self.assertEqual(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['energy'], 97)
        self.assertIsNone(moduleTest.execute_fill_properties(list_ingredient_ids)[1]['energy'])
        self.assertIsNone(moduleTest.execute_fill_properties(list_ingredient_ids)[4]['energy'])

        self.assertFalse(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['nuts'])
        self.assertFalse(moduleTest.execute_fill_properties(list_ingredient_ids)[1]['nuts'])
        self.assertIsNone(moduleTest.execute_fill_properties(list_ingredient_ids)[4]['nuts'])

        self.assertTrue(moduleTest.execute_fill_properties(list_ingredient_ids)[0]['crustaceans'])
        self.assertFalse(moduleTest.execute_fill_properties(list_ingredient_ids)[1]['crustaceans'])
        self.assertIsNone(moduleTest.execute_fill_properties(list_ingredient_ids)[4]['crustaceans'])        
        

if __name__ == '__main__':
    unittest.main()