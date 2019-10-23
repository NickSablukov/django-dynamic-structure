# coding: utf-8
import json
import itertools

from django.db import models
from django import forms
from dyn_struct import datatools
from dyn_struct.db import fields
from dyn_struct.exceptions import CheckClassArgumentsException
from swutils.string import transliterate


class ExcludeDeprecatedManager(models.Manager):
    def get_queryset(self):
        return super(ExcludeDeprecatedManager, self).get_queryset().filter(is_deprecated=False)


class DynamicStructure(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    version = models.PositiveIntegerField(editable=False, default=1)
    is_deprecated = models.BooleanField(editable=False, default=False)
    created = models.DateTimeField(auto_now_add=True)

    objects = ExcludeDeprecatedManager()
    standard_objects = models.Manager()

    class Meta:
        verbose_name = 'динамическая структура'
        verbose_name_plural = 'динамические структуры'
        unique_together = ('name', 'version')
        ordering = ('name', '-version')

    @staticmethod
    def get_verbose(data_json):
        table = []

        if not data_json:
            return table

        data = json.loads(data_json)
        verbose_data = data['verbose_data']
        verbose_data.sort(key=lambda i: i['row'])

        for i, row in itertools.groupby(verbose_data, lambda i: i['row']):
            row = sorted(row, key=lambda i: i['position'])
            table.append(row)
        return table

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_field_names(self):
        return list(self.fields.values_list('name', flat=True))

    def get_rows(self, form):
        table = []
        for row_number in self.fields.values_list('row', flat=True).order_by('row').distinct():
            row = []
            for field in self.fields.filter(row=row_number).order_by('position'):
                if not field.is_header():
                    field_name = field.get_transliterate_name()
                    field.bound_field = form[field_name]
                row.append(field)
            table.append(row)
        return table

    def build_form(self, data=None, prefix='data'):
        form = forms.Form(data, prefix=prefix)
        for field in self.fields.exclude(name=''):
            field_name = field.get_transliterate_name()
            form.fields[field_name] = field.build()
        return form

    def clone(self, exclude_field=None):
        self.is_deprecated = True
        self.save()

        fields = list(self.fields.all())

        self.id = None
        self.version += 1
        self.is_deprecated = False
        self.save()

        for field in fields:
            if exclude_field and exclude_field.id and exclude_field.id == field.id:
                continue
            field.id = None
            field.structure = self
            field.save()

    def delete(self, using=None):
        self.is_deprecated = True
        self.save()


class DynamicStructureField(models.Model):
    FORM_FIELD_CHOICES = [(field, field) for field in datatools.get_django_fields()]
    WIDGETS_CHOICES = [(widget, widget) for widget in datatools.get_django_widgets()]

    structure = models.ForeignKey(DynamicStructure, verbose_name='Структура', related_name='fields',
                                  on_delete=models.PROTECT)
    header = models.CharField(max_length=100, verbose_name='заголовок', blank=True,
                              help_text='при заполнении этого поля, вместо поля формы будет выводить заголовок')
    name = models.CharField(max_length=100, verbose_name='Название', blank=True)

    form_field = models.CharField(max_length=255, choices=FORM_FIELD_CHOICES, verbose_name='Поле', blank=True)
    form_kwargs = fields.ParamsField(verbose_name='Параметры поля', default='{}')

    widget = models.CharField(max_length=255, choices=WIDGETS_CHOICES, verbose_name='Виджет', blank=True)
    widget_kwargs = fields.ParamsField(verbose_name='Параметры виджета', default='{}')

    row = models.PositiveSmallIntegerField(verbose_name='Строка')
    position = models.PositiveSmallIntegerField(verbose_name='Позиция в строке')
    classes = models.CharField(max_length=255, verbose_name='CSS-классы', help_text='col-md-3, custom-class ...',
                               blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'поле динамической структуры'
        verbose_name_plural = 'поля динамических структур'
        unique_together = ('structure', 'name', 'header')
        ordering = ('structure__name', 'row', 'position')

    def __str__(self):
        if self.is_header():
            return self.header
        else:
            return self.name

    def __unicode__(self):
        if self.is_header():
            return self.header
        else:
            return self.name

    def get_transliterate_name(self):
        return transliterate(self.name, space='_').replace("'", "")

    def is_header(self):
        return bool(self.header)

    def clean(self):
        if self.is_header():
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
                if self.form_kwargs and self.form_kwargs != '{}':
                    self._check_field_arguments()

                if self.widget and self.widget_kwargs and self.widget_kwargs != '{}':
                    self._check_widget_arguments()

                self.build()

            except CheckClassArgumentsException as ex:
                forms.ValidationError(str(ex), code='invalid')
            except Exception as ex:
                raise forms.ValidationError('Не удалось создать поле формы ({})'.format(str(ex)), code='invalid')

        self.widget_kwargs = json.dumps(json.loads(self.widget_kwargs), indent=4, ensure_ascii=False)
        self.form_kwargs = json.dumps(json.loads(self.form_kwargs), indent=4, ensure_ascii=False)

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


class DynamicStructureMixin(object):
    data_field = 'data'

    def get_structure_name(self):
        raise NotImplementedError()

    def get_structure(self):
        structure_name = self.get_structure_name()

        data = getattr(self, self.data_field)
        version = json.loads(data)['version']

        structure = DynamicStructure.standard_objects.get(
            version=version,
            name=structure_name
        )

        return structure

    def get_verbose_data(self):
        return self.get_structure().get_verbose(self.data)
