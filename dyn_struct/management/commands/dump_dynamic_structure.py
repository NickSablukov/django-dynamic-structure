import json

from django.core.management.base import BaseCommand

from dyn_struct.datatools import structure_to_dict
from dyn_struct.db import models


class Command(BaseCommand):
    help = 'Dump dynamic structure'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--indent', dest='indent', type=int)
        parser.add_argument('-s', '--sorted', dest='sorted', default=False, action='store_true')
        parser.add_argument('-c', '--compact', dest='compact', default=False, action='store_true')
        parser.add_argument('-p', '--pretty', dest='pretty', default=False, action='store_true')

    def handle(self, *args, **options):
        is_compact = options['compact']

        structures = models.DynamicStructure.objects.all()
        if is_compact:
            structures = structures.filter(is_deprecated=False)

        structures_data = [structure_to_dict(struct, is_compact=is_compact) for struct in structures.iterator()]
        pretty = options['pretty']
        dump_kwargs = {
            'sort_keys': options['sorted']
        }
        if options['indent'] is not None:
            dump_kwargs['indent'] = options['indent']

        if pretty:
            dump_kwargs['ensure_ascii'] = False

        dumped_data = json.dumps(structures_data, **dump_kwargs)
        if pretty:
            dumped_data = dumped_data.encode('utf-8').decode('utf-8')

        print(dumped_data)
