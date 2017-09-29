import factory
import factory.fuzzy
from .db import models


class DynamicStructure(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DynamicStructure

    name = factory.fuzzy.FuzzyText(length=10, prefix='test_dyn_struct_')


class DynamicStructureField(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DynamicStructureField

    header = factory.fuzzy.FuzzyText(length=10, prefix='test_header_field_')
    name = factory.fuzzy.FuzzyText(length=10, prefix='test_name_field_')
    row = factory.fuzzy.FuzzyInteger(0, 100)
    position = factory.fuzzy.FuzzyInteger(0, 50)