
# Homepage

The website is generated with the [Pelican](https://docs.getpelican.com/)
static site generator.


## The Repository

The website repository has two main branches. The `main` branch is where all the
Pelican configuration files, the website data and templates are stored. It is a
regular Git branch. The `gh-pages` branch is a derivative branch that is used to
store the actual website. All content in the `gh-pages` branch is overwritten on
every push to the `main` branch.


## Building the Website Locally

The following assumes that you have set up a Python virtual environment:

    # Install venv module.
    sudo apt install python3-venv

    # If PYTHONPATH is set, unset it to obtain a clean environment.
    unset PYTHONPATH

    # Create and activate a Python virtual environment.
    python3 -m venv --prompt mrlab-website .venv
    source .venv/bin/activate

    # Upgrade basic packages in the virtual environment.
    pip install --upgrade pip wheel

If you use Python 3.8, you can now install the dependencies with:

    pip install -r requirements.txt

For other Python versions, use `pip install -r requirements.in`.

You can build the site locally with

    invoke livereload

and view the site by clicking on the `http://localhost:8000` link shown in
the terminal.

For debugging a failing build, use `make DEBUG=1 html`.


## Pushing the Site to Production

When you commit and push your changes, GitHub will automatically rebuild
the site.

## Publications

See [content/bibliography/README.md](content/bibliography/README.md) for
instructions on how to add or edit publications.


## Notes and References

The Pelican theme that we use is a customized version of the
[Alchemy](https://github.com/nairobilug/pelican-alchemy) theme.
Some other components currently used include:
* The [Bootstrap](https://getbootstrap.com/) CSS framework.
* The "Litera" Bootstrap theme from [Bootswatch](https://bootswatch.com/).


The university and other logos can be obtained from:
* https://media.liu.se/menu/48-LiU%20logos


Some other useful links:
* https://bootswatch.com/flatly/
* https://github.com/cocodelabs/cocode.org/issues/6
* https://favicon.io/favicon-generator/ (bg: #2c3e50, fg: #FFF, font: Lato, size:70)


## TODOs

* Add most recent awards to homepage under "Recent Awards" and rename news to "Other News".
* Allow adding relative links to news items.
* Make news prettier (https://bbbootstrap.com/snippets/latest-updates-list-68233138).
* Make paper pages.
* Only list the ten most recent news.
* Add relevant papers to project page automatically.


## Possible TODOs

* Allow overriding bibtex entries with metadata content.
* Use sticky header.
* The names of authors of publications should be links to their respective websites.


## Non-TODOs

* Show abstracts.
* Use darker link color: Cosmo, Litera and Zephyr themes look almost as nice as
  Flatly. Changing link color is involved.
* Add awards to publication list.
