# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Chess Engine Comparator'
copyright = '2025, Chess App Team'
author = 'Chess App Team'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
source_suffix = ['.rst', '.md']