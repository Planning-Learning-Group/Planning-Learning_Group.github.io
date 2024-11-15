from collections import defaultdict

from pelican import signals

import utils


def parse_people(generator):
    data = utils.load_people_data(generator.path)

    category_map = {cat["id"]: cat["name"] for cat in data["categories"]}
    # Let's index the people by their category, the way they will appear on the website.
    indexed_people = defaultdict(list)
    people_by_key = {}
    for p in data["people"]:
        indexed_people[category_map[p["category"]]].append(p)
        people_by_key[p["key"]] = p

    # Extract a sorted list of categories that have at least one member:
    ordered_categories = [
        cat["name"] for cat in data["categories"] if cat["name"] in indexed_people
    ]

    generator.context["people"] = indexed_people
    generator.context["people_categories"] = ordered_categories
    generator.context["people_by_key"] = people_by_key


def register():
    signals.page_generator_init.connect(parse_people)
