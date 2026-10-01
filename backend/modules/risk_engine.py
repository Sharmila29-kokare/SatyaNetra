# --------------------------------------------------
# SatyaNetra Risk Engine
# --------------------------------------------------


def evaluate_risk(
    m1_duplicate_count=0,
    m2_model_integrity=True,
    m3_ledger_integrity=True,
    m4_shift_detected=False
):

    findings = []
    risk_score = 0

    # M1 - Dataset Integrity
    if m1_duplicate_count > 0:

        findings.append({
            "module": "M1",
            "finding": "Near-duplicate images detected",
            "severity": "MEDIUM",
            "recommendation": "Review dataset"
        })

        risk_score += 25

    else:

        findings.append({
            "module": "M1",
            "finding": "No near-duplicate images detected",
            "severity": "LOW",
            "recommendation": "Accept"
        })


    # M2 - Model Integrity
    if not m2_model_integrity:

        findings.append({
            "module": "M2",
            "finding": "Model hash mismatch detected",
            "severity": "HIGH",
            "recommendation": "Quarantine model"
        })

        risk_score += 50

    else:

        findings.append({
            "module": "M2",
            "finding": "Model integrity verified",
            "severity": "LOW",
            "recommendation": "Accept"
        })


    # M3 - Provenance
    if not m3_ledger_integrity:

        findings.append({
            "module": "M3",
            "finding": "Audit ledger integrity failure",
            "severity": "HIGH",
            "recommendation": "Quarantine evidence"
        })

        risk_score += 50

    else:

        findings.append({
            "module": "M3",
            "finding": "Audit ledger verified",
            "severity": "LOW",
            "recommendation": "Accept"
        })


    # M4 - Distribution Shift
    if m4_shift_detected:

        findings.append({
            "module": "M4",
            "finding": "Distribution shift detected",
            "severity": "MEDIUM",
            "recommendation": "Review incoming data"
        })

        risk_score += 25

    else:

        findings.append({
            "module": "M4",
            "finding": "No significant distribution shift detected",
            "severity": "LOW",
            "recommendation": "Accept"
        })


    # Overall decision
    if risk_score >= 50:

        disposition = "QUARANTINE"

    elif risk_score > 0:

        disposition = "REVIEW"

    else:

        disposition = "ACCEPT"


    return {
        "risk_score": risk_score,
        "disposition": disposition,
        "findings": findings
    }


# --------------------------------------------------
# Print Risk Report
# --------------------------------------------------

def print_report(result):

    print()
    print("==========================================")
    print("       SATYANETRA RISK ASSESSMENT")
    print("==========================================")

    print()
    print("Risk Score:", result["risk_score"])
    print("Disposition:", result["disposition"])

    print()
    print("FINDINGS")
    print("------------------------------------------")

    for finding in result["findings"]:

        print()
        print(
            "[" + finding["module"] + "] "
            + finding["severity"]
        )

        print("Finding:", finding["finding"])
        print("Recommendation:", finding["recommendation"])

    print()
    print("==========================================")


# --------------------------------------------------
# Main Test
# --------------------------------------------------

if __name__ == "__main__":

    result = evaluate_risk(
        m1_duplicate_count=0,
        m2_model_integrity=True,
        m3_ledger_integrity=True,
        m4_shift_detected=False
    )

    print_report(result)