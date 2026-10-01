import hashlib
import json
from pathlib import Path


# --------------------------------------------------
# Calculate SHA-256 hash of model file
# --------------------------------------------------

def calculate_model_hash(model_path):
    sha256 = hashlib.sha256()

    with open(model_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


# --------------------------------------------------
# Register trusted model
# --------------------------------------------------

def register_model(model_path, registry_path):
    model_path = Path(model_path)
    registry_path = Path(registry_path)

    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return False

    model_hash = calculate_model_hash(model_path)

    registry = {
        "model_name": model_path.name,
        "model_path": str(model_path),
        "sha256": model_hash
    }

    with open(registry_path, "w") as file:
        json.dump(registry, file, indent=4)

    print("\n========== M2 MODEL REGISTRATION ==========")
    print("Model:", model_path.name)
    print("SHA-256:", model_hash)
    print("✅ Trusted model registered.")

    return True


# --------------------------------------------------
# Verify model integrity
# --------------------------------------------------

def verify_model(model_path, registry_path):

    model_path = Path(model_path)
    registry_path = Path(registry_path)

    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        return False

    if not registry_path.exists():
        print("❌ Model registry not found.")
        return False

    with open(registry_path, "r") as file:
        registry = json.load(file)

    registered_hash = registry["sha256"]
    current_hash = calculate_model_hash(model_path)

    print("\n========== M2 MODEL INTEGRITY ==========")
    print("Model:", model_path.name)
    print("Registered SHA-256:")
    print(registered_hash)

    print("\nCurrent SHA-256:")
    print(current_hash)

    if registered_hash == current_hash:

        print("\n✅ MODEL INTEGRITY VERIFIED")
        print("No model substitution or file modification detected.")

        return True

    else:

        print("\n❌ MODEL INTEGRITY FAILED")
        print("Model hash does not match the registered model.")
        print("⚠️ Possible model modification or substitution detected.")

        return False


# --------------------------------------------------
# Demo
# --------------------------------------------------

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent.parent

    models_folder = project_root / "models"

    model_path = models_folder / "model.pt"

    registry_path = models_folder / "model_registry.json"

    if not model_path.exists():

        print("⚠️ model.pt not found.")

    elif not registry_path.exists():

        register_model(
            model_path,
            registry_path
        )

    else:

        verify_model(
            model_path,
            registry_path
        )

        verify_model(
            model_path,
            registry_path
        )