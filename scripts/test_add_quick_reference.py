"""Quick reference の docstring 表示仕様を検証する。"""

import tempfile
import unittest
from pathlib import Path

from add_quick_reference import make_quick_reference, parse_python_file


class QuickReferenceTests(unittest.TestCase):
    def render(self, source: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "example.py"
            path.write_text(source, encoding="utf-8")
            return make_quick_reference(parse_python_file(path))

    def test_separate_module_class_constructor_and_methods(self):
        reference = self.render(
            '"""モジュール説明"""\n'
            'class First:\n'
            '    """クラス説明"""\n'
            '    def __init__(self, value=1):\n'
            '        """初期化説明"""\n'
            '    def run(self):\n'
            '        """操作説明"""\n'
            'class Second:\n'
            '    def __init__(self):\n'
            '        pass\n'
        )
        self.assertEqual(reference.count("モジュール説明"), 1)
        parts = [
            "**モジュール**",
            "モジュール説明",
            "`First(value=1)`",
            "クラス説明",
            "**コンストラクタ**",
            "初期化説明",
            "`run()`",
            "操作説明",
            "`Second()`",
        ]
        locations = [reference.index(part) for part in parts]
        self.assertEqual(locations, sorted(locations))
        self.assertEqual(reference.count("**コンストラクタ**"), 1)

    def test_module_docstring_only(self):
        reference = self.render('"""モジュールのみの説明"""\n')
        self.assertEqual(reference.count("モジュールのみの説明"), 1)
        self.assertIn("## Quick reference", reference)

    def test_function_and_escaped_docstring(self):
        reference = self.render(
            'def function(x):\n'
            '    """条件 x < 2 & x > 0"""\n'
        )
        self.assertIn("`function(x)`", reference)
        self.assertIn("x &lt; 2 &amp; x &gt; 0", reference)
        self.assertNotIn("**モジュール**", reference)


if __name__ == "__main__":
    unittest.main()
