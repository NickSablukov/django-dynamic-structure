# coding: utf-8
from inspect import signature

import django.forms
from dyn_struct.exceptions import CheckClassArgumentsException


def get_django_fields():
    return django.forms.fields.__all__


def get_django_widgets():
    return django.forms.widgets.__all__


def check_class_arguments(class_obj, kwargs):




    available_arg_names = set(list(signature(class_obj).parameters.keys()))
    kwargs_names = set(kwargs.keys())

    error_keys = kwargs_names - available_arg_names
    if error_keys:
        raise CheckClassArgumentsException(
            '{0} - неизвестные ключи для {2}. Выбирайте необходимые из {1}'.format(
                ', '.join(error_keys),
                ', '.join(available_arg_names),
                class_obj
            )
        )
