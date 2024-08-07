
"""
出力系

対称性のボードを出力する
"""
import tkinter as tk
from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.tools.draw_board import draw_board
from env_v2.symmetory.symmetory import (_get_y, _get_x, _get_right_z,_get_left_z,
                                        _get_rotato90, _get_rotato180, _get_rotato270)
from PIL import Image
import os


def draw_board_symmetory(
    canvas, black_board: int, white_board: int, symmetory_map, row_num, 
    actionables: int = None, start_x: int = 0, start_y: int = 0, board_size: int = 8, square_size: int = 50,
    buffer_x: int = 10, buffer_y: int = 10,  is_actionables: bool = False
):
    # 初期描画
    # base
    pos_x, pos_y = start_x, start_y
    draw_board(
        canvas, black_board, white_board, None, start_x=pos_x, start_y=pos_y, square_size=square_size, text="Base",
        text_color="red")
    now_row_num = 1
    for text, funcs in symmetory_map.items():
        sym_black_board, sym_white_board = black_board, white_board
        for func in funcs:
            sym_black_board = func(sym_black_board)
            sym_white_board = func(sym_white_board)
        if now_row_num%row_num==0:
            # 次の行へ
            pos_x = start_x
            pos_y = pos_y + buffer_y + board_size*square_size
        else:
            pos_x = pos_x + buffer_x + board_size*square_size
        draw_board(canvas, sym_black_board, sym_white_board, None, start_x=pos_x, start_y=pos_y, square_size=square_size, text=text)
        
        now_row_num += 1
    
if __name__ == "__main__": 
    # ------------設定値------------
    # ボードのサイズとマスのサイズ
    symmetory_map = {
        "①y軸反転": [_get_y],
        "②x軸反転": [_get_x],
        "③右斜めz軸反転": [_get_right_z],
        "④左斜めz軸反転": [_get_left_z],
        "⑤90度回転": [_get_rotato90],
        "⑥180度回転": [_get_rotato180],
        "⑦270度回転": [_get_rotato270],
        "⑧y->90度": [_get_x, _get_right_z],
        "⑧y->180度": [_get_x, _get_left_z],
        "⑧y->270度": [_get_left_z, _get_rotato270],
    }
        
    board_size = 8
    square_size = 30
    row_num = 4  # 1行当たりのボード数
    start_x = 50
    start_y = 0
    buffer_x = 10
    buffer_y = 50
    black_board = 17626548404224
    white_board = 35254098198528
    action_player = PlayerId.BLACK_PLAYER_ID.value
    actionables = Env2.get_actionables(black_board, white_board, action_player)
    is_actionables = False  # アクション可能を表示するかどうか
    # ------------------------------
    col_num = ((len(symmetory_map) + 1)//row_num) + 1  # 縦のボード数

    # ウィンドウの作成
    root = tk.Tk()
    try:
        out_player = "BLACK" if action_player == PlayerId.BLACK_PLAYER_ID.value else "WHITE"
        title = f"SYMMETORY ACTION: {out_player}"
    except Exception:
        title = "Othello Board"
    root.title(title)
    # Canvasの作成
    canvas_width = board_size*square_size*row_num + start_x*2 + buffer_x*(row_num-1)
    canvas_height = board_size*square_size*col_num + start_y*2 + buffer_y*(col_num-1) + 100  # TODO: +100を適切にする必要がある

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()
    canvas.delete("all")  # キャンバスをクリア

    draw_board_symmetory(
        canvas, black_board, white_board, symmetory_map, row_num, actionables, start_x, start_y,
        board_size, square_size, buffer_x, buffer_y, is_actionables
    )
    
    # ウィンドウのループ処理
    root.mainloop()
