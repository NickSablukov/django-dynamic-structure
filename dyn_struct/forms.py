# coding: utf-8
import six
import json

from django import forms
from django.core.exceptions import ValidationError
from django.template import Template, Context

from dyn_struct.db import models


class DynamicWidget(forms.Widget):

    def __init__(self, *args, **kwargs):
        self.template = kwargs.pop('template', 'bootstrap3')
        super(DynamicWidget, self).__init__(*args, **kwargs)
        self.dynamic_structure = None
        self.inner_form = None

    def render(self, name, value, attrs=None, renderer=None):
        assert self.dynamic_structure is not None

        if value and isinstance(value, six.string_types):
            value = json.loads(value)['form_data']

        data = None
        if value:
            data = {}
            for key in value.keys():
                inner_key = name + '-' + key
                data[inner_key] = value[key]

        template = Template('{% load dyn_struct %} {% render_struct structure prefix value template %}')
        context = Context({
            'structure': self.dynamic_structure,
            'prefix': name,
            'value': data,
            'template': self.template,
        })
        return template.render(context)

    def value_from_datadict(self, data, files, name):
        assert self.dynamic_structure is not None

        self._build_inner_form(prefix=name, data=data)
        value = {}
        for field_name in self.inner_form.fields.keys():
            name_with_prefix = name + '-' + field_name
            field_widget = self.inner_form.fields[field_name].widget
            value[field_name] = field_widget.value_from_datadict(data=data, files=files, name=name_with_prefix)
        return value

    def _build_inner_form(self, prefix, data):
        self.inner_form = self.dynamic_structure.build_form(data=data, prefix=prefix)


class DynamicField(forms.Field):
    widget = DynamicWidget

    def clean(self, data, initial=None):
        # удобные для отображения данные формы
        verbose_data = []
        for field in self.widget.dynamic_structure.fields.all():
            item = {
                'row': field.row,
                'position': field.position,
                'is_header': field.is_header(),
                'name': field.name or field.header,
                'value': None,
                'classes': field.classes,
            }
            if not field.is_header():
                item['value'] = data[field.get_transliterate_name()]
            verbose_data.append(item)

        dynamic_data = {
            'structure': self.widget.dynamic_structure.name,
            'version': self.widget.dynamic_structure.version,
            'form_data': data,
            'verbose_data': verbose_data,
        }

        json_data = json.dumps(dynamic_data)
        cleaned_data = json.loads(super(DynamicField, self).clean(json_data))

        if not self.widget.inner_form.is_valid():
            msg = ''
            for field_name, errors in self.widget.inner_form.errors.items():
                msg += field_name + ': ' + ', '.join(errors) + '\n'
            raise ValidationError(msg)

        return json.dumps(cleaned_data, indent=4, ensure_ascii=False)


class DynamicStructureForm(forms.ModelForm):
    data = DynamicField(label='')

    def __init__(self, *args, **kwargs):
        dynamic_structure_name = kwargs.pop('dynamic_structure_name')
        dynamic_template = kwargs.pop('dynamic_template', None)

        super(DynamicStructureForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id and self.instance.data:
            data = json.loads(self.instance.data)
            dynamic_structure_name = data['structure']
            version = data['version']

            dynamic_structure = models.DynamicStructure.standard_objects.get(
                version=version,
                name=dynamic_structure_name
            )
        else:
            dynamic_structure = models.DynamicStructure.objects.get(name=dynamic_structure_name)
        self.fields['data'].widget.dynamic_structure = dynamic_structure

        if dynamic_template:
            self.fields['data'].widget.template = dynamic_template
