import os
from pathlib import Path
import sys
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(Path(__file__).absolute().parent)

if 'publish' in sys.argv:
    if 'test' in sys.argv:
        os.system('python setup.py sdist bdist_wheel upload -rtest')
    else:
        os.system('python setup.py sdist bdist_wheel')
        # twine upload --repository pypi dist/*  # For markdown to render, use twine
    sys.exit()


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='classy-django-datatables',
    version='1.0.7',
    description='Create datatables quickly for django models.',
    url='https://github.com/scuml/django-datatables',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",

    license="Apache",
    author='Stephen Mitchell',
    author_email='stephen@echodot.com',

    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={'': ['LICENSE']},

    python_requires='>=3.6',
    install_requires=[
        'django>=2',
        'pyquerystring',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
