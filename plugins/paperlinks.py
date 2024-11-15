"""
Replace @jones-et-al-2022 tags by links to the respective papers.
"""

from pelican import signals

import utils


def add_paper_links(text):
    def get_link(match):
        return f"{{static}}/papers/{match.group(1)}.pdf"

    return utils.PAPER_LINKS_REGEX.sub(get_link, text)


def sequence_gen(genlist):
    for gen in genlist:
        yield from gen


def _add_paper_links(article_or_page_generator):
    all_content = [
        getattr(article_or_page_generator, attr, None)
        for attr in ["articles", "drafts", "pages"]
    ]
    all_content = [x for x in all_content if x is not None]
    for article in sequence_gen(all_content):
        article._content = add_paper_links(article._content)


def register():
    signals.article_generator_finalized.connect(_add_paper_links)
    signals.page_generator_finalized.connect(_add_paper_links)
