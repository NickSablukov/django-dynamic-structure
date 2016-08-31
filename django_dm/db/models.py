import json
from typing import NamedTuple

from django.core import exceptions
from django.db import models
from django import forms

from django_dm import datatools
from django_dm.db import fields

from django_dm.exceptions import DynamicModelException


class DynamicObject(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'динамический объект'
        verbose_name_plural = 'динамические объекты'

    def __str__(self):
        return self.name

    def build_fields(self):
        fields_data = {}
        for field in self.fields.all():
            try:
                fields_data[field.name] = field.build()
            except Exception:
                exceptions.DynamicModelException('Возникла ошибка в построении поля протокола под именем {}'.format(field.name))

        return fields_data

    def get_rows(self, form):
        rows = []

        rows_list = sorted(list(set(self.fields.all().values_list('row', flat=True))))
        fields_map = {field.name: field for field in form}

        for row_number in rows_list:
            row_fields = self.fields.filter(row=row_number).order_by('position')
            rows.append(
                [(fields_map[field.name] if not field.header else field, field.classes) for field in row_fields]
            )


class DynamicObjectField(models.Model):
    FORM_FIELD_CHOICES = [(field, field) for field in datatools.get_django_fields()]
    WIDGETS_CHOICES = [(field, field) for field in datatools.get_django_widgets()]

    KWARGS_HELP_TEXT = '{"key": value, ... }  / Используйте только двойные скобки ( " )'

    header = models.CharField(max_length=255, verbose_name='заголовок', null=True, blank=True,
                              help_text='при заполнении этого поля, объект будет являться заголовком')

    dynamic_object = models.ForeignKey(DynamicObject, verbose_name='Динамический объект', related_name='fields')
    name = models.CharField(max_length=255, verbose_name='Название', null=True, blank=True)

    form_field = models.CharField(max_length=255, choices=FORM_FIELD_CHOICES, verbose_name='Поле', null=True, blank=True) # success вынести в кclean чтоб было красиво для каждого РАЗНОГО  поля
    form_kwargs = fields.ParamsField(verbose_name='Параметры поля', help_text=KWARGS_HELP_TEXT, blank=True, null=True)

    widget = models.CharField(max_length=255, choices=WIDGETS_CHOICES, verbose_name='Виджет', null=True, blank=True)
    widget_kwargs = fields.ParamsField(verbose_name='Параметры виджета', help_text=KWARGS_HELP_TEXT, blank=True, null=True)

    row = models.PositiveIntegerField(verbose_name='Строка')
    position = models.PositiveIntegerField(verbose_name='Позиция в строке')
    classes = models.CharField(max_length=255, verbose_name='Классы', help_text='col-md-3, custom-class ...', null=True, blank=True)

    class Meta:
        verbose_name = 'поле динамического объекта'
        verbose_name_plural = 'поля динамических объектов'

    def __str__(self):
        return '{0} ({1}/{2})'.format(self.name, self.form_field, self.widget) if not self.header else 'Заголовок "{}"'.format(self.header)

    def check_item_arguments(self, arguments, json_data, item_name):
        if json_data:
            kwargs = json.loads(json_data)
            if arguments and kwargs.keys():
                error_keys = list(frozenset(kwargs.keys()) - frozenset(arguments))
                if error_keys:
                    raise ValidationError(
                        '{0} - неизвестные ключи для {2}. Выбирайте необходимые из {1}'.format(
                            ', '.join(error_keys),
                            ', '.join(arguments),
                            item_name
                        ), code='invalid'
                    )

    def check_field_arguments(self):
        arguments = datatools.get_item_arguments(getattr(forms.fields, self.form_field))
        self.check_item_arguments(arguments, self.form_kwargs, self.form_field)

    def check_widget_arguments(self):
        arguments = datatools.get_item_arguments(getattr(forms.widgets, self.widget))
        self.check_item_arguments(arguments, self.widget_kwargs, self.widget)

    def clean(self):

        if self.header:
            self.name = self.form_field = self.form_kwargs = self.widget = self.widget_kwargs = None
        elif self.name and self.form_field and self.widget:
            try:
                self.check_field_arguments()
                self.check_widget_arguments()
                self.build()
            except Exception as e:
                raise ValidationError('Не удалось создать поле формы ({})'.format(str(e)), code='invalid')
        else:
            raise ValidationError(
                'Необходимо указать заголовок, если это заголовок, либо название, поле и виджет', code='invalid'
            )

        self.widget_kwargs = json.dumps(json.loads(self.widget_kwargs), indent=4) if self.widget_kwargs else ''
        self.form_kwargs = json.dumps(json.loads(self.form_kwargs), indent=4) if self.form_kwargs else ''

    def build(self):
        if not self.header:
            widget = getattr(forms.widgets, self.widget)
            widget_kwargs = json.loads(self.widget_kwargs) if self.widget_kwargs else {}

            field_kwargs = json.loads(self.form_kwargs) if self.form_kwargs else {}
            field_kwargs.update({'widget': widget(**widget_kwargs)})
            field = getattr(forms.fields, self.form_field)

            field_object = field(**field_kwargs)
            field_object.classes = self.classes
            field_object.position = self.position
            field_object.row = self.row

            return field_object
        else:
            return self
