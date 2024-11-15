"""
Replace [jane-smith] tags by links to the person's homepage.
"""

import itertools
from pathlib import Path

from pelican import signals

import utils


def _add_people_links(article_or_page_generator):
    all_content = [
        getattr(article_or_page_generator, attr, None)
        for attr in ["articles", "drafts", "pages"]
    ]
    all_content = [x for x in all_content if x is not None]

    people_dict = {
        p["key"]: p
        for p in utils.load_yml(Path(article_or_page_generator.path) / "people.yml")["people"]
    }
    for article in itertools.chain.from_iterable(all_content):
        for key, person in people_dict.items():
            article._content = article._content.replace(f"[{key}]", utils.get_person_link(article_or_page_generator, key, person["name"]))


def register():
    signals.article_generator_finalized.connect(_add_people_links)
    signals.page_generator_finalized.connect(_add_people_links)
