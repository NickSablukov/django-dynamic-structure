from unittest import mock

from django.forms.models import modelform_factory
from django.test import TestCase
from dyn_struct import factories
from dyn_struct.db import models
from dyn_struct.forms import DynamicStructureForm, DynamicField, DynamicWidget


class DynamicWidgetTest(TestCase):
    def setUp(self):
        super().setUp()
        self.dynamic_structure = factories.DynamicStructure()

    def test_init_without_template(self):
        form = DynamicWidget()
        self.assertIsNone(form.inner_form)
        self.assertIsNone(form.dynamic_structure)

    def test_init_with_template(self):
        test_template = 'test_template'
        form = DynamicWidget(template=test_template)
        self.assertEqual(form.template, test_template)


class DynamicStructureFormTest(TestCase):

    def setUp(self):
        self.dyn_struct, self.test_obj = factories.DynamicStructure.create_batch(size=2)

    def test_init(self):
        test_form = modelform_factory(models.DynamicStructure, form=DynamicStructureForm, fields=('name',))
        form = test_form(dynamic_structure_name=self.dyn_struct.name)
        self.assertEqual(form.fields['data'].widget.dynamic_structure.name, self.dyn_struct.name)
        self.assertEqual(form.fields['data'].widget.template, 'bootstrap3')

    def test_init_with_dynamic_template(self):
        test_template = 'test_template'
        test_form = modelform_factory(models.DynamicStructure, form=DynamicStructureForm, fields=('name',))
        form = test_form(dynamic_structure_name=self.dyn_struct.name,
                         dynamic_template=test_template)
        self.assertEqual(form.fields['data'].widget.template, test_template)
