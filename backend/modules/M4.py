from pathlib import Path
from PIL import Image
import numpy as np


# --------------------------------------------------
# Extract image statistics
# --------------------------------------------------

def get_image_statistics(image_path):

    try:
        image = Image.open(image_path).convert("RGB")

        image_array = np.array(image)

        brightness = np.mean(image_array)

        width, height = image.size

        return {
            "brightness": brightness,
            "width": width,
            "height": height
        }

    except Exception as e:

        print(f"Could not process {image_path}: {e}")
        return None


# --------------------------------------------------
# Analyze dataset
# --------------------------------------------------

def analyze_dataset(folder):

    folder = Path(folder)

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    images = [
        file for file in folder.iterdir()
        if file.suffix.lower() in image_extensions
    ]

    statistics = []

    for image in images:

        result = get_image_statistics(image)

        if result:
            statistics.append(result)

    if not statistics:
        return None

    avg_brightness = np.mean(
        [x["brightness"] for x in statistics]
    )

    avg_width = np.mean(
        [x["width"] for x in statistics]
    )

    avg_height = np.mean(
        [x["height"] for x in statistics]
    )

    return {
        "image_count": len(statistics),
        "average_brightness": avg_brightness,
        "average_width": avg_width,
        "average_height": avg_height
    }


# --------------------------------------------------
# Calculate percentage difference
# --------------------------------------------------

def percentage_difference(reference, incoming):

    if reference == 0:
        return 0

    return abs(incoming - reference) / reference * 100


# --------------------------------------------------
# Detect dataset shift
# --------------------------------------------------

def detect_shift(reference_folder, incoming_folder):

    reference = analyze_dataset(reference_folder)
    incoming = analyze_dataset(incoming_folder)

    if reference is None or incoming is None:

        print("❌ Could not analyze datasets.")
        return

    brightness_shift = percentage_difference(
        reference["average_brightness"],
        incoming["average_brightness"]
    )

    width_shift = percentage_difference(
        reference["average_width"],
        incoming["average_width"]
    )

    height_shift = percentage_difference(
        reference["average_height"],
        incoming["average_height"]
    )

    # Overall shift
    overall_shift = np.mean([
        brightness_shift,
        width_shift,
        height_shift
    ])

    print("\n==========================================")
    print("        M4 SHIFT & ANOMALY ANALYSIS")
    print("==========================================")

    print("\nREFERENCE DATASET")
    print("-----------------")
    print("Images:", reference["image_count"])
    print(
        "Average brightness:",
        round(reference["average_brightness"], 2)
    )
    print(
        "Average width:",
        round(reference["average_width"], 2)
    )
    print(
        "Average height:",
        round(reference["average_height"], 2)
    )

    print("\nINCOMING DATASET")
    print("----------------")
    print("Images:", incoming["image_count"])
    print(
        "Average brightness:",
        round(incoming["average_brightness"], 2)
    )
    print(
        "Average width:",
        round(incoming["average_width"], 2)
    )
    print(
        "Average height:",
        round(incoming["average_height"], 2)
    )

    print("\nSHIFT ANALYSIS")
    print("----------------")

    print(
        "Brightness shift:",
        round(brightness_shift, 2),
        "%"
    )

    print(
        "Width shift:",
        round(width_shift, 2),
        "%"
    )

    print(
        "Height shift:",
        round(height_shift, 2),
        "%"
    )

    print(
        "Overall shift:",
        round(overall_shift, 2),
        "%"
    )

    # Threshold for MVP
    threshold = 20

    print("\nRESULT")
    print("------")

    if overall_shift >= threshold:

        print("⚠️ SHIFT DETECTED")
        print("Incoming data distribution differs")
        print("significantly from the reference dataset.")

    else:

        print("✅ NO SIGNIFICANT SHIFT DETECTED")
        print("Incoming data is similar to reference data.")


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent.parent

    reference_folder = project_root / "datasets" / "reference"

    incoming_folder = project_root / "datasets" / "incoming"

    detect_shift(
        reference_folder,
        incoming_folder
    )