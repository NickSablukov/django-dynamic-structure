import factory
import factory.fuzzy

from .db import models


FORM_FIELD_CHOICES = ['CharField', 'IntegerField', 'DateField', 'EmailField', 'BooleanField']


class DynamicStructure(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DynamicStructure

    name = factory.fuzzy.FuzzyText(length=10, prefix='test_dyn_struct_')


class DynamicStructureField(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DynamicStructureField

    header = factory.fuzzy.FuzzyText(length=10, prefix='test_header_field_')
    name = factory.fuzzy.FuzzyText(length=10, prefix='test_name_field_')
    form_field = factory.fuzzy.FuzzyChoice(FORM_FIELD_CHOICES)
    row = factory.fuzzy.FuzzyInteger(0, 5)
    position = factory.fuzzy.FuzzyInteger(0, 10)