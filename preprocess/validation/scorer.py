from config import RULE_WEIGHTS, THRESHOLDS


def compute_score(anomalies):
    total = sum(RULE_WEIGHTS.get(a["rule"], 0) for a in anomalies)
    return min(total, 100)


def compute_status(score):
    if score < THRESHOLDS["CLEAN"]:
        return "CLEAN"
    if score < THRESHOLDS["WARNING"]:
        return "WARNING"
    return "FRAUD"


def build_result(doc_id, anomalies):
    score = compute_score(anomalies)
    status = compute_status(score)
    return {
        "doc_id": doc_id,
        "risk_score": score,
        "status": status,
        "anomalies": anomalies,
    }
