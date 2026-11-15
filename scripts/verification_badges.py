"""生成済みの検証結果から、一覧と個別ページ用の検証元を集計する。"""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import yaml


def write_verification_badges(doc_root: Path, src_root: Path) -> None:
    """合格したテストの種類と外部ジャッジ名を Jekyll のデータに書き出す。"""
    judges = {"judge.yosupo.jp": "Yosupo", "judge.u-aizu.ac.jp": "AOJ",
              "onlinejudge.u-aizu.ac.jp": "AOJ"}
    tests = {}
    verified_with = {}
    for page in (doc_root / src_root.name).rglob("*.py.md"):
        text = page.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        header = text[4:].split("\n---\n", 1)[0]
        data = yaml.safe_load(header)["data"]
        path = data["path"]
        if not data["isVerificationFile"]:
            verified_with[path] = data["verifiedWith"]
            continue
        if data["verificationStatus"] != "TEST_ACCEPTED":
            continue
        problem = data["attributes"].get("PROBLEM")
        if problem:
            host = urlsplit(problem).hostname
            if host:
                tests[path] = judges.get(host, host)
        else:
            source = src_root / Path(path).relative_to(src_root.name)
            if re.search(r"(?m)^#\s*competitive-verifier:\s*STANDALONE\s*$",
                         source.read_text(encoding="utf-8")):
                tests[path] = "standalone"

    badges = {}
    verified_with.update({test: [test] for test in tests})
    for path, refs in verified_with.items():
        names = sorted({tests[ref] for ref in refs if ref in tests})
        if names:
            label = "S" if "standalone" in names else ""
            if any(name != "standalone" for name in names):
                label += "J"
            badges[path] = {"label": label, "sources": ", ".join(names)}

    target = doc_root / "_data" / "verification_badges.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(badges, ensure_ascii=False), encoding="utf-8")
