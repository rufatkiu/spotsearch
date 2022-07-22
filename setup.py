# -*- coding: utf-8 -*-
<<<<<<< HEAD
"""Installer for Spot package."""
=======
"""Installer for Searx package."""
# Test auto sync
>>>>>>> 06e179d0f1696b3dc6a66d1d01c178fcfafed5e5

from setuptools import setup
from setuptools import find_packages
from searx.version import VERSION_STRING
from searx import brand

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = [ l.strip() for l in f.readlines()]

with open('requirements-dev.txt') as f:
    dev_requirements = [ l.strip() for l in f.readlines()]

setup(
    name='spot',
    description="A privacy-respecting, hackable metasearch engine",
    long_description=long_description,
    url=brand.DOCS_URL,
    use_scm_version={"tag_regex": r"^(?:[\w-]+-)?(?P<version>[vV]?\d+(?:\.\d+){0,2}.*)$"},
    setup_requires=['setuptools_scm'],
    project_urls={
        "Code": brand.GIT_URL,
        "Issue tracker": brand.ISSUE_URL
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        'License :: OSI Approved :: GNU Affero General Public License v3'
    ],
    keywords='metasearch searchengine search web http',
    author='E FOUNDATION',
    author_email='dev@e.email',
    license='GNU Affero General Public License',
    packages=find_packages(exclude=["tests*", "searx_extra"]),
    zip_safe=False,
    install_requires=requirements,
    extras_require={
        'test': dev_requirements
    },
    entry_points={
        'console_scripts': [
            'searx-run = searx.webapp:run',
            'searx-checker = searx.search.checker.__main__:main'
        ]
    },
    package_data={
        'searx': [
            'settings.yml',
            '../README.md',
            '../requirements.txt',
            '../requirements-dev.txt',
            'data/*',
            'plugins/*/*',
            'static/*.*',
            'static/*/*.*',
            'static/*/*/*.*',
            'static/*/*/*/*.*',
            'static/*/*/*/*/*.*',
            'templates/*/*.*',
            'templates/*/*/*.*',
            'translations/*/*/*'
        ],
    },
)
