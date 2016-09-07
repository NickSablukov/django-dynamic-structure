import six
import json
import django.template

register = django.template.Library()


@register.inclusion_tag('dyn_struct/render_struct.html')
def render_struct(structure_obj, prefix, value=None, template='bootstrap3'):
    if value and isinstance(value, six.string_types):
        value = json.loads(value)

    form = structure_obj.build_form(data=value, prefix=prefix)
    rows = structure_obj.get_rows(form)

    return {
        'rows': rows,
        'template': template
    }
