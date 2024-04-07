from typing import Optional, Union

from env_v2.env import PlayerId, GameInfo, Env2, GameState

class HuristicEvaluate:
    # オセロの標準的なヒューリスティック評価関数
    EVALUATE_NAME = "HuristicEvaluate"

    @staticmethod
    def evaluate(black_board, white_board, base_player_id):
        """
        葉ノードの評価値を計算(末端ノード)
        
        100  -25   10    5    5   10  -25  100
        -25  -25    2    2    2    2  -25  -25
        10    2     5    1    1    5    2   10
        5     2     1    2    2    1    2    5
        5     2     1    2    2    1    2    5
        10    2     5    1    1    5    2   10
        -25  -25    2    2    2    2  -25  -25
        100  -25   10    5    5   10  -25  100
        """
        
        EVALUATE_MASK_NOT25 = 0x42c300000000c342
        EVALUATE_MASK_1 = 0x0000182424180000
        EVALUATE_MASK_2 = 0x003c425a5a423c00
        EVALUATE_MASK_5 = 0x1800248181240018
        EVALUATE_MASK_10 = 0x2400810000810024
        EVALUATE_MASK_100 = 0x8100000000000081

        black_result, white_result = 0, 0
        
        black_result += bin(EVALUATE_MASK_NOT25 & black_board).count("1") * -25
        white_result += bin(EVALUATE_MASK_NOT25 & white_board).count("1") * -25

        black_result += bin(EVALUATE_MASK_1 & black_board).count("1") * 1
        white_result += bin(EVALUATE_MASK_1 & white_board).count("1") * 1

        black_result += bin(EVALUATE_MASK_2 & black_board).count("1") * 2
        white_result += bin(EVALUATE_MASK_2 & white_board).count("1") * 2

        black_result += bin(EVALUATE_MASK_5 & black_board).count("1") * 5
        white_result += bin(EVALUATE_MASK_5 & white_board).count("1") * 5

        black_result += bin(EVALUATE_MASK_10 & black_board).count("1") * 10
        white_result += bin(EVALUATE_MASK_10 & white_board).count("1") * 10

        black_result += bin(EVALUATE_MASK_100 & black_board).count("1") * 100
        white_result += bin(EVALUATE_MASK_100 & white_board).count("1") * 100
        
        # 評価値を計算
        if base_player_id == PlayerId.BLACK_PLAYER_ID.value:
            result = black_result - white_result
        else:
            result = white_result - black_result

        return result 

class SimpleEvaluateV2:
    EVALUATE_NAME = "SIMPLE_EVALUATE_V2"

    @staticmethod
    def evaluate(black_board, white_board, base_player_id):
        """
        葉ノードの評価値を計算(末端ノード)
        
        ※ 問題点

        ゲームが終了した場合+10000 or -10000を返す
        評価方法
            + 自分の角の数 * 100
            + 相手の角の数 * -100
            + 自分の端の数 * 10
            + 相手の端の数 * -10
            + 自分の石の数 * 1
            + 相手の石の数 * -1
            + b2,b7,g2,g7のどれかに自分の石がある数 * -100
            + b2,b7,g2,g7のどれかに相手の石がある数 * +100
        """
        black_count = bin(black_board).count("1")
        white_count = bin(white_board).count("1")
        black_corner_count = 0
        white_corner_count = 0
        black_edge_count = 0
        white_edge_count = 0
        result = 0

        # 角の数を計算
        mask_corner = 0x8100000000000081
        black_corner_count = bin(black_board & mask_corner).count("1")
        white_corner_count = bin(white_board & mask_corner).count("1")
        
        # 端の数を計算
        mask_edge = 0x7e8181818181817e
        black_edge_count = bin(black_board & mask_edge).count("1")
        white_edge_count = bin(white_board & mask_edge).count("1")
        
        # b2,b7,g2,g7の数を計算
        mask_edge_leak = 0x0042000000004200
        black_edge_leak_count = bin(black_board & mask_edge_leak).count("1")
        white_edge_leak_count = bin(white_board & mask_edge_leak).count("1")

        # 評価値を計算
        if base_player_id == PlayerId.BLACK_PLAYER_ID.value:
            result += black_count * 1
            result += white_count * -1
            result += black_corner_count * 100
            result += white_corner_count * -100
            result += black_edge_count * 10
            result += white_edge_count * -10
            result += black_edge_leak_count * -100
            result += white_edge_leak_count * 100
        else:
            result += black_count * -1
            result += white_count * 1
            result += black_corner_count * -100
            result += white_corner_count * 100
            result += black_edge_count * -10
            result += white_edge_count * 10
            result += black_edge_leak_count * 100
            result += white_edge_leak_count * -100

        return result 

class SimpleEvaluate:
    EVALUATE_NAME = "SIMPLE_EVALUATE"

    @staticmethod
    def evaluate(black_board, white_board, base_player_id):
        """
        葉ノードの評価値を計算(末端ノード)
        
        ※ 問題点
            ・[先行(黒)]Minimax(5) vs [後攻(白)]Minimax(6)で先攻が勝った
            おそらく最初にB2などの石を取ろうとするので角を取られやすい

        ゲームが終了した場合+10000 or -10000を返す
        評価方法
            + 自分の角の数 * 100
            + 相手の角の数 * -100
            + 自分の端の数 * 10
            + 相手の端の数 * -10
            + 自分の石の数 * 1
            + 相手の石の数 * -1
        """
        black_count = bin(black_board).count("1")
        white_count = bin(white_board).count("1")
        black_corner_count = 0
        white_corner_count = 0
        black_edge_count = 0
        white_edge_count = 0
        result = 0

        # 角の数を計算
        mask_corner = 0x8100000000000081
        black_corner_count = bin(black_board & mask_corner).count("1")
        white_corner_count = bin(white_board & mask_corner).count("1")
        
        # 端の数を計算
        mask_edge = 0x7e8181818181817e
        black_edge_count = bin(black_board & mask_edge).count("1")
        white_edge_count = bin(white_board & mask_edge).count("1")

        # 評価値を計算
        if base_player_id == PlayerId.BLACK_PLAYER_ID.value:
            result += black_count * 1
            result += white_count * -1
            result += black_corner_count * 100
            result += white_corner_count * -100
            result += black_edge_count * 10
            result += white_edge_count * -10
        else:
            result += black_count * -1
            result += white_count * 1
            result += black_corner_count * -100
            result += white_corner_count * 100
            result += black_edge_count * -10
            result += white_edge_count * 10

        return result 