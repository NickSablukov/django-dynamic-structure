# coding: utf-8
import json

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text


@deconstructible
class ParamsValidator(object):
    json_valid_error_message = 'Введите корректные JSON данные.'
    dict_valid_error_message = 'Данные должны иметь вид {"ключ": значение}.'
    code = 'invalid'

    def __call__(self, value):
        value = force_text(value)

        try:
            dict(json.loads(value))
        except json.JSONDecodeError:
            raise ValidationError(self.json_valid_error_message, code=self.code)
        except TypeError:
            raise ValidationError(self.dict_valid_error_message, code=self.code)
