"""
世代ごとの推定最大状態数を求める

"""
from itertools import combinations
import csv
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from env_v2.common.symmetory import normalization


# 中心4マスの位置
CENTER_POS = [27, 28, 35, 36]
NOT_CENTER_POS = [
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 29, 30, 31,
    32, 33, 34, 37, 38, 39,
    40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55,
    56, 57, 58, 59, 60, 61, 62, 63
]



def calc(generation: int) -> int:
    """
    世代ごとの推定最大状態数を求める
    ※ 一旦可能な状態を保存しない。数だけ出力

    [ロジック1]
			1. 世代による黒と白石の合計数を求める
			2. 黒と白石の数のパターンをすべて洗い出す
			ただし、黒と白色の数が同数ではない場合は数を入れ替えたものは必ず同じ推定状態数になるため計算しない
			3. 黒と白石の数が確定している状態でその推定状態数を算出
			4. 3で求めた個数をすべて合計することで指定された世代の推定状態数を求める

			※ 問題点
			2で黒と白別々ですべてのパターンを洗い出して2つの乗数文ループしてします。
			またその中に白と黒で同じマスのパターンなども存在する(ループ内で除外されるが無駄なループ)

    [ロジック2]
      1. 世代による黒と白の合計数を求める
      2. 黒と白石の数のパターンをすべて洗い出す
      3. 中心の4マスを除いた中から(合計数-4)個のマスを選択するパターンをすべて列挙
         -> 白か黒の石が置かれるマス
      4. 黒と白石の数のパターンごとにループ
      5. (3で求めたマス+中心の4マス)の中から黒石の数を元に黒石の置くマスのパターンをすべて列挙
         以下これを元にループ
      6. 黒石の置くマスと(黒石と白石の)置くマスが決まっているので白石の置くマスも自動的に決まる
      
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

    # debug用カウンタ
    done_count = 0

    # 黒石と白石の同数ではないパターンのループ
    for stones_num in stone_pattern_not_same_num:
        black_stone_num, white_stone_num = stones_num
        # 黒と白の数を入れ替えて計算せずに2倍する
        estimated_state_num += _calc_state_num_by_white_black_num(black_stone_num, white_stone_num) * 2

        done_count += 1
        print(f"{done_count} / {len(stone_pattern_not_same_num)+len(stone_pattern_same_num)} done.")
    
    # 黒石と白石の同数のパターン
    for stone_num in stone_pattern_same_num:
        black_stone_num, white_stone_num = stones_num 
        estimated_state_num += _calc_state_num_by_white_black_num(black_stone_num, white_stone_num)

        done_count += 1
        print(f"{done_count} / {len(stone_pattern_not_same_num)+len(stone_pattern_same_num)} done.")
    
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
    
    [状態の持ち方で一番メモリ節約になる方法を検討]
    1. str(black_board)_str(white_board): 74bytes
       ※ 先頭の0xを排除
    2. tuple: 40bytes
       (black_board, white_board)
    3. hash化: 105bytes
       hashlib.sha256(state.encode()).hexdigest(): 必ず105bytesになる
    4. black_board(int) + white_board(int)
       ※ 数値として持つ方法。単純な合計値だと同じ状態でなくても合計値が同じ場合になるため除外

    [黒、白それぞれビットボードで可能なパターンを列挙]
    64Cstone_num
        ex)stone_num: 4
            64C4=635376

        64Crで(r=0-64)取りうる最大値は10の18乗(100京)
        ※ research/estimated_state_num/n_C_r/report.csvを参照
        
        
    args:
      black_stone_num: 黒石の数
      white_stone_num: 白石の数
    returns:
      estimated_num_by_white_black_num: 石と白石の数が確定している状態での推定最大状態数
    """
    stone_num = black_stone_num + white_stone_num
    # 黒と白のパターンごとに除外できる盤面を排除する
    estimated_boards = set()
    # 中心4マスは強制的に使用するので(64-60)の内(石の数-4)のパターンでループ
    for stone_pos_without_center in combinations(NOT_CENTER_POS, stone_num - 4):
        # stone_pos_without_centerは中心を除いた石が置けるマスのインデックスのtuple
        # stone_pos_with_centerは中心を含めた石がおけるマスのインデックスのリスト
        stone_pos_with_center = list(stone_pos_without_center) + CENTER_POS
        
        # 石を置くマスの内黒石の数のパターンでループ
        for black_stone_pos in combinations(stone_pos_with_center, black_stone_num):
            black_board = 0x0
            for pos in black_stone_pos:
                black_board |= (1<<pos)
            
            # black_boardに入らなかった残りのマスが白石
            white_board = 0x0
            for pos in stone_pos_with_center:
                if pos not in black_stone_pos:
                    white_board |= (1<<pos)

            # 1. 石の数 はすでに除外済み
            # 2. 黒と白に同じマスに存在するはすでに除外済み
            # 3. 中央の4マスが空白はすでに除外済み

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

def sec_to_str(calc_time: int) -> str:
    """
    秒を{hour}h{minute}m{seconds}sの形式に変換する
    """
    minute_slot = 60
    hour_slot = 60*60

    calc_time_str = ""
    if (calc_time // hour_slot) >= 1:
        # 1時間以上の場合
        hour = calc_time // hour_slot
        calc_time -= hour * hour_slot
        calc_time_str += f"{hour}h"
    if (calc_time // minute_slot) >= 1:
        # 1分以上の場合
        minute = calc_time // minute_slot 
        calc_time -= minute * minute_slot 
        calc_time_str += f"{minute}m"
    # 秒の追加
    calc_time_str += f"{calc_time}s"

    return calc_time_str


if __name__ == "__main__":
    # !!!適切な世代に修正!!!
    generation = 4

    start_time = time.time()
    estimated_num = calc(generation)
    print(f"世代: {generation}, 推定状態数: {estimated_num}")

    # CSV出力
    now_dt = datetime.now(tz=ZoneInfo("Asia/Tokyo"))
    now_str = f"{now_dt.year}/{now_dt.month}/{now_dt.day} {now_dt.hour}:{now_dt.minute}"

    calc_time_sec = int(time.time() - start_time)
    calc_time_str = sec_to_str(calc_time_sec)

    base_folder = os.path.dirname(__file__)
    file_path = base_folder + "/" + f"{generation}.csv"
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        rows = [
            ["推定状態数", "計測時間", "実行日時"],
            [str(estimated_num), calc_time_str, now_str],
        ]
        writer.writerows(rows)
    