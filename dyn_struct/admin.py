from django.contrib import admin

from .db import models

admin.site.register(models.DynamicObject)
admin.site.register(models.DynamicObjectField)
