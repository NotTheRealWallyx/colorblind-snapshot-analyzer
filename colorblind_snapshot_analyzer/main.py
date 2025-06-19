import os
import re
import requests
from PIL import Image
from io import BytesIO
from daltonize import daltonize
from github import Github

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
COLORBLIND_TYPES = ["protanopia", "deuteranopia", "tritanopia"]
COLORBLIND_TYPE_MAP = {
    "protanopia": "p",
    "deuteranopia": "d",
    "tritanopia": "t",
}


def simulate_colorblind(img, cb_type):
    dalton_type = COLORBLIND_TYPE_MAP[cb_type]
    return daltonize.daltonize(img, dalton_type)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set")
        exit(1)
    g = Github(token)
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")
    if not repo_name or not pr_number:
        print("GITHUB_REPOSITORY or PR_NUMBER not set")
        exit(1)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    files = pr.get_files()
    image_files = [
        f
        for f in files
        if any(f.filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
    ]
    pr_body = pr.body or ""
    pr_image_urls = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", pr_body)
    if not image_files and not pr_image_urls:
        print("No image files or PR body images found in this pull request.")
        return
    markdown_report = "### 🎨 Colorblind Snapshot Report\n\n"
    for f in image_files:
        try:
            response = requests.get(f.raw_url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            markdown_report += f"\n**{os.path.basename(f.filename)}**:\n"
            for cb_type in COLORBLIND_TYPES:
                try:
                    _ = simulate_colorblind(img, cb_type)
                    markdown_report += (
                        f"- ✅ Simulated {cb_type} vision successfully.\n"
                    )
                except Exception as e:
                    markdown_report += (
                        f"- ❌ Failed to simulate {cb_type} vision. Error: {e}\n"
                    )
        except Exception as e:
            markdown_report += f"❌ Failed to fetch/process {f.filename}: {e}\n"
    for url in pr_image_urls:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            file_name = url.split("/")[-1]
            markdown_report += f"\n**[PR Body] {file_name}**:\n"
            for cb_type in COLORBLIND_TYPES:
                try:
                    _ = simulate_colorblind(img, cb_type)
                    markdown_report += (
                        f"- ✅ Simulated {cb_type} vision successfully.\n"
                    )
                except Exception as e:
                    markdown_report += (
                        f"- ❌ Failed to simulate {cb_type} vision. Error: {e}\n"
                    )
        except Exception as e:
            markdown_report += f"❌ Failed to fetch/process {url}: {e}\n"
    pr.create_issue_comment(markdown_report)


if __name__ == "__main__":
    main()
