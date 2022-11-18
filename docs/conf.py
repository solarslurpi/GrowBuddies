# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
# Add the code path
sys.path.insert(0, os.path.abspath('../code'))

project = 'growBuddy'
copyright = '2022, HappyDay'
author = 'HappyDay'
release = '0.1'

# ignore files in the virtual environment
# https://youtu.be/gWrc4xzm45Y?list=PL2Uw4_HvXqvYk1Y5P8kryoyd83L_0Uk5K&t=1106
exclude_patterns = ["py_env/*"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinxcontrib.napoleon',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'myst_parser',
    'sphinx.ext.autosectionlabel',
    'sphinx_design'
]
# Make sure the target is unique
autosectionlabel_prefix_document = True


# Include methods that start with an _
napoleon_include_private_with_doc = True

# Add Myst extensions
myst_enable_extensions = ["colon_fence"]

# Ignore documentating these files.
autodoc_mock_imports = ['influxdb', 'paho']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
