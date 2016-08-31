# django_dm

## USE: 
- model attr "data = models.TextField()"
- modelForm use DynamicModelForm "class MyForm(django_dm.forms.DynamicModelForm)"
- required 'data' in Meta fields "class Meta:\ fields = ('data', )"
- dynamic_object in kwargs form "form = MyForm(dynamic_object=get_dynamic_object()"
- done!
