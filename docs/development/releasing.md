# Releasing

We follow **Semantic Versioning** and **Keep a Changelog**.

- SemVer → https://semver.org/
- Keep a Changelog → https://keepachangelog.com/en/1.1.0/

## Checklist

1. **Finish code/docs**
    - Ensure the README installation and compatibility information is current.
    - Ensure `docs/index.md` installation and compatibility information is
      current.
    - Document all notable user-facing changes.

2. **Changelog**
    - Move completed entries from `## [Unreleased]` to
      `## [X.Y.Z] – YYYY-MM-DD`.
    - Include the supported NetBox versions in the compatibility notice.
    - Update the comparison links at the bottom of `CHANGELOG.md`.

3. **Version bump**
    - Update `pyproject.toml`:
      `version = "X.Y.Z"`.
    - Update `netbox_aci_plugin/__init__.py`:
      `__version__ = "X.Y.Z"`.
    - Update current-version references in the README, security policy, issue
      templates, and other release metadata as needed.

4. **Verify**
    - Push the release commit and wait for all CI checks to pass.
    - Confirm that the supported NetBox and Python test matrix passes.
    - Confirm that there are no missing migrations.
    - Build and validate the release artifacts:

      ```bash
      rm -rf build dist *.egg-info
      python -m build
      python -m twine check dist/*
      ```

    - Run the manual package-manifest check:

      ```bash
      pre-commit run check-manifest --hook-stage manual --all-files
      ```

    - Merge the release commit into `main` and wait for the CI, package-build,
      and documentation workflows to pass.

5. **Tag**
    - Tag the exact tested commit on `main`:

      ```bash
      git tag vX.Y.Z
      git push origin vX.Y.Z
      ```

6. **Automated release**
    - The tag workflow verifies that the tag matches the version in
      `pyproject.toml`.
    - It builds the wheel and source distribution and validates their metadata.
    - It publishes the distributions to PyPI using Trusted Publishing.
    - It creates a draft GitHub Release using the matching section from
      `CHANGELOG.md`.

7. **Publish Release**
    - Review the generated release notes and attached distributions.
    - Click **Publish release**.

8. **Post-release**
    - Verify that the new version is available on PyPI.
    - Verify that the PyPI page renders the README correctly.
    - Verify that the documentation site has been deployed successfully.
    - Announce updated NetBox compatibility when it has changed.
