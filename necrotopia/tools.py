from numbers import Number
from decimal import Decimal


class DictionaryTool:
    @staticmethod
    def add_or_update(key, value, dictionary: {}):
        dictionary[key] = value

    @staticmethod
    def contains_key(key, dictionary_1: {}) -> bool:
        result = False

        if dictionary_1 is not None and len(dictionary_1) > 0:
            result = key in dictionary_1

        return result

    @staticmethod
    def is_number(value):
        return isinstance(value, Number) or isinstance(value, Decimal)

    @staticmethod
    def mergeDictionary(dict_1: {}, dict_2: {}) -> {}:
        """
            This function will merge two dictionaries. In the case of matching keys, if the values are numeric (integer or decimal)
            the values will be summed together. None and non-numeric values are not retained and are ignored. The resulting merged
            and summed dictionary will be returned
            So that if:
               x = {'x': 1, 'y': 5, 'z': 10}
               y = {'x': 2, 'z': 5}
               result = {'x': 3, 'y': 5, 'z': 15}

            And also if:
               x = {'x': 1, 'y': 'I love a good party'', 'z': 10}
               y = {'x': 2, 'z': 5}
               result = {'x': 3, 'z': 15}

        :param dict_1: the first dictionary
        :param dict_2: the second dictionary
        :return: a dictionary containing the keys and values of the first two merged together as noted above.
        """
        result = {**dict_1, **dict_2}
        for key, value in result.items():
            if key in dict_1 and key in dict_2:
                if DictionaryTool.is_number(dict_1[key]) and DictionaryTool.is_number(dict_2[key]):
                    result[key] = dict_1[key] + dict_2[key]

        return result
