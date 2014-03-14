import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "-DMMG-",
    version = "0",
    author = "Luca Da Rin Fioretto, Federico Campeotto",
    author_email = "Luca Da Rin Fioretto <lucadrf@nmsu.edu>,\
                    Federico Campeotto <campe8@nmsu.edu>",
    description = (""),
    license = "Apache License v2",
    keywords = "",
    url = "",
    packages = ['dmmg', 'dmmg/tests'],
    long_description = read('README.rst'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: NLP",
        "License :: Apache License v2",
    ],
)
