from django.db import models

from dyn_struct.db import validators


class ParamsField(models.TextField):

    @property
    def validators(self):
        field_validators = super(ParamsField, self).validators
        field_validators.extend([
            validators.ParamsValidator()
        ])
        return field_validators
