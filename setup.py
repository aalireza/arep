from setuptools import setup
from os import path
import codecs


with codecs.open(
    path.join(path.abspath(path.dirname(__file__)), 'README.rst'), 'r'
) as f:
    long_description = f.read()


setup(
    name="arep",
    version="0.1.0",
    description="semantic/syntactic source code searching for Python.",
    long_description=long_description,
    license="BSD License (3-Calause)",
    author="Alireza Rafiei",
    author_email="mail@rafiei.net",
    packages=["arep"],
    url="https://github.com/aalireza/arep",
    download_url="https://github.com/aalireza/arep/tarball/0.1.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License (3-Clause)"
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=["grep", "arep", "syntax", "semantics", "search", "source",
              "code analysis", "AST", "abstract syntax tree"],
    entry_points={
          'console_scripts': [
              'arep = arep.__main__:Main',
          ],
      },
)
