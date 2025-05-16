#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must install Twine:
#   $ pip install -r requirements.txt

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "app"
DESCRIPTION = "My short description for my project."
URL = "https://github.com/me/myproject"
EMAIL = "me@example.com"
AUTHOR = "Awesome Soul"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = None
LICENSE = "MIT"
# What packages are required for this module to be executed?
REQUIRED = [
    "requests",
    "rich",
    "questionary",
    "pyfiglet",
]

here = os.path.abspath(os.path.dirname(__file__))

# Use README.md if README.rst is absent
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with io.open(readme_path, encoding="utf-8") as f:
        long_description = "\n" + f.read()
else:
    long_description = ""

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    entry_points={"console_scripts": ["fib-manager=app.cli:main"]},
    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    cmdclass={"upload": UploadCommand},
)
