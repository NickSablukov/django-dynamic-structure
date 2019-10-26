import json

from django.core.management.base import BaseCommand

from dyn_struct.datatools import structure_from_dict


class Command(BaseCommand):
    help = 'Load dynamic structure'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', dest='file', type=str, required=True)

    def handle(self, *args, **options):
        print('Load ... ')
        with open(options['file'], 'r') as file:
            structs_data = json.loads(file.read())

        structure_from_dict(structs_data)

        print('Success!')
