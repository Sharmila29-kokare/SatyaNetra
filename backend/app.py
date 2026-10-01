from pathlib import Path
import json

from backend.modules.M5 import generate_report, generate_html


# ==================================================
# TRUSTLENS-CV MAIN APPLICATION
# ==================================================

def main():

    print()
    print("==============================================")
    print("             TRUSTLENS-CV")
    print("     Computer Vision Integrity Assurance")
    print("==============================================")

    print()
    print("Problem Statement: PS 26228")
    print("Mode: Fully Offline")
    print()

    print("----------------------------------------------")
    print("Running assurance pipeline...")
    print("----------------------------------------------")

    # --------------------------------------------------
    # Run complete M1-M5 pipeline through M5
    # --------------------------------------------------

    report, json_path = generate_report()

    html_path = generate_html(report)

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    print()
    print("==============================================")
    print("              FINAL ASSESSMENT")
    print("==============================================")

    risk = report["risk_assessment"]

    print()
    print("Risk Score :", risk["risk_score"])
    print("Disposition:", risk["disposition"])

    print()
    print("MODULE STATUS")
    print("----------------------------------------------")

    modules = report["modules"]

    print(
        "M1 Dataset Integrity :",
        modules["M1_dataset_integrity"]["status"]
    )

    print(
        "M2 Model Integrity   :",
        modules["M2_model_integrity"]["status"]
    )

    print(
        "M3 Provenance        :",
        modules["M3_provenance"]["status"]
    )

    print(
        "M4 Shift Analysis    :",
        modules["M4_shift_analysis"]["status"]
    )

    print()
    print("REPORTS")
    print("----------------------------------------------")

    print("JSON :", json_path)
    print("HTML :", html_path)

    print()
    print("==============================================")
    print("       ✅ TRUSTLENS-CV AUDIT COMPLETE")
    print("==============================================")
    print()


if __name__ == "__main__":

    main()