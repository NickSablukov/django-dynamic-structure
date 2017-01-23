# coding: utf-8
# python setup.py sdist register bdist_egg upload
from setuptools import setup, find_packages

setup(
    name='django-dynamic-structure',
    version='0.0.14',
    description='Dynamical django model structure. For example, for user customized medical specialist protocols.',
    author='Nick Sablukov',
    author_email='dessanndes@gmailcom',
    url='https://github.com/NickSablukov/django-dynamic-structure',
    include_package_data=True,
    packages=find_packages(),
    license='The MIT License',
    install_requires=[
        'django', 'six', 'sw-python-utils',
    ],
)
