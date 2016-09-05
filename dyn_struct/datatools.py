# coding: utf-8

import django.forms
from dyn_struct.exceptions import CheckClassArgumentsException


def get_django_fields():
    return django.forms.fields.__all__


def get_django_widgets():
    return django.forms.widgets.__all__


def get_all_bases_classes(class_obj, base_classes=None):
    if base_classes is None:
        base_classes = [class_obj, ]

    bases = [base_class for base_class in class_obj.__bases__ if base_class is not object]

    if bases:
        for base_class in class_obj.__bases__:
            if base_class != object:
                base_classes.extend(get_all_bases_classes(base_class, bases))

    return base_classes


def check_class_arguments(cls, kwargs):
    classes = get_all_bases_classes(cls)

    classes_params = []
    for class_obj in classes:
        classes_params.extend(class_obj.__init__.__code__.co_varnames)
    available_arg_names = set([param for param in classes_params if param not in ['args', 'kwargs', 'self']])

    kwargs_names = set(kwargs.keys())

    error_keys = kwargs_names - available_arg_names
    if error_keys:
        raise CheckClassArgumentsException(
            '{0} - неизвестные ключи для {2}. Выбирайте необходимые из {1}'.format(
                ', '.join(error_keys),
                ', '.join(available_arg_names),
                cls
            )
        )
