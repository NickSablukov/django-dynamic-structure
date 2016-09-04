import six
import json

from django import forms
from django.core.exceptions import ValidationError
from django.template import Template, Context

from dyn_struct.db import models


class DynamicWidget(forms.Widget):

    def __init__(self, *args, **kwargs):
        super(DynamicWidget, self).__init__(*args, **kwargs)
        self.dynamic_structure = None

    def render(self, name, value, attrs=None):
        assert self.dynamic_structure is not None

        template = Template('{% load dyn_struct %} {% render_struct structure prefix value %}')
        context = Context({
            'structure': self.dynamic_structure,
            'prefix': name,
            'value': value,
        })
        return template.render(context)

    def value_from_datadict(self, data, files, name):
        dynamic_names = self.dynamic_structure.get_field_names()
        value = {dynamic_name: data.get(six.u(name) + '_' + dynamic_name, None)
                 for dynamic_name in dynamic_names if dynamic_name}
        return value


class DynamicField(forms.Field):
    widget = DynamicWidget

    def clean(self, data, initial=None):
        json_data = json.dumps(data)
        cleaned_data = json.loads(super(DynamicField, self).clean(json_data))
        field_names = cleaned_data.keys()

        fields = models.DynamicStructureField.objects.filter(structure=self.widget.dynamic_structure)

        exception_messages = []
        for name in field_names:
            field = fields.get(name=name)
            django_field = field.build()
            try:
                django_field.clean(cleaned_data[name])
            except ValidationError as e:
                exception_messages.append(e.message)

        if exception_messages:
            raise ValidationError('\n'.join(exception_messages))

        return json.dumps(cleaned_data, indent=4)


class DynamicStructureForm(forms.ModelForm):
    data = DynamicField(label='')

    def __init__(self, *args, **kwargs):
        dynamic_structure = kwargs.pop('dynamic_structure')
        super(DynamicStructureForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.dynamic_structure = dynamic_structure
