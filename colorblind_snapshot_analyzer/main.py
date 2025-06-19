import os
import re
import requests
from PIL import Image
from io import BytesIO
from github import Github
from .analyze import analyze_images


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


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
    # Download images from PR files
    images = []
    for f in image_files:
        try:
            response = requests.get(f.raw_url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            images.append((os.path.basename(f.filename), img))
        except Exception as e:
            images.append(
                (os.path.basename(f.filename), None, f"Failed to fetch/process: {e}")
            )
    # Download images from PR body
    for url in pr_image_urls:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            file_name = url.split("/")[-1]
            images.append((f"[PR Body] {file_name}", img))
        except Exception as e:
            images.append((f"[PR Body] {url}", None, f"Failed to fetch/process: {e}"))
    markdown_report = analyze_images(images)
    pr.create_issue_comment(markdown_report)


if __name__ == "__main__":
    main()
