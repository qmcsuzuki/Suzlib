# Suzlib

競技プログラミング用の個人 Python ライブラリ。PyPy3 での利用を想定する。

## 使用方法

`python/` にアルゴリズム本体、各 `test/` に competitive-verifier 用の検証を置く。
各ファイルの docstring に引数、返り値、適用条件を記載する。添字と区間の規約は
ファイルごとに確認する。特に `FenwickTreeDinamic` は閉区間、通常の Fenwick 木や
セグメント木は半開区間を使う。順序付き多重集合の `kth_value` は 1-indexed。

貼り付け利用とリポジトリからの import の両方を想定している。
内部の `from python... import ...` は、提出時には依存元も含めて展開する。
import で使う場合はリポジトリのルートを `PYTHONPATH` に追加する。

一部のファイルは事前設定を必要とする。

| ファイル・系統 | 呼び出し側で必要な設定 |
| --- | --- |
| `combinatorics/coeff_inv_three_terms.py` | `MOD`、`choose(n,k)`、必要な長さの累乗表 |
| `combinatorics/count_bounded_ordered_division.py` | 実行前に `SIZE`、`MOD`、`choose(n,k)` を用意する貼り付け用コード |
| `polynomial/` | 各モジュールの `MOD`。`LinearRecurrence` は依存する `simple_brute_polynomial` にも同じ値を設定 |
| `other_convolution/FastWalshTransform.py`、`DivisorZetaMobius_allN.py` | 各モジュールの `MOD` |
| `matrix/DeterminantMatrixLinearExpression.py`、`FlattenMatrixFactory.make_MODint_matrix` | 各モジュールの `MOD` |
| `math/number_theory/Garner.py` | モジュールの `MOD` |
| `graph/minimum_distance/BellmanFord.py` | モジュールの `INF` |
| `graph/tree/TreeBasic.input_tree` | モジュールの `readline` |
| `graph/grid/LargeGridUF.get_blockid` | 戻り値をモジュールの `blockpos` に設定 |
| `graph/tree/DFStraverse.py` | `n`、隣接リスト `g` を用意する貼り付け用テンプレート |
| `data_structure/Dim2/Accumulate2dim(matrix_form).py` | 下半分に標準入力を読む使用例を含む。import 用には `data_structure_2D/Accumulate2dim.py` を使う |

演算を一般化したクラスでは、結合則、可換性、単位元、作用の合成順を確認する。
整数に符号化する実装にはビット幅の制約がある。`INF` に有限の整数を使う実装では、
有限の値がその番兵と衝突しないようにする。

## 検証

リポジトリのルートで、外部ジャッジに接続しない単独実行テストを実行する。

```sh
python3 scripts/run_standalone.py
```

PyPy3 があれば自動的に利用し、なければ起動した Python を使う。
実行環境を指定する場合は `--python pypy3` または `--python python3` を渡す。
`STANDALONE` のメタデータが付いたファイルだけを対象とする。
`PROBLEM` を持つジャッジ依存の検証を実行したことにはならない。

GitHub Actions は `config.toml` の `pypy3 {path}` に従い competitive-verifier を実行する。
公開 API を変更する際は対応する検証も確認する。
ドキュメントの Quick reference は `scripts/add_quick_reference.py` が docstring から生成する。
クラスの説明とコンストラクタの説明の両方を表示する。
