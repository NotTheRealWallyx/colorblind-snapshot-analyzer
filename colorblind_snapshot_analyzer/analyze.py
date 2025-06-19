import numpy as np
from PIL import ImageChops, Image
import subprocess
import tempfile
import os

COLORBLIND_TYPES = ["protanopia", "deuteranopia", "tritanopia"]
COLORBLIND_TYPE_MAP = {
    "protanopia": "p",
    "deuteranopia": "d",
    "tritanopia": "t",
}


def simulate_colorblind_cli(img, cb_type):
    dalton_type = COLORBLIND_TYPE_MAP[cb_type]
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_path = os.path.join(tmpdir, "orig.png")
        sim_path = os.path.join(tmpdir, "sim.png")
        img.save(orig_path)
        cmd = ["daltonize", "--simulate", "-t", dalton_type, orig_path, sim_path]
        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore"
        subprocess.run(cmd, check=True, env=env)
        sim_img = Image.open(sim_path).convert("RGB")
        return sim_img


def rmsdiff(im1, im2):
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = (sum_of_squares / float(im1.size[0] * im1.size[1])) ** 0.5
    return rms


def analyze_images(images):
    markdown_report = (
        "### 🎨 Colorblind Snapshot Report\n\n"
        "**Note:** RMS diff measures the visual difference between the original and simulated image. "
        "A higher RMS diff means more difference (more visible change for colorblind users), "
        "while a lower value means less difference (potentially less colorblind-friendly).\n\n"
    )
    for entry in images:
        if len(entry) == 3:
            # Error case
            name, _, error = entry
            markdown_report += f"❌ {name}: {error}\n"
            continue
        name, img = entry
        markdown_report += f"\n**{name}**:\n"
        for cb_type in COLORBLIND_TYPES:
            try:
                sim_img = simulate_colorblind_cli(img, cb_type)
                diff = rmsdiff(img, sim_img)
                if diff < 10:
                    markdown_report += f"- ⚠️ {cb_type} vision: Image may NOT be colorblind-friendly (RMS diff={diff:.2f})\n"
                else:
                    markdown_report += f"- ✅ {cb_type} vision: Image is likely colorblind-friendly (RMS diff={diff:.2f})\n"
            except Exception as e:
                markdown_report += (
                    f"- ❌ Failed to simulate {cb_type} vision. Error: {e}\n"
                )
    return markdown_report
