from django.test import TestCase
from dyn_struct import factories
from dyn_struct.db.models import DynamicStructure, DynamicStructureField


class BaseModels(TestCase):
    def setUp(self):
        self.dyn_stuct = factories.DynamicStructure()
        factories.DynamicStructureField.create_batch(size=10, structure=self.dyn_stuct)


class DynamicStructureTestCase(BaseModels):
    def test_str(self):
        name = "test_structure"
        dyn_stuct = factories.DynamicStructure(name=name)
        self.assertEqual(name, str(dyn_stuct))

    def test_unicode(self):
        name = "test_structure"
        dyn_stuct = factories.DynamicStructure(name=name)
        self.assertEqual(name, dyn_stuct.__unicode__())

    def test_get_field_names(self):
        dyn_struct_field_names = self.dyn_stuct.get_field_names()
        self.assertIsInstance(dyn_struct_field_names, list)
        fields = DynamicStructureField.objects.filter(structure=self.dyn_stuct)
        self.assertEqual(len(dyn_struct_field_names), fields.count())
        for f in fields:
            self.assertIn(f.name, dyn_struct_field_names)

    def test_clone_check_structure(self):
        old_id = self.dyn_stuct.id
        self.dyn_stuct.is_deprecated = False
        self.dyn_stuct.save()
        self.assertEqual(self.dyn_stuct.is_deprecated, False)
        self.assertIn(self.dyn_stuct, DynamicStructure.objects.all())

        self.dyn_stuct.clone()

        self.assertNotEqual(old_id, self.dyn_stuct)
        self.assertIn(self.dyn_stuct, DynamicStructure.objects.all())

        old_dyn_stuct = DynamicStructure.standard_objects.filter(id=old_id).last()
        self.assertEqual(old_dyn_stuct.is_deprecated, True)
        self.assertEqual(self.dyn_stuct.version - 1, old_dyn_stuct.version)

    def test_clone_without_exclude_field(self):
        count_fields_create = 10
        old_id = self.dyn_stuct.id

        DynamicStructureField.objects.all().delete()
        self.assertFalse(DynamicStructureField.objects.all())
        factories.DynamicStructureField.create_batch(size=count_fields_create, structure=self.dyn_stuct)
        self.assertEqual(DynamicStructureField.objects.all().count(), count_fields_create)
        self.assertEqual(self.dyn_stuct.fields.count(), count_fields_create)

        self.dyn_stuct.clone()

        self.assertEqual(DynamicStructureField.objects.all().count(), count_fields_create * 2)
        old_dyn_stuct = DynamicStructure.standard_objects.filter(id=old_id).last()
        self.assertEqual(self.dyn_stuct.get_field_names(), old_dyn_stuct.get_field_names())
        self.assertEqual(self.dyn_stuct.fields.count(), count_fields_create, old_dyn_stuct.fields.count())


    def test_delete(self):
        self.dyn_stuct.is_deprecated = False
        self.dyn_stuct.save()
        self.assertEqual(self.dyn_stuct.is_deprecated, False)
        self.dyn_stuct.delete()
        self.assertEqual(self.dyn_stuct.is_deprecated, True)