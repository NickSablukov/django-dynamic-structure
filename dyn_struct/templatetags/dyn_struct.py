import six
import json
import django.template

register = django.template.Library()


@register.inclusion_tag('dyn_struct/render_struct.html')
def render_struct(structure_obj, prefix, value=None, template='bootstrap3'):
    if value and isinstance(value, six.string_types):
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
        'template': template
    }


@register.inclusion_tag('dyn_struct/render_struct_field_bootstrap2.html')
def render_struct_field_bootstrap2(struct_field, prefix, value=None):
    return _render_struct_field(struct_field, prefix, value)


@register.inclusion_tag('dyn_struct/render_struct_field_bootstrap3.html')
def render_struct_field_bootstrap3(struct_field, prefix, value=None):
    return _render_struct_field(struct_field, prefix, value)


def _render_struct_field(struct_field, prefix, value=None):
    field_name = prefix + '_' + struct_field.name

    form_field = struct_field.build()
    rendered_input = form_field.widget.render(
        name=field_name,
        value=value or form_field.initial,
        attrs={'class': 'form-control'}
    )

    return {
        'classes': struct_field.classes,
        'item': form_field,
        'rendered_input': rendered_input,
        'name': field_name,
    }


