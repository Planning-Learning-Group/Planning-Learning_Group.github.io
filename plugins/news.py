from pathlib import Path

from pelican import signals

import utils


def add_links(generator, people_dict, item):
    content = item["content"]
    for key, person in people_dict.items():
        content = content.replace(key, utils.get_person_link(generator, key, person["name"]))
    item["content"] = content
    return item


def convert_all_fields_to_html(entry):
    for key in ["content"]:
        entry[key] = utils.convert_to_html(entry[key])


def parse_news(generator):
    news = utils.load_yml(Path(generator.path) / "news.yml")["news"]
    people_dict = {
        p["key"]: p
        for p in utils.load_yml(Path(generator.path) / "people.yml")["people"]
    }
    news = [add_links(generator, people_dict, item) for item in news]
    for item in news:
        convert_all_fields_to_html(item)
    generator.context["mrlab_news"] = news


def register():
    # Needs to run after the member pages have been generated.
    signals.static_generator_finalized.connect(parse_news)
