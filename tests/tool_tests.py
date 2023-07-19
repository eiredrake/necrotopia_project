import unittest

from necrotopia.tools import DictionaryTool


class TestDictionaryMergeTool(unittest.TestCase):
    def test_basic_integer_merge(self):
        dictionary_1 = {'x': 1, 'y': 5}
        dictionary_2 = {'x': 3, 'y': 10, 'z': 5}
        expected_results = {'x': 4, 'y': 15, 'z': 5}

        results = DictionaryTool.mergeDictionary(dictionary_1, dictionary_2)
        self.assertEqual(results, expected_results)

    def test_basic_decimal_merge(self):
        dictionary_1 = {'x': 1.5, 'y': 5.1}
        dictionary_2 = {'x': 3.5, 'y': 10.4, 'z': 5}
        expected_results = {'x': 5, 'y': 15.5, 'z': 5}

        results = DictionaryTool.mergeDictionary(dictionary_1, dictionary_2)
        self.assertEqual(results, expected_results)

    def test_mixed_integer_and_decimal_merge(self):
        dictionary_1 = {'x': 1, 'y': 5.1}
        dictionary_2 = {'x': 3.5, 'y': 10, 'z': 5}
        expected_results = {'x': 4.5, 'y': 15.1, 'z': 5}

        results = DictionaryTool.mergeDictionary(dictionary_1, dictionary_2)
        self.assertEqual(results, expected_results)

    def test_mixed_numerics_and_strings_merge(self):
        dictionary_1 = {'x': 1, 'y': 'I love a good party'}
        dictionary_2 = {'x': 3.5, 'y': 10, 'z': 5}
        expected_results = {'x': 4.5, 'y': 10, 'z': 5}

        results = DictionaryTool.mergeDictionary(dictionary_1, dictionary_2)
        self.assertEqual(results, expected_results)

    def test_dictionary_contains_positive(self):
        dictionary = {'x': 1, 'y': 2}

        self.assertTrue(DictionaryTool.contains_key('x', dictionary), "Dictionary positive contains check failed")

    def test_dictionary_contains_false(self):
        dictionary = {'x': 1, 'y': 2}

        self.assertFalse(DictionaryTool.contains_key('bob', dictionary), "Dictionary negative contains check failed")

    def test_dictionary_add(self):
        dictionary = {'x': 1, 'y': 2}
        expected_result = {'x': 1, 'y': 2, 'bob': 'yer uncle'}

        DictionaryTool.add_or_update('bob', 'yer uncle', dictionary)

        self.assertEqual(dictionary, expected_result)

    def test_dictionary_update(self):
        dictionary = {'x': 1, 'y': 2, 'bob': 'is your brother'}
        expected_result = {'x': 1, 'y': 2, 'bob': 'yer uncle'}

        DictionaryTool.add_or_update('bob', 'yer uncle', dictionary)

        self.assertEqual(dictionary, expected_result)


if __name__ == '__main__':
    unittest.main()
