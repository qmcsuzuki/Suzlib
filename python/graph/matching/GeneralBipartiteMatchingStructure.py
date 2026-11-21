# competitive-verifier: TITLE 二部マッチングの構造（自動二部彩色）

"""
GeneralBipartiteMatching に対する構造解析。内部の左右型マッチングに対する
BipartiteMatchingStructure の結果を、入力時の頂点番号に付け替える。
"""

# ALWAYS / SOMETIMES は戻り値の比較用にここからも import できるようにする。
from python.graph.matching.BipartiteMatchingStructure import ALWAYS, NEVER, SOMETIMES, DulmageMendelsohn, matching_structure
from python.graph.matching.GeneralBipartiteMatching import GeneralBipartiteMatching


def general_matching_structure(
    matching: GeneralBipartiteMatching,
) -> tuple[list[int], list[int]]:
    """
    各辺・頂点が最大マッチングで
    NEVER / SOMETIMES / ALWAYS のどれかを返す。

    戻り値は (edge_status, vertex_status)。
    頂点番号・辺番号は入力時の番号をそのまま使う。
    """
    edge_status, left_status, right_status = matching_structure(matching.lr_matching())

    vertex_status = [NEVER] * matching.n
    for left, v in enumerate(matching.fromL):
        vertex_status[v] = left_status[left]
    for right, v in enumerate(matching.fromR):
        vertex_status[v] = right_status[right]

    return edge_status, vertex_status


class GeneralDulmageMendelsohn:
    """
    GeneralBipartiteMatching に対する Dulmage--Mendelsohn 分解。

    頂点番号は入力時の番号をそのまま使う。color[v] == 0 の頂点を左、
    color[v] == 1 の頂点を右として内部の DulmageMendelsohn を構成する。

    API:
      DM.groups      : [V0, V1, ..., Vinf] のリスト
      DM.groupnum[v] : 元の頂点 v が属する group の番号
      DM.color[v]    : 自動二部彩色。0 が左、1 が右
      DM.dag         : groups を縮約した残余 DAG
      DM.V0, DM.Vinf : 両端の固定領域
      DM.blocks      : [V1, V2, ...] のリスト
    """

    def __init__(self, matching: GeneralBipartiteMatching) -> None:
        """自動二部彩色し、元の頂点番号で DM 分解を返す。"""
        dm = DulmageMendelsohn(matching.lr_matching())
        original = matching.fromL + matching.fromR

        self.n = matching.n
        self.color = matching.color.copy()
        self.groups = [
            [original[v] for v in group]
            for group in dm.groups
        ]
        self.V0 = [original[v] for v in dm.V0]
        self.blocks = [
            [original[v] for v in block]
            for block in dm.blocks
        ]
        self.Vinf = [original[v] for v in dm.Vinf]
        self.groupnum = [-1] * self.n
        for v in range(self.n):
            self.groupnum[original[v]] = dm.groupnum[v]
        self.dag = [adj.copy() for adj in dm.dag]
