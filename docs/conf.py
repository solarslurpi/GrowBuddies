# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
# Add the code path
sys.path.insert(0, os.path.abspath('../growbuddiesproject'))

project = 'GrowBuddies'
copyright = '2022, HappyDay'
author = 'HappyDay'
release = '2022.12.0'

# ignore files
exclude_patterns = ["py_env/*", '**/_*']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [ "sphinx.ext.autodoc", "sphinx.ext.autosectionlabel", "sphinx_design", "myst_parser"]
# Make sure the target is unique
autosectionlabel_prefix_document = True


# Include methods that start with an _
napoleon_include_private_with_doc = True

# Add Myst extensions
myst_enable_extensions = ["colon_fence", "html_image"]

# Needed for font awesome support using the sphinx-design extension.
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"
]

# Ignore documentating these files.
autodoc_mock_imports = ['influxdb', 'paho']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
