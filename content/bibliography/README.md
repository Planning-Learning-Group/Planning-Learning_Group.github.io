## Adding/Editing Publications

**Summary**: To add a paper or adapt a Bibtex entry, make the necessary changes
via a pull request to the Basel bib repo at https://github.com/aibasel/bib, then
run `make update-bib` in the root directory of the homepage repo and add
an entry to [metadata.yaml](metadata.yaml).

**Important**: Do not edit the files in this directory directly, since they will
be overwritten later.

**Detailed Instructions**:

1. Visit https://github.com/aibasel/bib and click "Fork" button.
2. `git clone git@github.com:<your-username>/bib.git`
3. `cd bib`
4. Make changes to the Bibtex files.
5. Run `./tests/format-bib.sh` and `./tests/run-tests.sh`.
6. Commit your changes.
7. `git push origin main`
8. Make a pull request from your fork to the aibasel repo (by clicking the
   suggestion in the terminal) and mark Jendrik or Daniel as a reviewer.

After the pull request is merged:

1. Call `make update-bib` in the root dir of the website repo.
2. Add an entry in [metadata.yaml](metadata.yaml).
3. Add the paper, slides and poster PDFs to `content/papers` and they'll be
   added to the website automatically.

The goal is that all our publications are in the Basel bib repo. Only add
publications that should not be part of the Basel bib repo to the `extra.bib`
file.

#### Workshop Papers

In general, we omit workshop papers that have already been accepted elsewhere
before we submitted the paper to the workshop. However, when a workshop paper is
later published somewhere else, we keep it in the list and add a "superseded by
..." note.
