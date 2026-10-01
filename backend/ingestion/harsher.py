import hashlib
from pathlib import Path


def calculate_sha256(file_path):
    """
    Calculate SHA-256 hash of a file.
    """
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def calculate_string_sha256(data):
    """
    Calculate SHA-256 hash of a string.
    """
    if not isinstance(data, str):
        data = str(data)

    return hashlib.sha256(data.encode("utf-8")).hexdigest()


if __name__ == "__main__":

    # Locate test.txt relative to this Python file
    current_folder = Path(__file__).parent
    test_file = current_folder / "test.txt"

    if test_file.exists():
        file_hash = calculate_sha256(test_file)
        print("File:", test_file)
        print("SHA-256:", file_hash)
    else:
        print("test.txt not found.")