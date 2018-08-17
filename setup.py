import os
from pathlib import Path
import sys
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(Path(__file__).absolute().parent)

if 'publish' in sys.argv:
    if 'testpublish' in sys.argv:
        os.system('python setup.py sdist bdist_wheel upload -rtest')
    else:
        os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()

setup(
    setup_cfg=True
)
