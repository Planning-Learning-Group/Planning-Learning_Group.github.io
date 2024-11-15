from dataclasses import dataclass
import os.path

from pelican import signals

from utils import load_yml


@dataclass
class Category:
    name: str
    ordering: int


def parse_software(generator):
    data = load_yml(os.path.join(generator.path, "software.yml"))
    software_categories = {
        cat["id"]: Category(cat["name"], index)
        for index, cat in enumerate(data["categories"])
    }
    generator.context["software"] = data["software"]
    generator.context["software_categories"] = software_categories


def register():
    signals.page_generator_init.connect(parse_software)
