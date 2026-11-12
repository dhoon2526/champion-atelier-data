"""Validate and mirror public champion settings without private metadata."""
import json
import urllib.request
from pathlib import Path
SOURCE = "https://champion-atelier-data-dohun.choicelens4.chatgpt.site/champions.json"
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"카엘", "리안", "클라우디아", "티안", "세르카", "우타", "벨", "루나"}
def validate(data):
    assert set(data) <= {"schemaVersion", "title", "readOnly", "updatedAt", "champions"}
    assert data["schemaVersion"] == 1 and data["readOnly"] is True
    assert EXPECTED <= {c["name"] for c in data["champions"]}
    for c in data["champions"]:
        assert set(c) <= {"id", "name", "title", "role", "summary", "combatType", "growth", "records"}
        for r in c["records"]:
            assert set(r) <= {"category", "title", "body", "status", "slot", "part", "tags", "updatedAt"}
            assert r["category"] in {"설정", "관계 서사", "스킬", "대사·연출"}
            assert r["status"] in {"확정", "미정", "보류"}
            assert all(isinstance(r[k], str) for k in ["title", "body", "status"])
    return data
if __name__ == "__main__":
    req = urllib.request.Request(SOURCE, headers={"Accept": "application/json", "User-Agent": "ChampionAtelier-PublicSync"})
    with urllib.request.urlopen(req, timeout=45) as res:
        assert res.status == 200
        assert res.headers.get("Content-Type", "").startswith("application/json")
        raw = res.read(1500001)
    assert len(raw) <= 1500000
    data = validate(json.loads(raw))
    temp = ROOT / "champions.json.tmp"
    temp.write_bytes(raw)
    temp.replace(ROOT / "champions.json")
    print("Validated", len(data["champions"]), "champions /", sum(len(c["records"]) for c in data["champions"]), "records")
