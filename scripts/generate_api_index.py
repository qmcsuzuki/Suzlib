#!/usr/bin/env python3
"""競プロライブラリの関数・クラス一覧ページを生成する。"""

from __future__ import annotations

import argparse
import ast
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote


TITLE_PREFIX = "# competitive-verifier: TITLE "
START_MARKER = "<!-- API_INDEX_LINK_START -->"
END_MARKER = "<!-- API_INDEX_LINK_END -->"


@dataclass
class ApiItem:
    kind: str
    name: str
    signature: str
    summary: str = ""
    children: list["ApiItem"] = field(default_factory=list)


@dataclass
class ApiFile:
    path: Path
    title: str = ""
    summary: str = ""
    items: list[ApiItem] = field(default_factory=list)


def is_target(path: Path) -> bool:
    """API 一覧に載せる Python ファイルかどうかを返す。"""
    if path.suffix != ".py":
        return False
    if "test" in path.parts:
        return False
    name = path.name
    return not (name.endswith(".test.py") or name.endswith(".standalone.test.py"))


def verifier_title(text: str) -> str:
    """competitive-verifier の TITLE コメントを読む。"""
    for line in text.splitlines()[:20]:
        if line.startswith(TITLE_PREFIX):
            return line[len(TITLE_PREFIX) :].strip()
    return ""


def first_doc_line(node: ast.AST) -> str:
    """docstring の最初の非空行を返す。"""
    doc = ast.get_docstring(node, clean=True)
    if not doc:
        return ""
    for line in doc.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def expr_to_str(node: ast.AST | None) -> str:
    if node is None:
        return ""
    return ast.unparse(node).replace("\n", " ")


def arg_to_str(arg: ast.arg, default: ast.AST | None = None) -> str:
    s = arg.arg
    if arg.annotation is not None:
        s += ": " + expr_to_str(arg.annotation)
    if default is not None:
        s += "=" + expr_to_str(default)
    return s


def function_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    skip_first: bool = False,
) -> str:
    """関数定義から、一覧表示用の簡潔なシグネチャを作る。"""
    args = node.args
    pos_args = list(args.posonlyargs) + list(args.args)
    if skip_first and pos_args:
        pos_args = pos_args[1:]

    num_pos_args = len(args.posonlyargs) + len(args.args)
    defaults: list[ast.AST | None] = [None] * (num_pos_args - len(args.defaults))
    defaults += list(args.defaults)
    if skip_first and defaults:
        defaults = defaults[1:]

    parts = [arg_to_str(arg, default) for arg, default in zip(pos_args, defaults)]
    if args.posonlyargs and not skip_first:
        parts.insert(len(args.posonlyargs), "/")

    if args.vararg is not None:
        parts.append("*" + arg_to_str(args.vararg))
    elif args.kwonlyargs:
        parts.append("*")

    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(arg_to_str(arg, default))

    if args.kwarg is not None:
        parts.append("**" + arg_to_str(args.kwarg))

    result = f"({', '.join(parts)})"
    if node.returns is not None:
        result += " -> " + expr_to_str(node.returns)
    return result


def has_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> bool:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == name:
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == name:
            return True
    return False


def public_function(node: ast.AST) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    return not node.name.startswith("_")


def public_class(node: ast.AST) -> bool:
    return isinstance(node, ast.ClassDef) and not node.name.startswith("_")


def class_signature(node: ast.ClassDef) -> str:
    """class Foo(...) の ... を __init__ から推定する。"""
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "__init__":
            return function_signature(child, skip_first=True)
    return "()"


def parse_file(path: Path, base: Path) -> ApiFile | None:
    path = path.resolve()
    text = path.read_text(encoding="utf-8")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        rel = path.relative_to(base)
        print(f"skip syntax error: {rel}: {exc}", file=sys.stderr)
        return None

    api_file = ApiFile(
        path=path.relative_to(base),
        title=verifier_title(text),
        summary=first_doc_line(tree),
    )

    for node in tree.body:
        if public_class(node):
            item = ApiItem(
                kind="class",
                name=node.name,
                signature=class_signature(node),
                summary=first_doc_line(node),
            )
            for child in node.body:
                if public_function(child):
                    skip_first = not has_decorator(child, "staticmethod")
                    item.children.append(
                        ApiItem(
                            kind="method",
                            name=child.name,
                            signature=function_signature(child, skip_first=skip_first),
                            summary=first_doc_line(child),
                        )
                    )
            api_file.items.append(item)
        elif public_function(node):
            api_file.items.append(
                ApiItem(
                    kind="function",
                    name=node.name,
                    signature=function_signature(node),
                    summary=first_doc_line(node),
                )
            )

    if api_file.title or api_file.summary or api_file.items:
        return api_file
    return None


def short(text: str) -> str:
    """Markdown の 1 行説明として安全にする。"""
    return text.replace("`", "\\`").strip()


def render_item(item: ApiItem, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    label = "class" if item.kind == "class" else "def" if item.kind == "function" else ""
    name = f"{label} {item.name}" if label else item.name
    line = f"{prefix}- `{name}{item.signature}`"
    if item.summary:
        line += f" — {short(item.summary)}"
    lines = [line]
    for child in item.children:
        lines.extend(render_item(child, indent + 1))
    return lines


def render(files: list[ApiFile], source_root: Path) -> str:
    lines = [
        "---",
        "title: API Index",
        "---",
        "",
        "# API Index",
        "",
        f"`{source_root.as_posix()}/**/*.py` から"
        "関数・クラス・メソッドと docstring の先頭行を自動抽出した一覧です。",
        "",
        f"- 対象ディレクトリ: `{source_root.as_posix()}`",
        f"- 掲載ファイル数: {len(files)}",
        "",
    ]

    for api_file in files:
        path = api_file.path.as_posix()
        href = quote(path, safe="/")
        lines.append(f"## [{path}]({href})")
        lines.append("")
        if api_file.title:
            lines.append(f"**{short(api_file.title)}**")
            lines.append("")
        if api_file.summary:
            lines.append(short(api_file.summary))
            lines.append("")
        if api_file.items:
            for item in api_file.items:
                lines.extend(render_item(item))
            lines.append("")
        else:
            lines.append("- 公開関数・クラスはありません。")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def update_index(index_path: Path, api_path: Path) -> None:
    """トップページに API Index へのリンクを差し込む。"""
    if not index_path.exists():
        print(f"skip index update: {index_path} does not exist")
        return

    text = index_path.read_text(encoding="utf-8")
    block = "\n".join(
        [
            START_MARKER,
            "## API Index",
            "",
            f"- [関数・クラス一覧]({api_path.with_suffix('.html').name})",
            END_MARKER,
        ]
    )

    if START_MARKER in text and END_MARKER in text:
        before = text.split(START_MARKER, 1)[0].rstrip()
        after = text.split(END_MARKER, 1)[1].lstrip("\n")
        text = before + "\n\n" + block + "\n\n" + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"

    index_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=Path("python"), help="解析する Python ライブラリのルート")
    parser.add_argument("--out", type=Path, required=True, help="生成する Markdown ファイル")
    parser.add_argument("--index", type=Path, help="リンクを追記する Jekyll の index.md")
    args = parser.parse_args()

    base = Path.cwd()
    src = args.src
    src_root = src.resolve()
    files = []
    for path in sorted(src_root.rglob("*.py")):
        rel = path.relative_to(base)
        if is_target(rel):
            parsed = parse_file(path, base)
            if parsed is not None:
                files.append(parsed)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(files, src), encoding="utf-8")
    if args.index is not None:
        update_index(args.index, args.out)


if __name__ == "__main__":
    main()
