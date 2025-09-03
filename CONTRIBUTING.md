# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

We love your input!
We want to make contributing to this project as easy and
transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## General Tips for Working on GitHub

* Register for a free [GitHub account](https://github.com/signup) if you haven't already.
* You can use [GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) for formatting text and adding images.
* To help mitigate notification spam, please avoid "bumping" issues with no
  activity.
  (To vote an issue up or down, use a :thumbsup: or :thumbsdown: reaction.)
* Please avoid pinging members with `@` unless they've previously expressed
  interest or involvement with that particular issue.
* Familiarize yourself with [this list of discussion anti-patterns](https://github.com/bradfitz/issue-tracker-behaviors)
  and make every effort to avoid them.

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/pheus/netbox-aci-plugin/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

NetBox ACI Plugin could always use more documentation, whether as part of the
official NetBox ACI Plugin docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at
https://github.com/pheus/netbox-aci-plugin/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute?
Here's how to set up `netbox-aci-plugin` for local development.

1. Fork the `netbox-aci-plugin` repo on GitHub.
2. Clone your fork locally

    ```
    $ git clone git@github.com:your_name_here/netbox-aci-plugin.git
    ```

3. Activate the NetBox virtual environment (see the NetBox documentation under
   [Setting up a Development Environment](https://docs.netbox.dev/en/stable/development/getting-started/)):

    ```
    $ source ~/.venv/netbox/bin/activate
    ```

4. Add the plugin to NetBox virtual environment in Develop mode
   (see [Plugins Development](https://docs.netbox.dev/en/stable/plugins/development/)):

    To ease development, it is recommended to go ahead and install the plugin
    at this point using setuptools' develop mode.
   This will create symbolic
    links within your Python environment to the plugin development directory.
    Call `pip` from the plugin's root directory with the `-e` (editable) flag:

    ```
    $ pip3 install -e .
    ```

    More information on editable builds can be found at
    [Editable installs for pyproject.toml ](https://peps.python.org/pep-0660/).

5. Create a branch for local development:

    ```
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

    Now you can make your changes locally.

6. Commit your changes and push your branch to GitHub:

    ```
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.10, 3.11 and 3.12.
   Check
   https://github.com/pheus/netbox-aci-plugin/actions
   and make sure that the tests pass for all supported Python versions.

## Deploying

See **[Releasing guide](docs/development/releasing.md)** for the versioning, tagging,
and publish process (Trusted Publishing to PyPI and a draft GitHub Release
on tag push).
