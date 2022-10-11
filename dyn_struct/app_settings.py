from django.conf import settings

# использует для преобразования имен полей библиотеку slugify
EXCLUDE_NAME_SYMBOLS = getattr(settings, "DYN_STRUCT_EXCLUDE_NAME_SYMBOLS", ["'"])
