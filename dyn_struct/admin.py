from django.contrib import admin

from .db import models

admin.site.register(models.DynamicStructure)


class DynamicStructureField(admin.ModelAdmin):
    list_display = ('name', 'header', 'form_field', 'widget', 'row', 'position')
    list_display_links = ('name', 'header')
admin.site.register(models.DynamicStructureField, DynamicStructureField)
