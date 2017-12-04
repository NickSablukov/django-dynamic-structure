from django.core.exceptions import ValidationError
from django.test import TestCase

from dyn_struct.db import validators


class ParamsValidatorTest(TestCase):

    def test_call(self):
        test_dict = '{"test_key": "test"}'
        params_field = validators.ParamsValidator()
        self.assertIsNone(params_field(test_dict))

    def test_call_with_json_exception(self):
        params_field = validators.ParamsValidator()
        with self.assertRaises(ValidationError) as ex:
            params_field({'test': 123})
        self.assertIn('Введите корректные JSON данные.', ex.exception)
        self.assertEqual('invalid', ex.exception.code)

    def test_call_with_type_error(self):
        params_field = validators.ParamsValidator()
        with self.assertRaises(ValidationError) as ex:
            params_field('123')
        self.assertIn('Данные должны иметь вид {"ключ": значение}.', ex.exception)
        self.assertEqual('invalid', ex.exception.code)