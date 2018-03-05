from django.contrib import admin

from .db import models
from . import forms

admin.site.register(models.DynamicStructure)


class DynamicStructureField(admin.ModelAdmin):
    list_display = ('structure', 'name', 'header', 'form_field', 'widget', 'row', 'position')
    list_display_links = ('name', 'header')
    list_filter = ('structure', )
    search_fields = ('structure__name', 'name', 'header')

    def get_queryset(self, request):
        qs = super(DynamicStructureField, self).get_queryset(request)
        qs = qs.filter(structure__is_deprecated=False)
        return qs

    def save_model(self, request, obj, form, change):
        if obj.structure.fields.exists():
            obj.structure.clone(exclude_field=obj)
            obj.structure_id = obj.structure.id
            obj.id = None
            form.fields['structure'].queryset = models.DynamicStructure.objects.all()
        return super(DynamicStructureField, self).save_model(request, obj, form, change)

admin.site.register(models.DynamicStructureField, DynamicStructureField)
