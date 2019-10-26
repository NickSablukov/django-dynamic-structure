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


def structure_to_dict(struct, is_compact=True):
    struct_info = {
        'name': struct.name,
        'version': struct.version,
        'fields': get_structure_fields_data(struct=struct)
    }

    if not is_compact:
        struct_info['is_deprecated'] = struct.is_deprecated
    return struct_info


def structure_from_dict(struct_info, use_local_version=False, struct_name=None):
    """
    Получение (создание) структуры из словаря
    :param struct_info: словарь с параметрами структуры
    :param use_local_version: нужно ли использовать локальное версионирование (т.е. не брать в расчет версию из файла)
    :param struct_name: название структуры (по-умолчанию берется из файла)
    :return:
    """
    from dyn_struct.db import models

    name = struct_name or struct_info.get('name')

    if use_local_version:
        struct, created = models.DynamicStructure.objects.get_or_create(name=name)

        if not created:
            struct.clone()
            struct = models.DynamicStructure.objects.get(name=name)
    else:
        version = struct_info.get('version', 1)
        struct, _, = models.DynamicStructure.objects.get_or_create(
            name=name,
            version=version,
            is_deprecated=struct_info.get('is_deprecated', False)
        )

    for field_info in struct_info['fields']:
        models.DynamicStructureField.objects.get_or_create(
            structure=struct, **field_info
        )

    models.DynamicStructure.objects.filter(name=name, version__lt=struct.version).update(is_deprecated=True)
    return struct


def get_structure_fields_data(struct):
    fields_data = []
    for field in struct.fields.all():
        fields_data.append({
            'header': field.header,
            'name': field.name,
            'form_field': field.form_field,
            'form_kwargs': field.form_kwargs,
            'widget': field.widget,
            'widget_kwargs': field.widget_kwargs,
            'row': field.row,
            'position': field.position,
            'classes': field.classes,
        })

    return fields_data
