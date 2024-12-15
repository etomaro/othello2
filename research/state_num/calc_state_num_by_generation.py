"""
世代ごとの推定最大状態数を求める

計算上省くことができるパターン
1. 石の数
2. 孤立石
   特性上連続性があるため各8方向に石が1つもない状態は省くことができる
3. 中央の4マスが空白
4. 対称性により同じ状態とみなせる盤面
   ※ 対称性により省ける場合、必ず黒石と白石のそれぞれの数が同じになる
"""


def calc(generation: int) -> int:
    """
    世代ごとの推定最大状態数を求める
    ※ 一旦可能な状態を保存しない。数だけ出力

    args:
      generation: 世代(1-60)
    
    """
    # 世代による黒と石の合計数(石の合計数)
    stone_num = 4 + generation
    # 世代による黒石と白石のパターン([(black_stone_num, white_stone_num), ...])
    stone_pattern = []
    for white_stone_num in range(stone_num+1):
        black_stone_num = stone_num - white_stone_num
        stone_pattern.append((black_stone_num, white_stone_num))

    for stones_num in stone_pattern:
        black_stone_num, white_stone_num = stones_num 

        """黒、白それぞれビットボードで可能なパターンを列挙
        64Cstone_num
          ex)stone_num: 4
             64C4=635376

         64Crで(r=0-64)取りうる最大値は10の18乗(100京)
           ※ n_C_r.csvを参照
        """


    