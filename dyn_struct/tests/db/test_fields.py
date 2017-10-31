from unittest import mock

from django.test import TestCase

from dyn_struct.db import fields


class ParamsFieldTest(TestCase):

    @mock.patch('dyn_struct.db.validators.ParamsValidator')
    def test_validators(self, mock_params):
        test_dict = {'test_key': 'test'}
        mock_params.return_value = test_dict
        params_field = fields.ParamsField()
        self.assertIn(test_dict, params_field.validators)
        self.assertTrue(mock_params.called)
