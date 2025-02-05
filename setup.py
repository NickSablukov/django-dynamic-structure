# coding: utf-8
# python -m pip install certifi
# export SSL_CERT_FILE=$(python -m certifi)
# python setup.py sdist
# twine upload dist/*
from setuptools import setup, find_packages

setup(
    name='django-dynamic-structure',
    version='0.0.35',
    description='Dynamical django model structure. For example, for user customized medical specialist protocols.',
    author='Telminov Sergey',
    author_email='sergey@telminov.ru',
    url='https://github.com/NickSablukov/django-dynamic-structure',
    include_package_data=True,
    packages=find_packages(),
    package_data={'dyn_struct': ['templates/dyn_struct/*.html']},
    license='The MIT License',
    install_requires=[
        'django', 'six', 'sw-python-utils', 'sw-django-utils'
    ],
)
