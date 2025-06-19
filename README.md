# Colorblind Snapshot Analyzer GitHub Action

This GitHub Action scans images added or changed in a Pull Request and runs colorblind vision simulations (Protanopia, Deuteranopia, Tritanopia) on them. It posts a textual report on the PR commenting whether the simulation succeeded, helping maintain color accessibility.

## Usage

**Important:**
To allow the action to comment on pull requests, add the following permissions block to your workflow:

```yaml
permissions:
  pull-requests: write
  contents: read
```

**Note:** This action currently only works on public repositories.

Add the action to your workflow triggered on pull requests:

```yaml
name: Colorblind Accessibility Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  pull-requests: write
  contents: read

jobs:
  colorblind-snapshot-analyzer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Colorblind Snapshot Analyzer
        uses: NotTheRealWallyx/colorblind-snapshot-analyzer@1.0.0
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

### Inputs

| Name       | Required | Description                                                                                 |
| ---------- | -------- | ------------------------------------------------------------------------------------------- |
| repo-token | Yes      | GitHub token to post comments and access PR files. Typically `${{ secrets.GITHUB_TOKEN }}`. |

### Output

Posts a PR comment listing the images analyzed and simulation status for each colorblind type.

### Example Output

```
### 🎨 Colorblind Snapshot Report

**Note:** RMS diff measures the visual difference between the original and simulated image. A higher RMS diff means more difference (more visible change for colorblind users), while a lower value means less difference (potentially less colorblind-friendly).


**Non Colorblind Friendly Images.png**:
- ✅ protanopia vision: Image is likely colorblind-friendly (RMS diff=45.70)
- ✅ deuteranopia vision: Image is likely colorblind-friendly (RMS diff=39.71)
- ⚠️ tritanopia vision: Image may NOT be colorblind-friendly (RMS diff=4.35)

**tzosjk2q91511.jpg**:
- ✅ protanopia vision: Image is likely colorblind-friendly (RMS diff=26.79)
- ✅ deuteranopia vision: Image is likely colorblind-friendly (RMS diff=21.13)
- ✅ tritanopia vision: Image is likely colorblind-friendly (RMS diff=47.16)
```

## Development

To set up locally:

```bash
poetry install
```

To run on a pull request (set environment variables as needed):

```bash
poetry run python -m colorblind_snapshot_analyzer.main
```

You may need to set the following environment variables for local testing:

- `GITHUB_TOKEN` (a GitHub personal access token)
- `GITHUB_REPOSITORY` (e.g., `username/repo`)
- `PR_NUMBER` (the pull request number)

### Run Locally on Images in a Folder

To analyze all images in a local folder (default: `images`):

1. Place your images in a folder named `images` (or set the `LOCAL_IMAGE_DIR` environment variable to your folder).
2. Run:

```bash
poetry run python -m colorblind_snapshot_analyzer.local
```

This will print a colorblind accessibility report for all images in the folder.

## Limitations

**Currently, this action only works on public repositories.**

This is because the action is only able to retrieve images from pull requests in public repositories. For private repositories or PRs from forks, GitHub restricts access to certain resources and files, which prevents the action from analyzing images or posting comments. This is a known limitation and is being investigated for possible workarounds or future support.

## Future Work

- Make action work on private repositories
- Investigate adding use of better vision deficiency simulators to have a better benchmark on what colorblind friendly is

## License

MIT © NotTheRealWallyx
