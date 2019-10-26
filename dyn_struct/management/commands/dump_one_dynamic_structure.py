import json

from django.core.management.base import BaseCommand

from dyn_struct.datatools import structure_to_dict
from dyn_struct.db import models


class Command(BaseCommand):
    help = 'Dump dynamic structure'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', dest='id')
        parser.add_argument('-n', '--name', dest='name')

    def handle(self, *args, **options):
        assert options.get('id') or options.get('name')
        instance_id = options.get('id')
        name = options.get('name')

        if instance_id:
            structure = models.DynamicStructure.objects.get(id=instance_id)
        else:
            structure = models.DynamicStructure.objects.get(name=name)

        structures_data = structure_to_dict(structure)
        dumped_data = json.dumps(structures_data, indent=2, ensure_ascii=False)
        dumped_data = dumped_data.encode('utf-8').decode('utf-8')

        print(dumped_data)
