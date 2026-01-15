"""
Setup script for NLScraper
"""
from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='nlscraper',
    version='1.0.0',
    author='NLScraper Contributors',
    author_email='',
    description='High-performance web scraper for Noel Leeming product data extraction',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/deepakchhabra-svg/NLScraper',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'nlscraper=main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
