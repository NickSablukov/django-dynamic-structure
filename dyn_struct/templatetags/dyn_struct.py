import six
import json

from django import template

register = template.Library()


@register.inclusion_tag('dyn_struct/render_struct.html')
def render_struct(structure_obj, prefix, value=None):
    if value and isinstance(value, basestring):
        value = json.loads(value)

    rows = structure_obj.get_rows()

    if value:
        for row in rows:
            for field in row:
                if field.form_field:
                    field.initial = value.get(field.name)

    return {
        'rows': rows,
        'prefix': prefix,
    }


@register.inclusion_tag('dyn_struct/render_struct_field.html')
def render_struct_field(struct_field, prefix, value=None):
    field_name = six.u(prefix) + '_' + struct_field.name

    form_field = struct_field.build()
    rendered_input = form_field.widget.render(
        name=field_name,
        value=value,
        attrs={'class': 'form-control'}
    )

    return {
        'classes': struct_field.classes,
        'item': form_field,
        'rendered_input': rendered_input,
        'name': field_name,
    }


