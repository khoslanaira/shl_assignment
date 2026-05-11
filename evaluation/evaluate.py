import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import VALID_URLS, app


def evaluate():
    cases = json.loads((ROOT / "eval_cases.json").read_text(encoding="utf-8"))
    client = TestClient(app)
    rows = []

    for case in cases:
        response = client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": case["query"]}]},
        )
        payload = response.json()
        recs = payload.get("recommendations", [])
        names = [rec["name"] for rec in recs]
        urls = [rec["url"] for rec in recs]
        expected = set(case["expected"])
        hits = expected.intersection(names)

        recall = len(hits) / len(expected) if expected else 1.0
        precision = len(hits) / len(names) if names and expected else 1.0 if not expected else 0.0
        grounded = all(url in VALID_URLS for url in urls)
        reply = payload.get("reply", "").lower()

        behavior_ok = True
        if case["behavior"] == "clarify":
            behavior_ok = "?" in payload.get("reply", "") and not recs
        elif case["behavior"] == "refuse":
            behavior_ok = not recs and "shl" in reply
        elif case["behavior"] == "compare":
            behavior_ok = recall == 1.0 and ("compare" in reply or "comparison" in reply)
        elif case["behavior"] == "recommend":
            behavior_ok = recall > 0 and bool(recs)

        rows.append({
            "id": case["id"],
            "recall": recall,
            "precision": precision,
            "grounded": grounded,
            "behavior_ok": behavior_ok,
        })

    summary = {
        "cases": len(rows),
        "mean_recall": round(sum(row["recall"] for row in rows) / len(rows), 3),
        "mean_precision": round(sum(row["precision"] for row in rows) / len(rows), 3),
        "groundedness": round(sum(row["grounded"] for row in rows) / len(rows), 3),
        "behavior_accuracy": round(sum(row["behavior_ok"] for row in rows) / len(rows), 3),
        "rows": rows,
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    evaluate()
