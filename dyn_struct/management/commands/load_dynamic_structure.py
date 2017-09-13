import json

from django.core.management.base import BaseCommand

from dyn_struct.db import models


class Command(BaseCommand):
    help = 'Load dynamic structure'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', dest='file', type=str)

    def handle(self, *args, **options):
        print('Load ... ', end='')
        with open(options['file'], 'r') as file:
            structs_data = json.loads(file.read())

        for struct_info in structs_data:
            struct, _, = models.DynamicStructure.objects.get_or_create(
                name=struct_info.get('name'),
                version=struct_info.get('version'),
            )
            for field_info in struct_info['fields']:
                models.DynamicStructureField.objects.get_or_create(
                    structure=struct, **field_info
                )

        print('Success!')
