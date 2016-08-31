from django.db import models

from django_dm.db import validators


class ParamsField(models.TextField):

    @property
    def validators(self):
        field_validators = super().validators
        field_validators.extend([
            validators.ParamsValidator()
        ])
        return field_validators
