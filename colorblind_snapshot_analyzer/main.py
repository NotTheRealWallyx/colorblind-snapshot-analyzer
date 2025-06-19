import os
import re
import requests
from PIL import Image
from io import BytesIO
from daltonize import daltonize
from github import Github
from PIL import ImageChops
import math

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


def rmsdiff(im1, im2):
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
    return rms


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
                    sim_img = simulate_colorblind(img, cb_type)
                    diff = rmsdiff(img, sim_img)
                    if diff < 10:
                        markdown_report += f"- ⚠️ {cb_type} vision: Image may NOT be colorblind-friendly (RMS diff={diff:.2f})\n"
                    else:
                        markdown_report += f"- ✅ {cb_type} vision: Image is likely colorblind-friendly (RMS diff={diff:.2f})\n"
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
                    sim_img = simulate_colorblind(img, cb_type)
                    diff = rmsdiff(img, sim_img)
                    if diff < 10:
                        markdown_report += f"- ⚠️ {cb_type} vision: Image may NOT be colorblind-friendly (RMS diff={diff:.2f})\n"
                    else:
                        markdown_report += f"- ✅ {cb_type} vision: Image is likely colorblind-friendly (RMS diff={diff:.2f})\n"
                except Exception as e:
                    markdown_report += (
                        f"- ❌ Failed to simulate {cb_type} vision. Error: {e}\n"
                    )
        except Exception as e:
            markdown_report += f"❌ Failed to fetch/process {url}: {e}\n"
    pr.create_issue_comment(markdown_report)


if __name__ == "__main__":
    main()
