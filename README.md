# Colorblind Snapshot Analyzer GitHub Action

This GitHub Action scans images added or changed in a Pull Request and runs colorblind vision simulations (Protanopia, Deuteranopia, Tritanopia) on them. It posts a textual report on the PR commenting whether the simulation succeeded, helping maintain color accessibility.

## Usage

Add the action to your workflow triggered on pull requests:

```yaml
name: Colorblind Accessibility Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  colorblind-snapshot-analyzer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Colorblind Snapshot Analyzer
        uses: your-username/your-repo@main
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

### Inputs

| Name       | Required | Description                                                                                 |
| ---------- | -------- | ------------------------------------------------------------------------------------------- |
| repo-token | Yes      | GitHub token to post comments and access PR files. Typically `${{ secrets.GITHUB_TOKEN }}`. |

### Output

Posts a PR comment listing the images analyzed and simulation status for each colorblind type.

## Development

To set up locally:

```bash
poetry install
```

To run locally (set environment variables as needed):

```bash
poetry run python -m colorblind_snapshot_analyzer.main
```

You may need to set the following environment variables for local testing:

- `GITHUB_TOKEN` (a GitHub personal access token)
- `GITHUB_REPOSITORY` (e.g., `username/repo`)
- `PR_NUMBER` (the pull request number)

## License

MIT © NotTheRealWallyx
