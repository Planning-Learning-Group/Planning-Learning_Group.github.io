from collections import defaultdict
from pathlib import Path

from pelican import signals

import utils


def get_awardees_string(generator, awardees, people_dict):
    awardee_strings = [
        utils.get_person_link(generator, awardee, people_dict[awardee]["name"]) if awardee in people_dict else awardee
        for awardee in awardees
    ]
    if len(awardees) == 1:
        return awardee_strings[0]
    else:
        return f"{', '.join(awardee_strings[:-1])}{',' if len(awardees) > 2 else ''} and {awardee_strings[-1]}"


def convert_all_fields_to_html(entry):
    for key in ["awarded_at", "description", "name"]:
        entry[key] = utils.convert_to_html(entry[key])


def parse_awards(generator):
    awards = utils.load_yml(Path(generator.path) / "awards.yml")["awards"]
    people_dict = {
        p["key"]: p
        for p in utils.load_yml(Path(generator.path) / "people.yml")["people"]
    }
    awards_by_person = defaultdict(list)
    awards.sort(key=lambda x: x["date"], reverse=True)
    for award in reversed(awards):
        convert_all_fields_to_html(award)
        only_personal_page = True
        for awardee in award["awardees"]:
            if awardee not in people_dict:
                # this could e.g. be a co-author who is not at LiU
                continue
            if people_dict[awardee]["join_date"] <= award["date"]:
                only_personal_page = False
            person_award = dict(award)
            # no need to display own name on personal page
            if len(award["awardees"]) > 1:
                person_award["awardees"] = get_awardees_string(
                    generator, [a for a in award["awardees"] if a != awardee], people_dict
                )
            else:
                del person_award["awardees"]
            awards_by_person[people_dict[awardee]["name"]].append(person_award)
        if only_personal_page or (
            "only_personal_page" in award and award["only_personal_page"]
        ):
            awards.remove(award)
        else:
            award["awardees"] = get_awardees_string(generator, award["awardees"], people_dict)
    for awards_person in awards_by_person.values():
        awards_person.reverse()
    generator.context["awards"] = awards
    generator.context["awards_by_person"] = awards_by_person


def register():
    # Needs to run after the member pages have been generated.
    signals.static_generator_finalized.connect(parse_awards)
