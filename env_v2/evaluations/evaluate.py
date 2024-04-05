from typing import Optional, Union

from env_v2.env import PlayerId, GameInfo, Env2, GameState




def simple_evaluate(black_board, white_board, base_player_id):
    """
    葉ノードの評価値を計算(末端ノード)

    ゲームが終了した場合+10000 or -10000を返す
    評価方法
        + 自分の角の数 * 100
        + 相手の角の数 * -100
        + 自分の端の数 * 10
        + 相手の端の数 * -10
        + 自分の石の数 * 1
        + 相手の石の数 * -1
        + b2,b7,g2,g7のどれかに自分の石がある場合 * -100
        + b2,b7,g2,g7のどれかに相手の石がある場合 * -100
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