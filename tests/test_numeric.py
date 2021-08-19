from __future__ import annotations
from unittest import TestCase
from jsonclasses.exceptions import ValidationException
from tests.classes.product_with_numeric import NumericProductId


class TestDigit(TestCase):

    def test_numeric_doesnt_raise_if_value_is_numeric(self):
        analysis = NumericProductId(product_name='water', product_id='12345')
        analysis.validate()

    def test_numeric_doesnt_raise_if_value_is_numeric_in_unicode(self):
        analysis = NumericProductId(product_name='water', product_id='\u00BC')
        analysis.validate()

    def test_numeric_raises_if_value_is_float(self):
        analysis = NumericProductId(product_name='water', product_id='12.1')
        with self.assertRaises(ValidationException) as context:
            analysis.validate()
        self.assertEqual(len(context.exception.keypath_messages), 1)
        self.assertEqual(context.exception.keypath_messages['product_id'],
                         "product_id '12.1' at 'product_id' is not a numeric.")

    def test_numeric_raises_if_value_contains_alphabet(self):
        analysis = NumericProductId(product_name='water', product_id='12a')
        with self.assertRaises(ValidationException) as context:
            analysis.validate()
        self.assertEqual(len(context.exception.keypath_messages), 1)
        self.assertEqual(context.exception.keypath_messages['product_id'],
                         "product_id '12a' at 'product_id' is not a numeric.")

    def test_numeric_raises_if_value_contains_special_characters(self):
        analysis = NumericProductId(product_name='water', product_id='12!')
        with self.assertRaises(ValidationException) as context:
            analysis.validate()
        self.assertEqual(len(context.exception.keypath_messages), 1)
        self.assertEqual(context.exception.keypath_messages['product_id'],
                         "product_id '12!' at 'product_id' is not a numeric.")