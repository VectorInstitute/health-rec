"""Configuration file for the Sphinx documentation builder."""
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from typing import List


sys.path.insert(0, os.path.abspath("../../aieng_template"))


# -- Project information -----------------------------------------------------

project = "aieng-template"
copyright = "2024, Vector AI Engineering"  # noqa: A001
author = "Vector AI Engineering"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# Only keep necessary extensions
extensions = [
    "myst_parser",  # for markdown support
    "sphinx_design",  # for UI components
    "sphinx_copybutton",  # for copy button on code blocks
    "sphinxcontrib.httpdomain",  # for REST API documentation
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = []

# -- Options for Markdown files ----------------------------------------------
#

# Markdown settings
myst_enable_extensions = [
    "colon_fence",  # for code fences
    "deflist",  # for definition lists
    "fieldlist",  # for field lists
    "tasklist",  # for task lists
    "attrs_inline",  # for inline attributes
]
myst_heading_anchors = 2


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_title = "Health Recommendation System"
html_theme_options = {
    "dark_css_variables": {
        "color-brand-primary": "#faad1a",
        "color-brand-content": "#eb088a",
        "color-foreground-secondary": "#52c7de",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/VectorInstitute/aieng-template",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
templates_path = ["_templates"]
html_static_path = ["_static"]
html_js_files = [
    "require.min.js",
    "custom.js",
]
html_additional_pages = {"page": "page.html"}