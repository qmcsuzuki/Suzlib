# 上下限付きフロー

`python.graph.flow.BFlow` は辺の上下限と頂点の需給を扱う。
`python.graph.flow.LowerBoundSTFlow` は非負の総流量を持つ s-t フローを扱う。
どちらも既存の `MFGraph` に帰着し、整数容量・整数需給を前提とする。

## BFlow

```python
from python.graph.flow.BFlow import BFlow

g = BFlow(3)
g.add_balance(0, 3)   # 正は供給
g.add_balance(2, -3)  # 負は需要
g.add_edge(0, 1, 1, 4)
g.add_edge(1, 2, 1, 4)
e = g.add_edge(0, 2, 0, 2)
if g.solve():
    assert g.maximize_edge(e) == 2
    maximum_edges = g.edges()
    assert g.minimize_edge(e) == 0
    minimum_edges = g.edges()
```

各頂点で「流出量 − 流入量 = balance」を要求する。
`add_balance(v, amount)` は加算で、初期値は全頂点0。
全頂点0なら上下限付き循環流になる。
`add_edge(src, dst, lower, upper)` は `0 <= lower <= upper` を要求し、辺番号を返す。
自己ループ・多重辺・逆向きの辺も扱える。

`maximize_edge(i)` / `minimize_edge(i)` は辺 i の最適化後の流量そのものを返し、
内部の解も更新する。元の上下限・需給を維持し、前回最適化した辺の値は固定しない。
同じ辺や別の辺を続けて最適化できる。

## LowerBoundSTFlow

```python
from python.graph.flow.LowerBoundSTFlow import LowerBoundSTFlow

g = LowerBoundSTFlow(3, s=0, t=2)
g.add_edge(0, 1, 1, 4)
g.add_edge(1, 2, 1, 3)
g.add_edge(0, 2, 0, 2)
if g.solve():
    assert g.maximize() == 5
    max_edges = g.edges()
    assert g.minimize() == 1
    min_edges = g.edges()
```

総流量は s の流出量 − 流入量とする。標準では0以上を要求する。
`solve(flow_lower=2, flow_upper=5)` なら総流量を2以上5以下に制限する。
`solve(flow_lower=3, flow_upper=3)` なら3に固定する。
`flow_upper=None` は上限指定なし。指定範囲は以後の最適化でも維持する。
負の総流量しか実現できない場合は解なしとなる。

## 共通仕様と計算量

- 構築後、`solve()` は成否によらず1回だけ呼べる。実行可能なら `True`、解なしは `False`。
- 辺・需給の追加は `solve()` 前のみ。
- 最適化・解の取得は `solve()` 成功後のみ。不正な呼び出しは assertion で検出する。
- `get_edge(i)` は `src, dst, lower, upper, flow` を持つ値を返す。
- `edges()` は利用者が追加した辺だけを追加順に返す。補助辺は含まない。
- 流量は下限を足し戻した値。取得済みの辺情報は後の最適化で変化しない。
- `solve()` と各最適化は最大流を高々1回呼ぶ。一般に O(V²(E+V)) 時間、O(V+E) 空間。
- `get_edge()` は O(1)、`edges()` は O(E)。

BFlow の存在判定では下限を需給へ移し、補助始点・終点間の最大流を求める。
成功後は補助辺を順逆とも無効化する。
指定辺 u→v を増やす場合、その辺を順逆とも一時的に無効化し、
v→u の残余最大流を上限まで流してから対象辺に同量を加える。
減らす場合は u→v に流して対象辺から同量を引く。
差分が循環流になるため需給を保ち、任意の実行可能解との差もこの形で表せるため最適値を得る。
自己ループは需給に影響せず、直接上下限に設定する。

LowerBoundSTFlow は t→s の補助辺を BFlow に追加し、その辺を最適化する。
固定の巨大定数は使わず、上限未指定時は s から他頂点へ出る辺の上限の和を利用する。
