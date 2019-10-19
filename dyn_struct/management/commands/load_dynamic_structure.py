import json

from django.core.management.base import BaseCommand

from dyn_struct.datatools import structure_from_dict


class Command(BaseCommand):
    help = 'Load dynamic structure'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', dest='file', type=str)

    def handle(self, *args, **options):
        print('Load ... ')
        with open(options['file'], 'r') as file:
            structs_data = json.loads(file.read())

        for struct_info in structs_data:
            structure_from_dict(struct_info)

        print('Success!')
