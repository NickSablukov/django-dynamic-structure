from django import forms
from django.test import TestCase

import dyn_struct.datatools


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