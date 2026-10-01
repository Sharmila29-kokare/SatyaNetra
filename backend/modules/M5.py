import json
from pathlib import Path
from datetime import datetime

from backend.modules.M1 import detect_duplicates
from backend.modules.M2 import calculate_model_hash
from backend.modules.M3 import verify_ledger
from backend.modules.M4 import analyze_dataset, percentage_difference
from backend.modules.risk_engine import evaluate_risk


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATASETS = PROJECT_ROOT / "datasets"

REFERENCE = DATASETS / "reference"
INCOMING = DATASETS / "incoming"

MODELS = PROJECT_ROOT / "models"

MODEL = MODELS / "model.pt"
REGISTRY = MODELS / "model_registry.json"

REPORTS = PROJECT_ROOT / "backend" / "reports"

REPORTS.mkdir(exist_ok=True)


# ==================================================
# M1 - DATASET INTEGRITY
# ==================================================

def run_m1():

    try:

        duplicates = detect_duplicates(DATASETS)

        return {
            "status": "REVIEW" if len(duplicates) > 0 else "PASS",
            "duplicate_count": int(len(duplicates)),
            "evidence": duplicates[:10]
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "duplicate_count": 0,
            "evidence": [],
            "reason": str(e)
        }


# ==================================================
# M2 - MODEL INTEGRITY
# ==================================================

def run_m2():

    if not MODEL.exists():

        return {
            "status": "UNAVAILABLE",
            "reason": "Model file not found."
        }

    if not REGISTRY.exists():

        return {
            "status": "UNAVAILABLE",
            "reason": "Model registry not found."
        }

    try:

        with open(REGISTRY, "r") as file:
            registry = json.load(file)

        registered_hash = registry["sha256"]

        current_hash = calculate_model_hash(MODEL)

        verified = registered_hash == current_hash

        return {
            "status": "PASS" if verified else "FAIL",
            "registered_sha256": registered_hash,
            "current_sha256": current_hash
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "reason": str(e)
        }


# ==================================================
# M3 - PROVENANCE
# ==================================================

def run_m3():

    try:

        verified = verify_ledger()

        return {
            "status": "PASS" if verified else "FAIL",
            "ledger_verified": bool(verified)
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "ledger_verified": False,
            "reason": str(e)
        }


# ==================================================
# M4 - SHIFT ANALYSIS
# ==================================================

def run_m4():

    try:

        reference = analyze_dataset(REFERENCE)

        incoming = analyze_dataset(INCOMING)

        if reference is None or incoming is None:

            return {
                "status": "UNAVAILABLE",
                "reason":
                    "Reference or incoming dataset unavailable."
            }

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

        overall_shift = (
            brightness_shift +
            width_shift +
            height_shift
        ) / 3

        shift_detected = overall_shift >= 20

        return {
            "status":
                "SHIFT_DETECTED"
                if shift_detected
                else "PASS",

            "overall_shift_percent":
                float(round(overall_shift, 2)),

            "brightness_shift_percent":
                float(round(brightness_shift, 2)),

            "width_shift_percent":
                float(round(width_shift, 2)),

            "height_shift_percent":
                float(round(height_shift, 2))
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "reason": str(e)
        }


# ==================================================
# RISK ENGINE
# ==================================================

def calculate_overall_risk(m1, m2, m3, m4):

    result = evaluate_risk(

        m1_duplicate_count=
            m1.get("duplicate_count", 0),

        m2_model_integrity=
            m2.get("status") == "PASS",

        m3_ledger_integrity=
            m3.get("status") == "PASS",

        m4_shift_detected=
            m4.get("status") == "SHIFT_DETECTED"
    )

    return result


# ==================================================
# COVERAGE STATEMENT
# ==================================================

def generate_coverage_statement():

    return {

        "supported": [

            "Near-duplicate image detection",

            "Model file integrity using SHA-256",

            "Tamper-evident audit ledger verification",

            "Basic image-statistics distribution shift detection",

            "Evidence-based risk assessment"
        ],

        "not_supported": [

            "Adaptive attackers aware of the detectors",

            "Very-low-rate clean-label poisoning",

            "Conclusive proof of backdoor absence under black-box access",

            "Hardware or firmware compromise",

            "Signing-key compromise",

            "Advanced trigger reconstruction",

            "Full MMD, KS, Frechet-distance and domain-classifier analysis"
        ],

        "operating_mode":
            "Fully offline MVP with no cloud or external API dependency.",

        "data_policy":
            "Development and evaluation use public or synthetic data only."
    }


# ==================================================
# GENERATE JSON REPORT
# ==================================================

def generate_report():

    print()
    print("Running SatyaNetra M5...")
    print()

    # Run modules

    m1 = run_m1()

    m2 = run_m2()

    m3 = run_m3()

    m4 = run_m4()

    # Risk assessment

    risk_result = calculate_overall_risk(
        m1,
        m2,
        m3,
        m4
    )

    # Final report

    report = {

        "report_name":
            "SatyaNetra Assurance Report",

        "problem_statement":
            "PS 26228",

        "generated_at":
            datetime.now().isoformat(),

        "modules": {

            "M1_dataset_integrity":
                m1,

            "M2_model_integrity":
                m2,

            "M3_provenance":
                m3,

            "M4_shift_analysis":
                m4
        },

        "risk_assessment": {

            "risk_score":
                int(risk_result["risk_score"]),

            "disposition":
                risk_result["disposition"],

            "findings":
                risk_result["findings"]
        },

        "coverage_statement":
            generate_coverage_statement()
    }

    # JSON path

    json_path = REPORTS / "satyanetra_report.json"

    # FIX FOR NUMPY VALUES

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=lambda obj:
                obj.item()
                if hasattr(obj, "item")
                else str(obj)
        )

    return report, json_path


# ==================================================
# GENERATE HTML REPORT
# ==================================================

def generate_html(report):

    risk = report["risk_assessment"]

    modules = report["modules"]

    coverage = report["coverage_statement"]

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>SatyaNetra Assurance Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f4f7fb;
    color: #1f2937;
}}

.header {{
    background: #0b3d91;
    color: white;
    padding: 25px;
    border-radius: 12px;
}}

.header h1 {{
    margin: 0;
    font-size: 32px;
}}

.card {{
    background: white;
    padding: 22px;
    margin-top: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

.status {{
    font-size: 25px;
    font-weight: bold;
}}

.score {{
    font-size: 20px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    background: #e5efff;
}}

th, td {{
    padding: 13px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}}

.pass {{
    font-weight: bold;
}}

ul {{
    line-height: 1.8;
}}

.footer {{
    margin-top: 30px;
    font-size: 13px;
    color: #666;
}}

</style>

</head>


<body>


<div class="header">

<h1>SatyaNetra</h1>

<p>
Trustworthy Computer Vision Integrity Assurance
</p>

<p>
Problem Statement: PS 26228
</p>

<p>
Generated: {report["generated_at"]}
</p>

</div>


<div class="card">

<h2>Overall Assessment</h2>

<p class="status">
Disposition:
{risk["disposition"]}
</p>

<p class="score">
Risk Score:
{risk["risk_score"]}
</p>

</div>


<div class="card">

<h2>Module Results</h2>

<table>

<tr>

<th>Module</th>

<th>Status</th>

<th>Evidence</th>

</tr>


<tr>

<td>M1 – Dataset Integrity</td>

<td>
{modules["M1_dataset_integrity"]["status"]}
</td>

<td>
Duplicate count:
{modules["M1_dataset_integrity"].get("duplicate_count", "N/A")}
</td>

</tr>


<tr>

<td>M2 – Model Integrity</td>

<td>
{modules["M2_model_integrity"]["status"]}
</td>

<td>
SHA-256 fingerprint verification
</td>

</tr>


<tr>

<td>M3 – Provenance</td>

<td>
{modules["M3_provenance"]["status"]}
</td>

<td>
Audit ledger verification
</td>

</tr>


<tr>

<td>M4 – Shift Analysis</td>

<td>
{modules["M4_shift_analysis"]["status"]}
</td>

<td>
Overall shift:
{modules["M4_shift_analysis"].get("overall_shift_percent", "N/A")}%
</td>

</tr>


</table>

</div>


<div class="card">

<h2>Risk Findings</h2>

<table>

<tr>

<th>Module</th>

<th>Severity</th>

<th>Finding</th>

<th>Recommendation</th>

</tr>

{
"".join(
    f'''
<tr>
<td>{finding["module"]}</td>
<td>{finding["severity"]}</td>
<td>{finding["finding"]}</td>
<td>{finding["recommendation"]}</td>
</tr>
'''
    for finding in risk["findings"]
)

}

</table>

</div>


<div class="card">

<h2>Coverage Statement</h2>

<h3>Supported</h3>

<ul>

{
"".join(
    f"<li>{item}</li>"
    for item in coverage["supported"]
)
}

</ul>


<h3>Known Limitations</h3>

<ul>

{
"".join(
    f"<li>{item}</li>"
    for item in coverage["not_supported"]
)
}

</ul>


<p>
<strong>Operating Mode:</strong>
{coverage["operating_mode"]}
</p>


<p>
<strong>Data Policy:</strong>
{coverage["data_policy"]}
</p>

</div>


<div class="footer">

Generated locally by SatyaNetra.
No external API or cloud service is required.

</div>


</body>

</html>
"""

    html_path = REPORTS / "satyanetra_report.html"

    with open(
        html_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    return html_path


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    report, json_path = generate_report()

    html_path = generate_html(report)

    print()
    print("==========================================")
    print("       SATYANETRA M5 REPORT")
    print("==========================================")

    print()

    print(
        "Risk Score:",
        report["risk_assessment"]["risk_score"]
    )

    print(
        "Disposition:",
        report["risk_assessment"]["disposition"]
    )

    print()

    print("JSON report:")

    print(json_path)

    print()

    print("HTML report:")

    print(html_path)

    print()

    print("✅ M5 REPORT GENERATED")