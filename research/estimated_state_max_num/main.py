"""
世代ごとの推定最大状態数を求める

"""
from itertools import combinations
import csv
import time
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import multiprocessing

from env_v2.common.symmetory import normalization
from common.dt_utils import sec_to_str
from common.numerical_utils import get_with_jp_unit



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

# 黒または白石が置かれるマスの選択パターン数(60_C_r.csvを参照.rは石の数-4を指定)
patterns_select_stone_pos_by_r = {
    0: "1",
    1: "60",
    2: "1770",
    3: "3万4220",
    4: "48万7635",
    5: "546万1512",
    6: "5006万3860",
    7: "3億8620万6920",
    8: "25億5862万845",
}
patterns_select_stone_pos_by_r_int = {
    0: 1,
    1: 60,
    2: 1770,
    3: 34220,
    4: 487635,
    5: 5461512,
    6: 50063860,
    7: 386206920,
    8: 255862845,
}


# multiprocessing 用: ワーカーでタプルを受け取り、本来の処理に回すラッパー関数
def worker_wrapper(args):
    return _calc_state_num_by_white_black_num(*args)

def calc(generation: int, chunk_size: int) -> int:
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
    stone_num_pattern = []
    for black_stone_num in range(stone_num+1):
        # 合計石数の半数を超えた場合ループ終了
        if black_stone_num > (stone_num/2):
            break
    
        white_stone_num = stone_num - black_stone_num
        stone_num_pattern.append((black_stone_num, white_stone_num))

    print(f"--------calc start--------")
    print(f"generation: {generation}")
    print(f"石の数: {stone_num}")
    print(f"黒または白石が置かれるマスの選択パターン数: {patterns_select_stone_pos_by_r[stone_num-4]}")
    print(f"stone_num_pattern: {stone_num_pattern}")
    print(f"chunk_size: {chunk_size}")
    print("----------------------------")

    # ---3. 黒と白石の数が確定している状態でその推定状態数を算出---
    estimated_state_num = 0

    # debug用カウンタ
    done_count = 0

    # chunk_size 16で割れる値が適切かも
    # -> CPU100%を維持できてない(なぜか)
    # if patterns_select_stone_pos_by_r_int[stone_num-4]%16 == 0:
    #     chunk_size = patterns_select_stone_pos_by_r_int[stone_num-4]//16
    # else:
    #     chunk_size = (patterns_select_stone_pos_by_r_int[stone_num-4]//16) + 1

    # 黒石と白石の数のパターンでループ
    for stones_num in stone_num_pattern:
        black_stone_num, white_stone_num = stones_num
        stone_num = black_stone_num + white_stone_num

        # -- 並列で処理したい対象(外側ループ)を準備 --
        def get_yield_stone_pos_without_center(chunk_size=1000):
            # stone_pos_without_centerの組み合わせを予め作成。ただしyield
            # ここで yield するだけ。リストは作らない
            # chunkでまとめて処理できるように修正
            # chunk_sizeは黒または白石が置かれるマスの選択パターン数の(メモリが許す限り)16分割できるサイズが適切かも
            chunk = []
            for comb in combinations(NOT_CENTER_POS, stone_num - 4):

                # stone_pos_with_center は「中心4マス(CENTER_POS)」を足した配置可能マス
                stone_pos_with_center = list(comb) + CENTER_POS
                # 1) stone_pos_with_center をビットマスク化
                mask_of_stone_pos_with_center = 0
                for pos in stone_pos_with_center:
                    mask_of_stone_pos_with_center |= (1 << pos)
                
                if _judge_alone_stone(mask_of_stone_pos_with_center):
                    continue


                # 追加する要素は tuple( comb, black_stone_num, ... ) など、元のコードに合わせる
                chunk.append((comb, mask_of_stone_pos_with_center))

                if len(chunk) == chunk_size:
                    # 1万件たまったらまとめて yield
                    yield (
                        chunk,
                        black_stone_num,
                        CENTER_POS,
                        _judge_alone_stone,
                        normalization
                    )
                    chunk = []

            # 余りがあれば最後にまとめて yield
            if chunk:
                yield (
                        chunk,
                        black_stone_num,
                        CENTER_POS,
                        _judge_alone_stone,
                        normalization
                    )

        # -----------------------------------------------------------
        #  マルチプロセスで各 stone_pos_without_center の処理を行う
        # -----------------------------------------------------------
        #   1) Pool を作る
        #   2) apply_async / map などで並列タスクに投げる
        #   3) 各プロセスが局所的に得た set を返し、メインプロセスで union する
        #
        # 並列外でマスの位置を指定する
        # 並列内でマス内の黒と白の位置を指定する
        # -----------------------------------------------------------
        with multiprocessing.Pool() as pool:
            # map の引数にするためのラップ関数を定義
            # stone_pos_without_center を受け取り → 各プロセス内で黒石配置ループを回し
            # 最終的に set(normalized_boards) を返す

            # プロセスプールで並列実行 (map や imap などもOK)
            results = pool.imap(
                worker_wrapper,
                get_yield_stone_pos_without_center(chunk_size=chunk_size),
            )

            # 結果をマージ (各プロセスの set を union)
            estimated_boards = set()
            for s in results:
                estimated_boards |= s  # set の union 代入
        
        if black_stone_num != white_stone_num:
            estimated_state_num += len(estimated_boards) * 2  # 黒と白の数を入れ替えて計算せずに2倍する
        else:
            estimated_state_num += len(estimated_boards)
        del estimated_boards

        done_count += 1
        print(f"{done_count} / {len(stone_num_pattern)} done.")
    
    # 4. 3で求めた個数をすべて合計することで指定された世代の推定状態数を求める
    return estimated_state_num


def _calc_state_num_by_white_black_num(
        stone_pos_without_centers: list[tuple], black_stone_num: int,
        CENTER_POS: list, _judge_alone_stone, normalization
    ) -> set:
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
    local_estimated_boards = set()
    for stone_pos_without_center, mask_of_stone_pos_with_center in stone_pos_without_centers:
        # stone_pos_with_center は「中心4マス(CENTER_POS)」を足した配置可能マス
        stone_pos_with_center = list(stone_pos_without_center) + CENTER_POS

        # # 1) stone_pos_with_center をビットマスク化
        # mask_of_stone_pos_with_center = 0
        # for pos in stone_pos_with_center:
        #     mask_of_stone_pos_with_center |= (1 << pos)

        # 黒石を置く組合せをループ
        for black_stone_pos in combinations(stone_pos_with_center, black_stone_num):
            black_board = 0x0
            for pos in black_stone_pos:
                black_board |= (1 << pos)
            
            # 残りは白石
            white_board = mask_of_stone_pos_with_center & ~black_board  # TODO: ビット反転の処理が正しいか調べる
            
            # 1. 石の数 はすでに除外済み
            # 2. 黒と白に同じマスに存在するはすでに除外済み
            # 3. 中央の4マスが空白はすでに除外済み
            # 4. 孤立石チェックはすでに除外済み

            # 5. 対称性で正規化して重複排除
            norm_board = normalization(black_board, white_board)
            local_estimated_boards.add(norm_board)
    
    return local_estimated_boards

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
    # !!!適切な世代に修正!!!
    chunk_size = 10000  # 1万
    for generation in [4,5]:

        start_time = time.time()
        estimated_num = calc(generation, chunk_size)
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
                ["推定状態数", "推定状態数(単位)", "計測時間", "実行日時", "chunk_size"],
                [str(estimated_num), get_with_jp_unit(estimated_num), calc_time_str, now_str, str(chunk_size)],
            ]
            writer.writerows(rows)
    