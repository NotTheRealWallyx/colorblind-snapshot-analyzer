import os

from PIL import Image

from .analyze import analyze_images

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


def main():
    images = []
    image_dir = os.environ.get("LOCAL_IMAGE_DIR", "images")
    for fname in os.listdir(image_dir):
        if any(fname.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            try:
                img = Image.open(os.path.join(image_dir, fname)).convert("RGB")
                images.append((fname, img))
            except Exception as e:
                images.append((fname, None, f"Failed to open: {e}"))
    report = analyze_images(images)
    print(report)


if __name__ == "__main__":
    main()
