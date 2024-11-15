import datetime
import logging
from pathlib import Path
import re

from markdown import Markdown

from pelican.contents import Content

import yaml


PAPER_LINKS_REGEX = re.compile(r"\{paper\}([a-z\-]+[0-9]{4}[a-z\-]*)")


def load_yml(filename):
    try:
        with open(filename, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        logging.error(f'Could not open file "{filename}": {e}')


def preprocess_person(person):
    join_date = person["join_date"]
    person["join_date"] = join_date.strftime("%Y-%m-%d")
    if "leave_date" in person:
        leave_date = person["leave_date"]
        person["leave_date"] = leave_date.strftime("%Y-%m-%d")
        if leave_date < datetime.date.today():
            person["category"] = "former"


def load_people_data(generator_path):
    data = load_yml(Path(generator_path) / "people.yml")
    for person in data["people"]:
        preprocess_person(person)
    return data


def _add_paper_links(text):
    def get_link(match):
        return f"/papers/{match.group(1)}.pdf"

    return PAPER_LINKS_REGEX.sub(get_link, text)


def convert_to_html(text):
    text = _add_paper_links(text)
    html = Markdown().convert(text)
    # Strip block environment.
    p = '<p>'
    np = '</p>'
    if html.startswith(p) and html.endswith(np):
        html = html[len(p):-len(np)]
    return html


def get_person_link(generator, key, name):
    text = f"[{name}]({{filename}}team-members/{key}.md)"
    html = convert_to_html(text)
    link = Content(
        html,
        metadata={"template": "page"},
        source_path=Path(generator.path) / "pages" / "home.md",
        context=generator.context,
        settings=generator.settings,
    ).get_content("")
    return link
