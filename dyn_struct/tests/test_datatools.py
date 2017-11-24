from django import forms
from django.test import TestCase

import dyn_struct.datatools
from dyn_struct.exceptions import CheckClassArgumentsException


class DatatoolsTest(TestCase):
    def test_get_django_fields(self):
        all_django_fields = dyn_struct.datatools.get_django_fields()
        self.assertIn('DateField', all_django_fields)
        self.assertIn('CharField', all_django_fields)
        self.assertNotIn('MyTestField', all_django_fields)

    def test_get_django_widgets(self):
        all_django_widgets = dyn_struct.datatools.get_django_widgets()
        self.assertIn('TextInput', all_django_widgets)
        self.assertIn('Select', all_django_widgets)
        self.assertNotIn('MyTestWidget', all_django_widgets)

    def test_get_all_bases_classes_with_one_base_class(self):
        class_obj = getattr(forms.fields, 'Field')
        base_classes = dyn_struct.datatools.get_all_bases_classes(class_obj)
        self.assertIn(class_obj, base_classes)
        self.assertListEqual([class_obj], base_classes)

    def test_get_all_bases_classes_with_more_Than_one_base_class(self):
        class_obj = getattr(forms.fields, 'CharField')
        base_classes = dyn_struct.datatools.get_all_bases_classes(class_obj)
        self.assertIn(class_obj, base_classes)
        self.assertGreater(len(base_classes), 1)

    def test_get_all_bases_classes_with_base_classes(self):
        class_obj = getattr(forms.fields, 'EmailField')
        base_class = getattr(forms.fields, 'FileField')
        base_classes = dyn_struct.datatools.get_all_bases_classes(class_obj, [base_class])
        self.assertNotIn(class_obj, base_classes)
        self.assertIn(base_class, base_classes)

    def test_check_class_arguments_without_error(self):
        class_obj = getattr(forms.fields, 'EmailField')
        self.assertIsNone(dyn_struct.datatools.check_class_arguments(class_obj, {}))
        self.assertIsNone(dyn_struct.datatools.check_class_arguments(class_obj, {'label': 'test_label_email'}))

    def test_check_class_arguments_with_one_error_key(self):
        error_key = 'error_key'
        class_obj = getattr(forms.fields, 'EmailField')
        with self.assertRaises(CheckClassArgumentsException) as ex:
            dyn_struct.datatools.check_class_arguments(class_obj, {error_key: 'test_error'})
        self.assertIn('{0} - неизвестные ключи для {1}. Выбирайте необходимые из'.format(error_key,class_obj),
                      str(ex.exception))

    def test_check_class_arguments_with_error_keys(self):
        error_key1 = 'error_key1'
        error_key2 = 'error_key2'
        class_obj = getattr(forms.fields, 'EmailField')
        with self.assertRaises(CheckClassArgumentsException) as ex:
            dyn_struct.datatools.check_class_arguments(class_obj, {error_key1: 'test_error', error_key2: 'test_error2'})
        self.assertIn(error_key1, str(ex.exception))
        self.assertIn(error_key2, str(ex.exception))