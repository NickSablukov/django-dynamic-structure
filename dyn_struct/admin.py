from django.contrib import admin

from .db import models

admin.site.register(models.DynamicStructure)
admin.site.register(models.DynamicStructureField)
