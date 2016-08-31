import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from itertools import groupby

from .db import models


class DynamicWidget(forms.Widget):
    def render(self, base_name, value, attrs=None):  # TODO почему то иногда не работает группировка по строкам

        def set_name(field_data):
            field_object = field_data[1]
            field_name = field_data[0]

            if not (type(field_object) is str):
                field_object.name = field_name

            return field_object

        get_dynamic_object = self.attrs['get_dynamic_object']
        dynamic_object = get_dynamic_object()

        field_rows = groupby(map(set_name, dynamic_object.build_fields().items()), key=lambda field: field.row)
        field_rows = [list(i) for o, i in field_rows]
        field_rows.sort(key=lambda data: data[0].row)

        rendered_fields = '<div id="dynamic_object"><div class="row">'
        for field_row in field_rows:
            row = """
                    <div class="row">
                        {cols}
                    </div>
                """
            cols = ""
            for field in field_row:
                if isinstance(field, models.DynamicObjectField):
                    cols += '<h4>{}</h4><br>'.format(field.header)
                else:
                    field_name = '{0}_{1}'.format(base_name, field.name)
                    field_value = value[field.name] if value else None
                    cols += \
                        """
                            <div class="form-group {classes}">
                                <p><label class="control-label" for="id_{row_name}">{label}</label></p>
                                {render_input}
                            </div>
                        """.format(
                            render_input=field.widget.render(
                                name=field_name,
                                value=field_value,
                                attrs={'class': 'form-control'}
                            ),
                            classes=field.classes,
                            row_name=field_name,
                            label=field.label
                        )

            rendered_fields += row.format(cols=cols)
        rendered_fields += '</div></div>'

        return format_html(rendered_fields)

    def value_from_datadict(self, data, files, base_name):
        names = self.attrs['get_dynamic_object']().build_fields().keys()
        value = {name: data.get('{0}_{1}'.format(self.attrs['base_name'], name), None) for name in names if name}
        return value


class DynamicField(forms.Field):
    widget = DynamicWidget
    FIELD_NAME = 'data'

    def widget_attrs(self, widget):
        return {
            'get_dynamic_object': self.get_dynamic_object,
            'base_name': self.FIELD_NAME
        }

    def __init__(self, *args, dynamic_object, **kwargs):
        self.dynamic_object = dynamic_object
        super().__init__(*args, **kwargs)

    def get_dynamic_object(self):
        return self.dynamic_object

    def clean(self, data, initial=None):
        json_data = json.dumps(data)
        cleaned_data = json.loads(super().clean(json_data))
        field_names = cleaned_data.keys()

        fields = models.DynamicObjectField.objects.filter(dynamic_object=self.get_dynamic_object())

        exceptions = []
        for name in field_names:
            field = fields.get(name=name)
            django_field = field.build()
            try:
                django_field.clean(cleaned_data[name])
            except ValidationError as e:
                exceptions.append(e)

        if exceptions:
            raise ValidationError(*exceptions)

        return json.dumps(cleaned_data, indent=4)


class DynamicModelForm(forms.ModelForm):
    data = DynamicField(dynamic_object=None)

    def __init__(self, *args, dynamic_object, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_fields['data'].dynamic_object = dynamic_object
