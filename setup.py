# -*- coding: utf-8 -*-
"""Installer for the collective.droproles package."""

from setuptools import find_packages
from setuptools import setup


with open("README.rst") as myfile:
    readme = myfile.read()
with open("CONTRIBUTORS.rst") as myfile:
    contributors = myfile.read()
with open("CHANGES.rst") as myfile:
    changes = myfile.read()

long_description = "\n\n".join([readme, contributors, changes])


setup(
    name="collective.droproles",
    version="1.0.0",
    description="Plone PAS patch for dropping roles for editors and managers",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="Maurits van Rees",
    author_email="m.van.rees@zestsoftware.nl",
    url="https://github.com/collective/collective.droproles/",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools"],
    extras_require={"test": ["plone.app.testing"]},
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
