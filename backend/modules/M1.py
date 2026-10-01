import os
from pathlib import Path
from PIL import Image
import imagehash


def calculate_image_hash(image_path):
    """
    Calculate perceptual hash of an image.
    Similar images will have similar hashes.
    """
    try:
        image = Image.open(image_path)
        return imagehash.phash(image)

    except Exception as e:
        print(f"Could not process {image_path}: {e}")
        return None


def detect_duplicates(dataset_folder, threshold=5):
    """
    Detect near-duplicate images in a dataset.

    threshold:
    Smaller value = more similar images required.
    """

    dataset_folder = Path(dataset_folder)

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    images = [
        file for file in dataset_folder.rglob("*")
        if file.suffix.lower() in image_extensions
    ]

    print(f"\nImages found: {len(images)}")

    hashes = {}

    for image_path in images:

        image_hash = calculate_image_hash(image_path)

        if image_hash is not None:
            hashes[image_path] = image_hash

    duplicates = []

    image_list = list(hashes.items())

    for i in range(len(image_list)):

        path1, hash1 = image_list[i]

        for j in range(i + 1, len(image_list)):

            path2, hash2 = image_list[j]

            distance = hash1 - hash2

            if distance <= threshold:

                duplicates.append({
                    "image1": str(path1),
                    "image2": str(path2),
                    "hash_distance": distance
                })

    return duplicates


def print_results(duplicates):

    print("\n========== M1 DATASET INTEGRITY ==========")

    if not duplicates:

        print("✅ No near-duplicate images detected.")

        return

    print(f"⚠️ Near-duplicates detected: {len(duplicates)}")

    for item in duplicates:

        print("\nImage 1:")
        print(item["image1"])

        print("Image 2:")
        print(item["image2"])

        print("Hash distance:")
        print(item["hash_distance"])

    print("\n⚠️ Dataset requires review.")


if __name__ == "__main__":

    dataset_path = Path(__file__).resolve().parent.parent.parent / "datasets"

    duplicates = detect_duplicates(dataset_path)

    print_results(duplicates)