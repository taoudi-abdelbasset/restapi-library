import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'restapi-library'
copyright = '2023, Taoudi Abdelbasset'
author = 'Taoudi Abdelbasset'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',  # For Markdown support
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

myst_enable_extensions = [
    "colon_fence",  # Support ::: for code blocks
    "deflist",      # Support definition lists
    "html_admonition",  # Support admonitions
]

autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__init__',
}