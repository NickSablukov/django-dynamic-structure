# coding: utf-8
import json

from django.db import models
from django import forms
from dyn_struct import datatools
from dyn_struct.db import fields
from dyn_struct.exceptions import CheckClassArgumentsException


class DynamicStructure(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'динамическая структура'
        verbose_name_plural = 'динамические структуры'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_field_names(self):
        return list(self.fields.values_list('name', flat=True))

    def get_rows(self):
        table = []
        for row_number in self.fields.values_list('row', flat=True).order_by('row').distinct():
            row = self.fields.filter(row=row_number).order_by('position')
            table.append(row)
        return table


class DynamicStructureField(models.Model):
    FORM_FIELD_CHOICES = [(field, field) for field in datatools.get_django_fields()]
    WIDGETS_CHOICES = [(widget, widget) for widget in datatools.get_django_widgets()]

    header = models.CharField(max_length=255, verbose_name='заголовок', blank=True,
                              help_text='при заполнении этого поля, вместо поля формы будет выводить заголовок')

    structure = models.ForeignKey(DynamicStructure, verbose_name='Структура', related_name='fields')
    name = models.CharField(max_length=255, verbose_name='Название', blank=True, unique=True)

    form_field = models.CharField(max_length=255, choices=FORM_FIELD_CHOICES, verbose_name='Поле', blank=True)
    form_kwargs = fields.ParamsField(verbose_name='Параметры поля', default='{}')

    widget = models.CharField(max_length=255, choices=WIDGETS_CHOICES, verbose_name='Виджет', blank=True)
    widget_kwargs = fields.ParamsField(verbose_name='Параметры виджета', default='{}')

    row = models.PositiveSmallIntegerField(verbose_name='Строка')
    position = models.PositiveSmallIntegerField(verbose_name='Позиция в строке')
    classes = models.CharField(max_length=255, verbose_name='CSS-классы', help_text='col-md-3, custom-class ...',
                               blank=True)

    class Meta:
        verbose_name = 'поле динамической структуры'
        verbose_name_plural = 'поля динамических структур'

    def __str__(self):
        if self.header:
            return self.header
        else:
            return self.name

    def __unicode__(self):
        if self.header:
            return self.header
        else:
            return self.name

    def clean(self):
        if self.header:
            if self.name or self.form_field or self.widget:
                raise forms.ValidationError('Если указывается заголовок, то поля '
                                            '"Название", "Поле" и "Виджет" '
                                            'указывать не нужно')

        else:
            if not self.name:
                raise forms.ValidationError('Необходимо указать название', code='invalid')
            if not self.form_field:
                raise forms.ValidationError('Необходимо указать поле', code='invalid')

            try:
                if self.form_kwargs:
                    self._check_field_arguments()

                if self.widget and self.widget_kwargs:
                    self._check_widget_arguments()

                self.build()

            except CheckClassArgumentsException as ex:
                forms.ValidationError(str(ex), code='invalid')
            except Exception as ex:
                raise forms.ValidationError('Не удалось создать поле формы ({})'.format(str(ex)), code='invalid')

        self.widget_kwargs = json.dumps(json.loads(self.widget_kwargs), indent=4)
        self.form_kwargs = json.dumps(json.loads(self.form_kwargs), indent=4)

    def build(self):
        assert self.form_field

        field_kwargs = json.loads(self.form_kwargs) if self.form_kwargs else {}
        if 'label' not in field_kwargs:
            field_kwargs['label'] = self.name

        if self.widget:
            widget_class = getattr(forms.widgets, self.widget)
            widget_kwargs = json.loads(self.widget_kwargs) if self.widget_kwargs else {}
            field_kwargs.update({'widget': widget_class(**widget_kwargs)})

        field_class = getattr(forms.fields, self.form_field)

        field = field_class(**field_kwargs)
        field.name = self.name
        return field

    def _check_field_arguments(self):
        field_class = getattr(forms.fields, self.form_field)
        kwargs = json.loads(self.form_kwargs)
        datatools.check_class_arguments(field_class, kwargs)

    def _check_widget_arguments(self):
        widget_class = getattr(forms.widgets, self.widget)
        kwargs = json.loads(self.widget_kwargs)
        datatools.check_class_arguments(widget_class, kwargs)
