#!/usr/bin/env python3
"""competitive-verifier 生成ページへ Quick reference を差し込む。"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

SRC_ROOT = Path(os.environ.get("SRC_ROOT", "python"))
DOC_ROOT = Path(os.environ.get("DOC_ROOT", "_jekyll"))
BEGIN = "<!-- BEGIN QUICK REFERENCE -->"
END = "<!-- END QUICK REFERENCE -->"


def first_line(doc: str | None) -> str:
    """docstring の最初の非空行を返す。"""
    if not doc:
        return ""
    for line in doc.strip().splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _expr(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node)


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """関数定義から Quick reference 用の簡潔な signature を作る。"""
    args: list[str] = []
    all_args = node.args.posonlyargs + node.args.args
    defaults = [None] * (len(all_args) - len(node.args.defaults)) + list(node.args.defaults)

    for i, (arg, default) in enumerate(zip(all_args, defaults)):
        if i == 0 and arg.arg in ("self", "cls"):
            continue
        s = arg.arg
        if default is not None:
            s += "=" + _expr(default)
        args.append(s)

    if node.args.vararg:
        args.append("*" + node.args.vararg.arg)
    elif node.args.kwonlyargs:
        args.append("*")

    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        s = arg.arg
        if default is not None:
            s += "=" + _expr(default)
        args.append(s)

    if node.args.kwarg:
        args.append("**" + node.args.kwarg.arg)

    return f"{node.name}({', '.join(args)})"


def parse_python_file(path: Path) -> list[dict]:
    """Python ファイルから公開 class / function / method を抽出する。"""
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as e:
        print(f"skip: syntax error in {path}: {e}")
        return []

    items = []
    module_doc = first_line(ast.get_docstring(tree))

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                items.append(
                    {
                        "kind": "function",
                        "sig": signature(node),
                        "doc": first_line(ast.get_docstring(node)),
                    }
                )
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue

            init = None
            methods = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if child.name == "__init__":
                        init = child
                    elif not child.name.startswith("_"):
                        methods.append(child)

            class_sig = node.name
            if init is not None:
                init_sig = signature(init)
                class_sig = node.name + init_sig[init_sig.find("(") :]

            items.append(
                {
                    "kind": "class",
                    "sig": class_sig,
                    "doc": first_line(ast.get_docstring(node)) or module_doc,
                    "methods": [
                        {
                            "sig": signature(method),
                            "doc": first_line(ast.get_docstring(method)),
                        }
                        for method in methods
                    ],
                }
            )

    return items


def make_quick_reference(items: list[dict]) -> str:
    """抽出結果を Markdown の Quick reference ブロックにする。"""
    if not items:
        return ""

    lines = ["## Quick reference", ""]
    for item in items:
        lines.append(f"- `{item['sig']}`")
        if item["doc"]:
            lines.append(f"  - {item['doc']}")

        if item["kind"] == "class":
            for method in item["methods"]:
                lines.append(f"  - `{method['sig']}`")
                if method["doc"]:
                    lines.append(f"    - {method['doc']}")

    lines.append("")
    return "\n".join(lines)


def doc_page_candidates(src_path: Path) -> list[Path]:
    """competitive-verifier の代表的な出力名から候補を作る。"""
    rel = src_path.relative_to(SRC_ROOT)
    base = DOC_ROOT / SRC_ROOT.name / rel
    candidates = [
        base.with_name(base.name + ".md"),
        base.with_name(base.name + ".html"),
        base.with_suffix(".md"),
        base.with_suffix(".html"),
        base,
    ]
    return candidates


def find_doc_page(src_path: Path) -> Path | None:
    """元 Python ファイルに対応する生成済み個別ページを探す。"""
    for path in doc_page_candidates(src_path):
        if path.exists():
            return path

    rel = src_path.as_posix()
    candidates = sorted(DOC_ROOT.rglob(src_path.name + "*"))
    for path in candidates:
        s = path.as_posix()
        if rel in s or src_path.stem in path.name:
            return path
    return None


def inject_quick_reference(page_path: Path, quick_ref: str) -> None:
    """生成済みページへ Quick reference を挿入または差し替える。"""
    text = page_path.read_text(encoding="utf-8")
    block = f"{BEGIN}\n{quick_ref}{END}\n"
    pattern = re.compile(f"{re.escape(BEGIN)}.*?{re.escape(END)}\n?", re.DOTALL)

    if pattern.search(text):
        text = pattern.sub(block, text)
    elif text.startswith("---"):
        end = text.find("\n---", 3)
        if end == -1:
            text = block + "\n" + text
        else:
            end = text.find("\n", end + 1)
            text = text[: end + 1] + "\n" + block + "\n" + text[end + 1 :]
    else:
        text = block + "\n" + text

    page_path.write_text(text, encoding="utf-8")


def should_skip(src_path: Path) -> bool:
    """verify / test 用ファイルは対象外にする。"""
    return "test" in src_path.parts or ".test" in src_path.name


def main() -> None:
    updated = 0
    for src_path in sorted(SRC_ROOT.rglob("*.py")):
        if should_skip(src_path):
            continue

        quick_ref = make_quick_reference(parse_python_file(src_path))
        if not quick_ref:
            continue

        page_path = find_doc_page(src_path)
        if page_path is None:
            print(f"skip: no doc page for {src_path}")
            continue

        inject_quick_reference(page_path, quick_ref)
        updated += 1
        print(f"updated: {page_path}")

    print(f"quick references updated: {updated}")


if __name__ == "__main__":
    main()
