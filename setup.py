#!/usr/bin/env python3
"""
Presto: GitHub PR Comment Workflow Tool
A systematic approach to handling PR review comments.
"""

from setuptools import setup
import os

# Read the README file
def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            return f.read()
    return "Presto: GitHub PR Comment Workflow Tool"

setup(
    name="presto-pr",
    version="1.0.0",
    description="GitHub PR Comment Workflow Tool - Systematic approach to handling PR review comments",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Presto Contributors",
    author_email="presto@example.com",
    url="https://github.com/your-username/presto",
    project_urls={
        "Bug Reports": "https://github.com/your-username/presto/issues",
        "Source": "https://github.com/your-username/presto",
        "Documentation": "https://github.com/your-username/presto#readme",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    keywords="github pr review comments workflow cli git",
    python_requires=">=3.7",
    py_modules=["app"],
    install_requires=[
        # No external dependencies - uses only standard library + system gh CLI
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "presto=app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 