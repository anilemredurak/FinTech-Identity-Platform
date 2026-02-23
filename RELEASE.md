# Releasing

This repository supports creating GitHub releases via Actions. Use the `Create Release` workflow in the repository Actions tab or run the workflow from the CLI.

Steps to create a release from the GitHub UI:

1. Go to the repository Actions -> `Create Release` workflow.
2. Click `Run workflow`.
3. Provide the `tag` (for example `v1.0.0`), optional `name` and `body` (release notes). Set `draft`/`prerelease` as needed.

Notes:
- The workflow uses the built-in `GITHUB_TOKEN` to create the release. No extra secrets are required for basic release creation.
- Add changelog entries to `CHANGELOG.md` before releasing and paste release notes into the `body` field.
- To attach build artifacts, extend the workflow to build and upload assets using `actions/upload-release-asset`.

Example CLI (GitHub CLI):

```bash
# create annotated tag locally
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# OR trigger the workflow manually from the Actions UI
```
