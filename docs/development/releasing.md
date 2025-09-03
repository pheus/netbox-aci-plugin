# Releasing

We follow **Semantic Versioning** and **Keep a Changelog**.

- SemVer → https://semver.org/
- Keep a Changelog → https://keepachangelog.com/en/1.1.0/

## Checklist

1. **Finish code/docs**
   - README shows `pip install netbox-aci-plugin`.
   - `docs/index.md` Installing & Compatibility are correct.
2. **Changelog**
   - Add `## X.Y.Z – YYYY-MM-DD` with **Added / Changed / Fixed / Compatibility**.
3. **Version bump**
   - `pyproject.toml` → `version = "X.Y.Z"`.
4. **Tag**
   - `git tag vX.Y.Z && git push origin vX.Y.Z`
5. **CI**
   - Build wheel+sdist, `twine check`, publish to PyPI (Trusted Publishing), draft GitHub Release with only the current section from the changelog.
6. **Publish Release**
   - Review the draft notes and click **Publish**.
7. **Post-release**
   - Verify the PyPI page renders the README.
   - Announce compatibility (NetBox 4.3) if it changed.
