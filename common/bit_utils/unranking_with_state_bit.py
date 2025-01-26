"""
Gosper's hackではi番目に作成される結果飲みを求めることができない
(やろうとするとi-1番目までをskip roopするしかない)
そのためunrankingという手法でi番目を直接求める。ただし、全列挙の場合gosper's hackより遅い
"""

def get_60_c_r_by_unranking_with_state_bit(r: int):
    """
    Unrankingで指定されたビット長に変換かつ、固定のビットを立てる

    args:
      r: nCrのr, generationの値と同値
    """
    pass