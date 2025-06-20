import os

import pytest
from PIL import Image

from colorblind_snapshot_analyzer import analyze

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")


def test_rmsdiff_identical_images():
    img1 = Image.new("RGB", (10, 10), color="red")
    img2 = Image.new("RGB", (10, 10), color="red")
    diff = analyze.rmsdiff(img1, img2)
    assert diff == 0


def test_rmsdiff_different_images():
    img1 = Image.new("RGB", (10, 10), color="red")
    img2 = Image.new("RGB", (10, 10), color="blue")
    diff = analyze.rmsdiff(img1, img2)
    assert diff > 0


def test_analyze_images_report(monkeypatch):
    img1 = Image.new("RGB", (10, 10), color="red")
    img2 = Image.new("RGB", (10, 10), color="blue")

    def fake_sim(img, cb_type):
        return img2 if cb_type == "protanopia" else img

    monkeypatch.setattr(analyze, "simulate_colorblind_cli", fake_sim)
    images = [("test.png", img1)]
    report = analyze.analyze_images(images)
    assert "test.png" in report
    assert "protanopia vision" in report
    assert "RMS diff" in report


def test_real_images_in_images_folder(monkeypatch):
    if not os.path.isdir(IMAGES_DIR):
        pytest.skip("images folder not found")
    image_files = [
        f
        for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    if not image_files:
        pytest.skip("No images in images folder")
    # Patch simulate_colorblind_cli to just return the original image for speed
    monkeypatch.setattr(analyze, "simulate_colorblind_cli", lambda img, cb_type: img)
    images = []
    for fname in image_files:
        img = Image.open(os.path.join(IMAGES_DIR, fname)).convert("RGB")
        images.append((fname, img))
    report = analyze.analyze_images(images)
    for fname in image_files:
        assert fname in report
        assert "RMS diff=0.00" in report  # since we return the same image
