import datetime
import logging
import os.path
from pathlib import Path
from typing import Dict, List  # noqa
from urllib.parse import urljoin
import sys

from pelican import signals
from pelican.contents import Content
from pelican.generators import Generator

import biblib.algo
import biblib.bib
from biblib import bib
import yaml

import utils


logger = logging.getLogger(__name__)


DEFAULT_SETTINGS = {
    # A directory that contains the bibliography-related templates
    # type: Union[str, os.PathLike]
    "BIBLIOGRAPHY_TEMPLATES": Path(__file__).resolve().parent / "data" / "templates",
    # A list of directories and files to look at for bibliographies, relative
    # to PATH.
    # type: List[str]
    "BIBLIOGRAPHY_PATH": "bibliography",
    # Order of bib files is important for the parser.
    "BIBLIOGRAPHY_FILES": ["abbrv.bib", "literatur.bib", "extra.bib", "crossref.bib", "extra_crossref.bib"],
    # list of file extensions (without leading period) that are metadata files
    # type: List[str]
    "BIBLIOGRAPHY_METADATA_EXTENSIONS": ["yml", "yaml"],
    # whether to write citations to files
    # type: bool
    "BIBLIOGRAPHY_WRITE_CITATIONS": True,
    # template to use for citations
    # type: str
    "BIBLIOGRAPHY_CITATION_TEMPLATE_NAME": "citation.html",
    # format string to link to citation
    # type: str
    "BIBLIOGRAPHY_CITATION_URL": "files/citation/{key}",
    # format string to save citations as in generated site
    # type: str
    "BIBLIOGRAPHY_CITATION_SAVE_AS": "files/citation/{key}/index.html",
}


def format_authors(entry):
    return [
        biblib.algo.tex_to_unicode(author.pretty(), pos=entry.field_pos["author"])
        for author in entry.authors()
    ]


def concat_authors(entry, authors):
    if len(authors) == 0:
        sys.exit(f"Error: bibtex entry {entry} has no author field.")
    elif len(authors) == 1:
        author = authors[0]
    else:
        author = ", ".join(authors[:-1])
        if entry.authors()[-1].is_others():
            author += " et al."
        else:
            author += " and " + authors[-1]
    return author


def tex_to_unicode(entry, field_name):
    return biblib.algo.tex_to_unicode(
        entry[field_name], pos=entry.field_pos[field_name]
    )


class Reference(Content):
    mandatory_properties = (
        "key",
        "bibtex_type",
    )
    default_template = "citation"  # this is the default, but ignored

    @classmethod
    def from_entry(
        cls,
        entry: biblib.bib.Entry,
        source_path: str,
        metadata: dict,
        settings: dict,
    ):
        content = entry.to_bib(wrap_width=90)

        # Pelican expects "date" variables to be datetime objects, not date objects.
        metadata["date"] = datetime.datetime.combine(
            metadata["date"], datetime.datetime.min.time()
        )
        metadata = {
            "key": entry.key,
            "bibtex_type": entry.typ,
            **metadata,
        }

        # Add default thesis type.
        if entry.typ == "mastersthesis":
            metadata.setdefault("type", "Master's thesis")

        # Convert bibtex fields from Tex to Unicode.
        for field_name in [
            "booktitle",
            "howpublished",
            "journal",
            "pages",
            "school",
            "title",
            "type",
            "volume",
            "year",
        ]:
            if field_name in entry:
                metadata[field_name] = tex_to_unicode(entry, field_name)


        metadata.setdefault("projects", [])
        metadata["url"] = urljoin(
            settings["SITEURL"],
            settings["BIBLIOGRAPHY_CITATION_URL"].format(**metadata),
        )
        metadata["save_as"] = settings["BIBLIOGRAPHY_CITATION_SAVE_AS"].format(
            **metadata
        )

        return cls(content, metadata=metadata, source_path=source_path)


def read_yaml(source_path):
    with open(source_path) as f:
        return yaml.safe_load(f)


class BibliographyGenerator(Generator):
    def _read_bibdata(self):
        bib_files = [
            str(Path(self.path) / self.settings["BIBLIOGRAPHY_PATH"] / bib_file)
            for bib_file in self.settings["BIBLIOGRAPHY_FILES"]
        ]
        parser = biblib.bib.Parser()
        for bib_file in bib_files:
            logger.debug(f"Reading references from {bib_file}")
            with open(bib_file) as f:
                parser.parse(f, log_fp=sys.stderr)
        db = parser.get_entries()
        db = bib.resolve_crossrefs(db, min_crossrefs=99)
        logger.debug(f"Found {len(db)} bibtex references.")
        return db

    def _read_extra_metadata(self) -> Dict[str, dict]:
        extra_metadata = {}
        for file in self.get_files(
            self.settings["BIBLIOGRAPHY_PATH"],
            extensions=self.settings["BIBLIOGRAPHY_METADATA_EXTENSIONS"],
        ):
            logger.debug(f"Reading extra metadata from {file}")
            try:
                source_path = os.path.join(self.path, file)
                new_metadata = read_yaml(source_path)
            except Exception as e:
                logger.error(
                    "Could not process %s\n%s",
                    file,
                    e,
                    exc_info=self.settings.get("DEBUG", False),
                )
                continue

            logger.debug(f"Read {len(new_metadata)} extra metadata entries from {file}")
            extra_metadata.update(new_metadata)

        return extra_metadata

    def _validate_extra_metadata(self, extra_metadata):
        dates = [metadata.get("date") for metadata in extra_metadata.values()]
        dates = [t for t in dates if t is not None]
        if not all(dates[i] >= dates[i + 1] for i in range(len(dates) - 1)):
            wrong_dates = [
                dates[i + 1] for i in range(len(dates) - 1) if dates[i] < dates[i + 1]
            ]
            sys.exit(f"Error: entries in not ordered inversely by date: {wrong_dates}.")

    def _get_file_links(self, key):
        papers_dir = Path(self.path) / "papers"
        assert papers_dir.is_dir()
        links = []
        for suffix, filetype, icon in [
            (".pdf", "paper", "file-pdf"),
            ("-slides.pdf", "slides", "file-slides"),
            ("-poster.pdf", "poster", "tv"),
        ]:
            path = papers_dir / f"{key}{suffix}"
            if path.is_file():
                logger.debug(f"Found publication file {path}")
                links.append(
                    {"href": f"/papers/{path.name}", "filetype": filetype, "icon": icon}
                )
        return links

    def _check_entry(self, key, ref, person_name_to_key):
        def search(typ):
            return any(link["filetype"] == typ for link in ref.metadata["links"])

        paper_found = search("paper")
        poster_found = search("poster")
        slides_found = search("slides")

        try:
            first_internal_author = next(author for author in ref.author_list if author in person_name_to_key)
        except StopIteration:
            # No paper author is a member of the group anymore, so we don't issue any warnings.
            return

        def paper_has_been_presented():
            return datetime.datetime.now().date() > ref.date.date()

        def is_recent_conference_paper():
            return int(ref.year) >= 2021 and ref.bibtex_type == "inproceedings" and not any(x in key for x in ["core", "demos", "ipc"])

        def presentation_was_long_enough_in_the_past():
            return datetime.datetime.now().date() > ref.date.date() + datetime.timedelta(days=14)

        if not paper_found and paper_has_been_presented():
            logging.warning(f"Paper missing for {key} (presented at {ref.date.date()}). Responsible: {first_internal_author}.")

        if not poster_found and not slides_found and is_recent_conference_paper() and presentation_was_long_enough_in_the_past():
            logging.warning(f"Neither slides nor poster found for {key} (presented at {ref.date.date()}). Responsible: {first_internal_author}.")

    def generate_context(self):
        db = self._read_bibdata()
        extra_metadata = self._read_extra_metadata()
        self._validate_extra_metadata(extra_metadata)
        people = utils.load_people_data(self.path)["people"]

        # Convert to Reference, subclass of Content.
        full_bibliography = []
        for key, metadata in extra_metadata.items():
            try:
                entry = db[key]
            except KeyError:
                sys.exit(f"Error: found no bibtex entry with key {key}.")

            # Format authors and add links for authors from the group.
            authors = format_authors(entry)
            metadata["author_list"] = authors
            person_name_to_key = {person["name"]: person["key"] for person in people if person["category"] != "former"}
            authors_with_links = [
                utils.get_person_link(self, person_name_to_key[author], author)
                if author in person_name_to_key else author
                for author in authors
            ]
            metadata["author"] = concat_authors(entry, authors_with_links)

            # Add links.
            links = metadata.get("links", [])
            # Convert Youtube IDs to links.
            youtube_id = metadata.get("youtube")
            if youtube_id:
                links.append(
                    {
                        "href": f"https://www.youtube.com/watch?v={youtube_id}",
                        "filetype": "recording",
                    }
                )
            # Convert Zenodo IDs to links.
            zenodo_id = metadata.get("zenodo")
            if zenodo_id:
                links.append(
                    {
                        "href": f"https://doi.org/10.5281/zenodo.{zenodo_id}",
                        "filetype": "code",
                    }
                )
            links.extend(self._get_file_links(key))
            links_order = [
                "paper",
                "technical report",
                "erratum",
                "slides",
                "recording",
                "poster",
                "code",
                "data",
            ]
            metadata["links"] = sorted(
                links, key=lambda link: links_order.index(link["filetype"])
            )

            source_path = entry.pos.fname
            ref = Reference.from_entry(entry, source_path, metadata, self.settings)
            self._check_entry(key, ref, person_name_to_key)
            full_bibliography.append(ref)

        def sort(ref):
            bib_year = int(ref.metadata["year"])
            date = ref.metadata["date"]
            if date.year != bib_year:
                sys.exit(f"Error: date and bibtex year differ for {ref.key}")
            return date

        full_bibliography.sort(key=sort, reverse=True)
        self.full_bibliography = full_bibliography
        self.group_bibliography = self._get_group_bibliography(
            full_bibliography, people
        )
        self.bibliography_by_person = {}
        people_names = [person["name"] for person in people]
        for person in people_names:
            self.bibliography_by_person[person] = [
                ref
                for ref in full_bibliography
                if person in ref.metadata["author_list"]
            ]
        self._update_context(("group_bibliography", "bibliography_by_person"))

    def _get_group_bibliography(self, full_bibliography, people):
        def is_group_reference(ref):
            ref_date = ref.metadata["date"].strftime("%Y-%m-%d")
            authors = ref.metadata["author_list"]
            for person in people:
                if person["name"] in authors:
                    join_date = person["join_date"]
                    if join_date <= ref_date:
                        return True
            return False

        return [ref for ref in full_bibliography if is_group_reference(ref)]

    def _update_context(self, items):
        """Update the context with the given items from the current
        processor.

        We override this method to avoid converting dictionaries to lists.
        """
        for item in items:
            value = getattr(self, item)
            # if hasattr(value, 'items'):
            #    value = list(value.items())  # py3k safeguard for iterators
            self.context[item] = value

    def generate_output(self, writer):
        if self.settings["BIBLIOGRAPHY_WRITE_CITATIONS"]:
            template = self.env.get_template(
                self.settings["BIBLIOGRAPHY_CITATION_TEMPLATE_NAME"]
            )
            for ref in self.full_bibliography:
                dest = ref.metadata["save_as"]
                writer.write_file(
                    dest, template, self.context, override_output=True, url="", ref=ref
                )


def update_settings(pelican):
    for key in DEFAULT_SETTINGS:
        pelican.settings.setdefault(key, DEFAULT_SETTINGS[key])
    if pelican.settings["BIBLIOGRAPHY_TEMPLATES"]:
        pelican.settings["THEME_TEMPLATES_OVERRIDES"].insert(
            0, pelican.settings["BIBLIOGRAPHY_TEMPLATES"]
        )


def get_generators(pelican_object):
    return BibliographyGenerator


def register():
    signals.initialized.connect(update_settings)
    signals.get_generators.connect(get_generators)
