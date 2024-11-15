#!/usr/bin/env python

import os
import sys
import pathlib
here = pathlib.Path(__file__).parent.absolute()

# Import custom plugins.
sys.path.append(str(here / 'plugins'))
import awards
import bibliography
import news
import paperlinks
import peoplelinks
import pelican_redirect
import people
import software

AUTHOR = 'Planning & Learning Group'
SITENAME = 'Planning & Learning Group'
SITESUBTITLE = 'Planning & Learning Research Group at Universidad Carlos III of Madrid'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

# Disable those Pelican components we don't want, such as a blog index, or
# RSS feeds, category pages, etc.
INDEX_URL = None
INDEX_SAVE_AS = None
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
AUTHORS_SAVE_AS = None
CATEGORIES_SAVE_AS = None
TAGS_SAVE_AS = None
TAG_SAVE_AS = None
AUTHOR_URL = None
AUTHOR_SAVE_AS = None
ARCHIVES_URL = None
ARCHIVES_SAVE_AS = None
CATEGORY_URL = None
CATEGORY_SAVE_AS = None
TAG_URL = None
# We might want to use articles for some blog in the future
# ARTICLE_URL = '{slug}/'  # category is part of the slug (i.e., examples)
# ARTICLE_SAVE_AS = '{slug}/index.html'

DEFAULT_PAGINATION = False

STATIC_PATHS = [
    'images',
    'extra',
    'papers',
]

# https://stackoverflow.com/a/42968572/1277298
ARTICLE_EXCLUDES = STATIC_PATHS


EXTRA_PATH_METADATA = {
    f"extra/{name}": {'path': name}
    for name in os.listdir(f"{PATH}/extra")
}

IGNORE_FILES = [".#*", "README.md"]

# Parse subdir name from file path to preserve file hierarchy:
#   pages/awards.md --> subdir=""
#   pages/projects/rleap.md --> subdir="projects/"
PATH_METADATA = r'pages/(?P<subdir>(projects|teaching)/|)?.*\..*'
PAGE_URL = '/{subdir}{slug}/'
PAGE_SAVE_AS = '{subdir}{slug}/index.html'

THEME = 'themes/rleap'

# The following contains pairs <title, page>, where `title` is the text that
# will appear on the menu, and `page` is the page name, as defined by some file
# page.xxx in content/pages.
RLEAP_MENU = (
    #('Home', '/'),
    ('People', 'people'),
    ('Projects', 'projects'),
    # ('Awards', 'awards'),
    # ('Publications', 'publications'),
    ('Software', 'software'),
    # ('Teaching', 'teaching'),
    # ('Positions', 'positions')
)


PLUGINS = [awards, bibliography, news, paperlinks, peoplelinks, pelican_redirect, people, software]

EMAIL = "ffernand@inf.uc3m.es"

DELETE_OUTPUT_DIRECTORY = True


# A directory that contains the bibliography-related templates
# type: Union[str, os.PathLike]
BIBLIOGRAPHY_TEMPLATES = f"{PATH}/../templates"

# format string to link to citation
# type: str
BIBLIOGRAPHY_CITATION_URL = "/papers/{key}.html"

# format string to save citations as in generated site
# type: str
BIBLIOGRAPHY_CITATION_SAVE_AS = "papers/{key}.html"
