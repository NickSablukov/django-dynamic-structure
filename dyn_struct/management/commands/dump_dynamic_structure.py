import json

from django.core.management.base import BaseCommand

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

        structures_data = []
        for struct in structures.iterator():
            struct_info = {
                'name': struct.name,
                'version': struct.version,
                'fields': self.get_fields_data(struct)
            }

            if not is_compact:
                struct_info['is_deprecated'] = struct.is_deprecated

            structures_data.append(struct_info)

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

    def get_fields_data(self, struct):
        fields_data = []
        for field in struct.fields.all():
            fields_data.append({
                'header': field.header,
                'name': field.name,
                'form_field': field.form_field,
                'form_kwargs': field.form_kwargs,
                'widget': field.widget,
                'widget_kwargs': field.widget_kwargs,
                'row': field.row,
                'position': field.position,
                'classes': field.classes,
            })

        return fields_data
