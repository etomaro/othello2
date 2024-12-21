"""
世代ごとの推定最大状態数を求める

"""
from itertools import combinations

from env_v2.common.symmetory import normalization

def calc(generation: int) -> int:
    """
    世代ごとの推定最大状態数を求める
    ※ 一旦可能な状態を保存しない。数だけ出力

    [ロジック]
    1. 世代による黒と白石の合計数を求める
    2. 黒と白石のパターンをすべて洗い出す
       ただし、黒と白色の数が同数ではない場合は数を入れ替えたものは必ず同じ推定状態数になるため計算しない
    3. 黒と白石の数が確定している状態でその推定状態数を算出
    4. 3で求めた個数をすべて合計することで指定された世代の推定状態数を求める
      
    args:
      generation: 世代(1-60)
    returns:
      estimated_state_num
    """
    # 1. 世代による黒と白石の合計数を求める
    stone_num = 4 + generation
    # 2. 黒と白石のパターンをすべて洗い出す
    stone_pattern_not_same_num = []  # 黒と白の数が同数ではない
    stone_pattern_same_num = []  # 黒と白の数が同数
    for black_stone_num in range(stone_num+1):
        # 合計石数の半数を超えた場合ループ終了
        if black_stone_num > (stone_num/2):
            break
    
        white_stone_num = stone_num - black_stone_num
        if black_stone_num != white_stone_num:
            stone_pattern_not_same_num.append((black_stone_num, white_stone_num))
        else:
            stone_pattern_same_num.append((black_stone_num, white_stone_num))
        
    print(f"stone_pattern_not_same_num: {stone_pattern_not_same_num}")
    print(f"stone_pattern_same_num: {stone_pattern_same_num}")

    # ---3. 黒と白石の数が確定している状態でその推定状態数を算出---
    estimated_state_num = 0

    # 黒石と白石の同数ではないパターンのループ
    for stones_num in stone_pattern_not_same_num:
        black_stone_num, white_stone_num = stones_num
        # 黒と白の数を入れ替えて計算せずに2倍する
        estimated_state_num += _calc_state_num_by_white_black_num(black_stone_num, white_stone_num) * 2
    
    # 黒石と白石の同数のパターン
    for stone_num in stone_pattern_same_num:
        black_stone_num, white_stone_num = stones_num 
        estimated_state_num += _calc_state_num_by_white_black_num(black_stone_num, white_stone_num)
    
    # 4. 3で求めた個数をすべて合計することで指定された世代の推定状態数を求める
    return estimated_state_num


def _calc_state_num_by_white_black_num(black_stone_num: int, white_stone_num: int) -> int:
    """
    黒石と白石の数が確定している状態での推定最大状態数を求める

    [計算上省くことができるパターン]
      1. 石の数
      2. 黒と白に同じマスに存在する場合
      3. 中央の4マスが空白
      4. 孤立石
         特性上連続性があるため各8方向に石が1つもない状態は省くことができる
      5. 対称性により同じ状態とみなせる盤面
         ※ 対称性により省ける場合、必ず黒石と白石のそれぞれの数が同じになる
    [省くことができないパターン]
      1. 黒と白石の数が同数ではい場合入れ替えることで推定状態数を2倍と計算しているが
         ゲーム進行上ありえない盤面を追加することになる

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
    black_boards = []
    for combo in combinations(range(64), black_stone_num):
        # comboは1にするビット位置のタプル
        # 64ビット整数の値を構築
        value = 0
        for bit in combo:
            value |= (1<<bit)
        black_boards.append(value)

    white_boards = []
    for combo in combinations(range(64), white_stone_num):
        # comboは1にするビット位置のタプル
        # 64ビット整数の値を構築
        value = 0
        for bit in combo:
            value |= (1<<bit)
        white_boards.append(value)
    
    """
    状態の持ち方で一番メモリ節約になる方法を検討
    1. str(black_board)_str(white_board): 74bytes
       ※ 先頭の0xを排除
    2. tuple: 40bytes
       (black_board, white_board)
    3. hash化: 105bytes
       hashlib.sha256(state.encode()).hexdigest(): 必ず105bytesになる
    4. black_board(int) + white_board(int)
       ※ 数値として持つ方法。単純な合計値だと同じ状態でなくても合計値が同じ場合になるため除外
    """
    # 黒と白のパターンごとに除外できる盤面を排除する
    estimated_boards = set()
    for black_board in black_boards:
        for white_board in white_boards:
            # 1. 石の数 はすでに除外済み
            # 2. 黒と白に同じマスに存在する場合
            if (black_board & white_board) != 0:
                continue
            # 3. 中央の4マスが空白
            center_4_stone_mask = 0x0000001818000000
            if (center_4_stone_mask & (black_board | white_board)) != center_4_stone_mask:
                continue

            # 4. 孤立石: 特性上連続性があるため各8方向に石が1つもない状態は省くことができる
            board = black_board | white_board
            if _judge_alone_stone(board):
                continue
            
            # 5. 対称性により同じ状態とみなせる盤面をsetの重複で排除する
            normalization_board = normalization(black_board, white_board)
            estimated_boards.add(normalization_board)
    
    return len(estimated_boards)

def _judge_alone_stone(board: int) -> bool:
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



    