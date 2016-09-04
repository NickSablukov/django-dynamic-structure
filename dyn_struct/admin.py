from django.contrib import admin

from .db import models

admin.site.register(models.DynamicStructure)


class DynamicStructureField(admin.ModelAdmin):
    list_display = ('name', 'form_field', 'widget')
admin.site.register(models.DynamicStructureField)
