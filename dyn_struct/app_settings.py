from django.conf import settings

# использует для преобразования имен полей библиотеку slugify
EXCLUDE_NAME_SYMBOLS = getattr(settings, "EXCLUDE_NAME_SYMBOLS", ["'"])
