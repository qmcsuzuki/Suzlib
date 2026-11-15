"""生成済みの検証結果から、一覧と個別ページ用の検証元を集計する。"""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import yaml


def write_verification_badges(doc_root: Path, src_root: Path) -> None:
    """検証元ごとの状態と外部ジャッジ名を Jekyll のデータに書き出す。"""
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
        status = data["verificationStatus"]
        problem = data["attributes"].get("PROBLEM")
        if problem:
            host = urlsplit(problem).hostname
            if host:
                tests[path] = (judges.get(host, host), status)
        else:
            source = src_root / Path(path).relative_to(src_root.name)
            if re.search(r"(?m)^#\s*competitive-verifier:\s*STANDALONE\s*$",
                         source.read_text(encoding="utf-8")):
                tests[path] = ("standalone", status)

    badges = {}
    verified_with.update({test: [test] for test in tests})
    for path, refs in verified_with.items():
        results = [tests[ref] for ref in refs if ref in tests]
        if not results:
            continue
        badge = {"sources": ", ".join(sorted({name for name, _ in results}))}
        for slot in ("judge", "standalone"):
            statuses = {status for name, status in results
                        if (name == "standalone") == (slot == "standalone")}
            if "TEST_WRONG_ANSWER" in statuses:
                badge[slot] = "×"
            elif statuses == {"TEST_ACCEPTED"}:
                badge[slot] = "✓"
            elif statuses:
                badge[slot] = "…"
            else:
                badge[slot] = "–"
        badges[path] = badge

    target = doc_root / "_data" / "verification_badges.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(badges, ensure_ascii=False), encoding="utf-8")
