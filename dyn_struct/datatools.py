from inspect import signature

import django.forms


def get_django_fields():
    return django.forms.fields.__all__


def get_django_widgets():
    return django.forms.widgets.__all__


def get_item_arguments(item):
    arguments = list(
        set(list(signature(item).parameters.keys()) + list(signature(django.forms.Field.__init__).parameters.keys()))
    )

    return arguments
