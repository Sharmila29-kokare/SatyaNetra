import streamlit as st
import json
from pathlib import Path

from backend.modules.M1 import detect_duplicates
from backend.modules.M2 import calculate_model_hash
from backend.modules.M3 import verify_ledger
from backend.modules.M4 import analyze_dataset, percentage_difference
from backend.modules.risk_engine import evaluate_risk
from backend.modules.M5 import generate_report, generate_html


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATASETS = PROJECT_ROOT / "datasets"

REFERENCE = DATASETS / "reference"
INCOMING = DATASETS / "incoming"

MODELS = PROJECT_ROOT / "models"

MODEL = MODELS / "model.pt"
REGISTRY = MODELS / "model_registry.json"

REPORTS = PROJECT_ROOT / "backend" / "reports"

REPORTS.mkdir(exist_ok=True)
INCOMING.mkdir(exist_ok=True)
REFERENCE.mkdir(exist_ok=True)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="SatyaNetra",
    page_icon="🛡️",
    layout="wide"
)


# ==========================================================
# CSS
# ==========================================================

st.markdown(
    """
    <style>

    .title {
        font-size: 40px;
        font-weight: 700;
        color: #0b3d91;
    }

    .subtitle {
        font-size: 18px;
        color: #555;
    }

    .module-card {
        padding: 18px;
        border-radius: 12px;
        background: #f5f8ff;
        border: 1px solid #d9e4f5;
        text-align: center;
        min-height: 140px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    '<div class="title">🛡️ SatyaNetra</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Trustworthy Computer Vision Integrity Assurance'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "**Problem Statement:** PS 26228  |  "
    "**Mode:** Fully Offline"
)

st.divider()


# ==========================================================
# SESSION STATE
# ==========================================================

if "results" not in st.session_state:
    st.session_state.results = None


# ==========================================================
# UPLOAD TEST DATA
# ==========================================================

st.subheader("📤 Upload Test Data")

st.info(
    "Upload images to test the SatyaNetra pipeline. "
    "Uploaded images are stored locally in datasets/incoming/."
)

uploaded_images = st.file_uploader(
    "Choose test images",
    type=[
        "jpg",
        "jpeg",
        "png",
        "bmp",
        "webp"
    ],
    accept_multiple_files=True
)


if uploaded_images:

    st.write(
        f"**{len(uploaded_images)} image(s) selected.**"
    )

    for uploaded_file in uploaded_images:

        st.write(
            "•",
            uploaded_file.name
        )


    if st.button(
        "📥 Save Uploaded Images",
        use_container_width=True
    ):

        saved_count = 0

        for uploaded_file in uploaded_images:

            destination = (
                INCOMING /
                uploaded_file.name
            )

            with open(
                destination,
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )

            saved_count += 1

        st.success(
            f"{saved_count} image(s) saved to "
            "datasets/incoming/."
        )


# ==========================================================
# CURRENT DATASET
# ==========================================================

st.subheader("📁 Current Test Dataset")

incoming_images = [
    file
    for file in INCOMING.iterdir()
    if file.suffix.lower()
    in {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }
]

st.write(
    f"Images currently available: **{len(incoming_images)}**"
)

if incoming_images:

    for image in incoming_images:

        st.write(
            "•",
            image.name
        )


# ==========================================================
# CLEAR TEST DATA
# ==========================================================

if st.button(
    "🗑️ Clear Uploaded Test Images",
    use_container_width=True
):

    for image in incoming_images:

        try:
            image.unlink()
        except Exception:
            pass

    st.session_state.results = None

    st.success(
        "Test images cleared."
    )

    st.rerun()


st.divider()


# ==========================================================
# MODULE FUNCTIONS
# ==========================================================

def run_m1():

    try:

        duplicates = detect_duplicates(
            INCOMING
        )

        return {
            "status":
                "REVIEW"
                if len(duplicates) > 0
                else "PASS",

            "duplicate_count":
                len(duplicates),

            "evidence":
                duplicates[:10]
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "duplicate_count": 0,
            "evidence": [],
            "reason": str(e)
        }


def run_m2():

    if not MODEL.exists():

        return {
            "status": "UNAVAILABLE",
            "reason": "model.pt not found."
        }

    if not REGISTRY.exists():

        return {
            "status": "UNAVAILABLE",
            "reason":
                "model_registry.json not found."
        }

    try:

        with open(
            REGISTRY,
            "r"
        ) as file:

            registry = json.load(file)

        registered_hash = (
            registry["sha256"]
        )

        current_hash = (
            calculate_model_hash(MODEL)
        )

        verified = (
            registered_hash ==
            current_hash
        )

        return {

            "status":
                "PASS"
                if verified
                else "FAIL",

            "registered_sha256":
                registered_hash,

            "current_sha256":
                current_hash
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "reason": str(e)
        }


def run_m3():

    try:

        verified = verify_ledger()

        return {

            "status":
                "PASS"
                if verified
                else "FAIL",

            "ledger_verified":
                bool(verified)
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "ledger_verified": False,
            "reason": str(e)
        }


def run_m4():

    try:

        reference = analyze_dataset(
            REFERENCE
        )

        incoming = analyze_dataset(
            INCOMING
        )

        if reference is None:

            return {
                "status": "UNAVAILABLE",
                "reason":
                    "Reference dataset unavailable."
            }

        if incoming is None:

            return {
                "status": "UNAVAILABLE",
                "reason":
                    "Incoming dataset unavailable."
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
            brightness_shift
            + width_shift
            + height_shift
        ) / 3

        detected = (
            overall_shift >= 20
        )

        return {

            "status":
                "SHIFT_DETECTED"
                if detected
                else "PASS",

            "overall_shift_percent":
                float(round(overall_shift, 2)),

            "brightness_shift_percent":
                float(round(
                    brightness_shift,
                    2
                )),

            "width_shift_percent":
                float(round(
                    width_shift,
                    2
                )),

            "height_shift_percent":
                float(round(
                    height_shift,
                    2
                ))
        }

    except Exception as e:

        return {
            "status": "ERROR",
            "reason": str(e)
        }


# ==========================================================
# COMPLETE AUDIT
# ==========================================================

def run_complete_audit():

    m1 = run_m1()

    m2 = run_m2()

    m3 = run_m3()

    m4 = run_m4()

    risk = evaluate_risk(

        m1_duplicate_count=
            m1.get(
                "duplicate_count",
                0
            ),

        m2_model_integrity=
            m2.get("status") == "PASS",

        m3_ledger_integrity=
            m3.get("status") == "PASS",

        m4_shift_detected=
            m4.get("status")
            == "SHIFT_DETECTED"
    )

    return (
        m1,
        m2,
        m3,
        m4,
        risk
    )


# ==========================================================
# RUN AUDIT
# ==========================================================

st.subheader(
    "🔍 Run Integrity Assessment"
)

if st.button(
    "🚀 RUN COMPLETE AUDIT",
    type="primary",
    use_container_width=True
):

    if len(incoming_images) == 0:

        st.warning(
            "Please upload at least one image "
            "before running the audit."
        )

    else:

        with st.spinner(
            "Running M1 → M2 → M3 → M4 → Risk Engine..."
        ):

            st.session_state.results = (
                run_complete_audit()
            )

        st.success(
            "Complete audit finished successfully."
        )


# ==========================================================
# RESULTS
# ==========================================================

if st.session_state.results:

    m1, m2, m3, m4, risk = (
        st.session_state.results
    )

    st.divider()

    st.subheader(
        "📊 Integrity Assessment"
    )

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "M1 Dataset",
            m1["status"]
        )


    with c2:

        st.metric(
            "M2 Model",
            m2["status"]
        )


    with c3:

        st.metric(
            "M3 Provenance",
            m3["status"]
        )


    with c4:

        st.metric(
            "M4 Shift",
            m4["status"]
        )


    st.divider()

    st.subheader(
        "⚠️ Overall Risk Assessment"
    )

    r1, r2 = st.columns(2)

    with r1:

        st.metric(
            "Risk Score",
            risk["risk_score"]
        )

    with r2:

        st.metric(
            "Disposition",
            risk["disposition"]
        )


    # ======================================================
    # M1
    # ======================================================

    st.divider()

    st.subheader(
        "M1 — Dataset Integrity"
    )

    st.write(
        "Near-duplicates:",
        m1.get(
            "duplicate_count",
            0
        )
    )

    if m1.get("evidence"):

        st.warning(
            "Near-duplicate evidence detected."
        )

        st.json(
            m1["evidence"]
        )

    else:

        st.success(
            "No near-duplicates detected."
        )


    # ======================================================
    # M2
    # ======================================================

    st.subheader(
        "M2 — Model Integrity"
    )

    if m2["status"] == "PASS":

        st.success(
            "✅ Model integrity verified."
        )

    elif m2["status"] == "FAIL":

        st.error(
            "🔴 Model integrity failed."
        )

    else:

        st.warning(
            m2.get(
                "reason",
                "Model verification unavailable."
            )
        )


    # ======================================================
    # M3
    # ======================================================

    st.subheader(
        "M3 — Provenance"
    )

    if m3["status"] == "PASS":

        st.success(
            "✅ Audit ledger verified."
        )

    elif m3["status"] == "FAIL":

        st.error(
            "🔴 Audit ledger integrity failed."
        )

    else:

        st.warning(
            m3.get(
                "reason",
                "Ledger verification unavailable."
            )
        )


    # ======================================================
    # M4
    # ======================================================

    st.subheader(
        "M4 — Shift Analysis"
    )

    if "overall_shift_percent" in m4:

        a, b, c, d = st.columns(4)

        with a:

            st.metric(
                "Overall Shift",
                f'{m4["overall_shift_percent"]}%'
            )

        with b:

            st.metric(
                "Brightness",
                f'{m4["brightness_shift_percent"]}%'
            )

        with c:

            st.metric(
                "Width",
                f'{m4["width_shift_percent"]}%'
            )

        with d:

            st.metric(
                "Height",
                f'{m4["height_shift_percent"]}%'
            )

        if m4["status"] == "PASS":

            st.success(
                "No significant shift detected."
            )

        else:

            st.warning(
                "Distribution shift detected."
            )


    # ======================================================
    # RISK FINDINGS
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Risk Findings"
    )

    for finding in risk["findings"]:

        severity = finding["severity"]

        if severity == "LOW":

            st.success(
                f'🟢 {finding["module"]} — LOW'
            )

        elif severity == "MEDIUM":

            st.warning(
                f'🟠 {finding["module"]} — MEDIUM'
            )

        else:

            st.error(
                f'🔴 {finding["module"]} — HIGH'
            )

        st.write(
            "**Finding:**",
            finding["finding"]
        )

        st.write(
            "**Recommendation:**",
            finding["recommendation"]
        )


# ==========================================================
# M5 REPORT
# ==========================================================

st.divider()

st.subheader(
    "📄 M5 — Assurance Report"
)

if st.button(
    "Generate M5 Report",
    use_container_width=True
):

    with st.spinner(
        "Generating assurance report..."
    ):

        report, json_path = (
            generate_report()
        )

        html_path = (
            generate_html(report)
        )

    st.success(
        "M5 report generated."
    )

    st.write(
        "Disposition:",
        report["risk_assessment"]["disposition"]
    )


# ==========================================================
# DOWNLOAD REPORTS
# ==========================================================

JSON_PATH = (
    REPORTS /
    "satyanetra_report.json"
)

HTML_PATH = (
    REPORTS /
    "satyanetra_report.html"
)


if JSON_PATH.exists():

    with open(
        JSON_PATH,
        "rb"
    ) as file:

        st.download_button(
            "📥 Download JSON Report",
            file,
            file_name="satyanetra_report.json",
            mime="application/json",
            use_container_width=True
        )


if HTML_PATH.exists():

    with open(
        HTML_PATH,
        "rb"
    ) as file:

        st.download_button(
            "🌐 Download HTML Report",
            file,
            file_name="satyanetra_report.html",
            mime="text/html",
            use_container_width=True
        )


# ==========================================================
# COVERAGE
# ==========================================================

st.divider()

st.subheader(
    "🛡️ Coverage & Limitations"
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("### ✅ Supported")

    for item in [

        "Near-duplicate image detection",

        "SHA-256 model integrity verification",

        "Tamper-evident audit ledger verification",

        "Basic image-statistics shift detection",

        "Evidence-based risk assessment"

    ]:

        st.write(
            "•",
            item
        )


with col2:

    st.markdown("### ⚠️ Current Limitations")

    for item in [

        "Adaptive detector-aware attackers",

        "Very-low-rate clean-label poisoning",

        "Conclusive black-box backdoor absence",

        "Hardware or firmware compromise",

        "Signing-key compromise",

        "Advanced trigger reconstruction"

    ]:

        st.write(
            "•",
            item
        )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "SatyaNetra | PS 26228 | "
    "Offline Computer Vision Integrity Assurance"
)