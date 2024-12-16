"""
世代ごとの推定最大状態数を求める

計算上省くことができるパターン
1. 石の数
2. 黒と白に同じマスに存在する場合
3. 中央の4マスが空白
4. 孤立石
   特性上連続性があるため各8方向に石が1つもない状態は省くことができる
5. 対称性により同じ状態とみなせる盤面
   ※ 対称性により省ける場合、必ず黒石と白石のそれぞれの数が同じになる
"""
from itertools import combinations


def calc(generation: int) -> int:
    """
    世代ごとの推定最大状態数を求める
    ※ 一旦可能な状態を保存しない。数だけ出力

    args:
      generation: 世代(1-60)
    returns:
      estimated_state_num
    """
    estimated_state_num = 0

    # 世代による黒と石の合計数(石の合計数)
    stone_num = 4 + generation
    """世代による黒石と白石のパターン([(black_stone_num, white_stone_num), ...])
    ただ、黒と白の数が同数ではない場合入れ替えればいいだけなので(2倍)片方だけを求める
    黒と白の数が同数の場合はそのまま求める
    """
    stone_pattern_not_same_num = []
    stone_pattern_same_num = []
    for black_stone_num in range(stone_num+1):
        if black_stone_num > (stone_num/2):
            break
    
        white_stone_num = stone_num - black_stone_num
        if black_stone_num != white_stone_num:
            stone_pattern_not_same_num.append((black_stone_num, white_stone_num))
        else:
            stone_pattern_same_num.append((black_stone_num, white_stone_num))
        
    print(f"stone_pattern_not_same_num: {stone_pattern_not_same_num}")
    print(f"stone_pattern_same_num: {stone_pattern_same_num}")

    # 黒石と白石の同数ではないパターンのループ
    for stones_num in stone_pattern_not_same_num:
        black_stone_num, white_stone_num = stones_num 
        estimated_state_num += calc_state_num_by_white_black_num(black_stone_num, white_stone_num) * 2
    
    # 黒石と白石の同数のパターン
    for stone_num in stone_pattern_same_num:
        black_stone_num, white_stone_num = stones_num 
        estimated_state_num += calc_state_num_by_white_black_num(black_stone_num, white_stone_num)
    
    return estimated_state_num


def calc_state_num_by_white_black_num(black_stone_num: int, white_stone_num: int) -> int:
    """
    黒石と白石の数が確定している状態での推定最大状態数を求める

    args:
      black_stone_num: 黒石の数
      white_stone_num: 白石の数
    returns:
      estimated_num_by_white_black_num: 石と白石の数が確定している状態での推定最大状態数
    """
    estimated_num_by_white_black_num = 0

    """黒、白それぞれビットボードで可能なパターンを列挙
    64Cstone_num
        ex)stone_num: 4
            64C4=635376

        64Crで(r=0-64)取りうる最大値は10の18乗(100京)
        ※ n_C_r.csvを参照
    """
    # 64ビットのうち、n個のビットを1にするすべてのパターンを生成
    # ビット番号は0～63で下位ビットが0番とする
    black_stones = []
    for combo in combinations(range(64), black_stone_num):
        # comboは1にするビット位置のタプル
        # 64ビット整数の値を構築
        value = 0
        for bit in combo:
            value |= (1<<bit)
        black_stones.append(value)

    white_stones = []
    for combo in combinations(range(64), white_stone_num):
        # comboは1にするビット位置のタプル
        # 64ビット整数の値を構築
        value = 0
        for bit in combo:
            value |= (1<<bit)
        white_stones.append(value)
    
    # 黒と白のパターンごとに除外できる盤面を排除する
    for black_stone in black_stones:
        for white_stone in white_stones:
            # 1. 石の数 はすでに除外済み
            # 2. 黒と白に同じマスに存在する場合
            if (black_stone & white_stone) != 0:
                continue
            # 3. 中央の4マスが空白
            center_4_stone_mask = 0x0000001818000000
            if (center_4_stone_mask & (black_stone | white_stone)) != center_4_stone_mask:
                continue

            # 4. 孤立石: 特性上連続性があるため各8方向に石が1つもない状態は省くことができる
            board = black_stone | white_stone
            if judge_alone_stone(board):
                continue
            
            estimated_num_by_white_black_num += 1  # インクリメント
    
    return estimated_num_by_white_black_num

def judge_alone_stone(board: int) -> bool:
    """
    孤立石かどうかを判定する

    args:
      board: 黒石または白石
    """
    # 境界処理用マスク(両端の列マスク)
    mask_without_a_col = 0x7f7f7f7f7f7f7f7f  # A列(左端)を除くマスク
    mask_without_h_col = 0xfefefefefefefefe  # H列(右端)を除くマスク

    # ボードの最下位ビットの石のから順にチェック
    check_board = board
    while check_board != 0:
        # すべての石をチェック(=0)するまでループ

        """
        A & (-A): 最下位の立っているビットを抽出

        -A: 2の補数: プログラムにおいて「-A=~A+1」
          ex) -ob1010=0b0101 + 0b0001
        A&(-A): 最下位の立っているビットを抽出することができるテクニック
          ex) a = 0b1010 -> 最下位ビットを抽出すると0b0010
              a & (-a)
              =0b1010 & (0b0101+0b0001)
              =0b1010 & 0b0010
              =0b0010
        """
        position = check_board & (-check_board)  # 最下位の立っているビットを抽出(処理対象のマス)
        """
        最下位のビットを取り除く

        positionは最下位の立っているビットのためボードと排他的論理和を取ることで最下位のビットは1と1の関係性のため
        最下位のビットを0に更新できる

        XOR(排他的論理和)
        a b c
        0 0 0
        0 1 1
        1 0 1
        1 1 0
        """
        check_board ^= position  # 最下位のビットを取り除く(最下位のビットを0にしてboardを更新)

        # 各8方向に石があるかチェック
        right = (position >> 1) & board & mask_without_a_col  # 元のボードの処理対象のマスの右のマスに石があるか かつ 処理対象のマスが右端ではないか
        left = (position << 1) & board & mask_without_h_col  # 元のボードの処理対象のマスの左のマスに石があるか かつ 処理対象マスが左端ではないか
        up = (position << 8)  & board  # 一番上のボートの場合元のボードでmaskする際にoutになるので左端、右端のようにmaskする必要がない
        down = (position >> 8) & board 
        left_up = (position << 9) & board & mask_without_h_col  # 元のボードの処理対象のマスの左上に石があるか かつ 処理対象のマスが左端ではないか
        left_down = (position >> 7) & board & mask_without_h_col  # 元のボードの処理対象のマスの左下に石があるか かつ 処理対象のマスが左端ではないか
        right_up = (position << 7) & board & mask_without_a_col  # 元のボードの処理対象のマスの右上に石があるか かつ 処理対象マスが右端ではないか
        right_down = (position >> 9) & board & mask_without_a_col  # 元のボードの処理対象のマスの右下に石があるか かつ 処理対象マスが右端ではないか

        # 各8方向に石が1つもなければ孤立石と判定
        if (right | left | up | down | left_up | left_down | right_up | right_down) == 0:
            return True 

    # すべての石があるマスを調べて1つも孤立石がない場合False
    return False




if __name__ == "__main__":
    print(calc(0))



    