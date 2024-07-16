"""
出力系
"""
import tkinter as tk
from env_v2.env import Env2, GameInfo, PlayerId, GameState


# ボードを描画する関数
def draw_board(
    canvas, black_board: int, white_board: int, actionables: int = None,
    start_x: int = 0, start_y: int = 0, board_size: int = 8, square_size: int = 50,
    text: str = None, text_color: str = "black"
):
    """
    Tinkerを用いてゲーム状態をGUIとして出力する
    """
    # textを描画
    pos_x_text = start_x + (square_size*board_size)//2
    pos_y_text = start_y + 30
    start_y = pos_y_text + 15
    canvas.create_text(pos_x_text, pos_y_text, text=text, font=("HG丸ｺﾞｼｯｸM-PRO",20), fill=text_color)
    
    # マス目を描画
    for i in range(board_size):  # 行
        for j in range(board_size):  # 列
            x1 = start_x + j * square_size  # 左のx座標
            y1 = start_y + i * square_size  # 上のy座標
            x2 = x1 + square_size  # 右のx座標
            y2 = y1 + square_size  # 下のy座標
            canvas.create_rectangle(x1, y1, x2, y2, outline="black")
            
            index = 0x8000000000000000
            board_index = j + i*8
            is_black, is_white, is_actionable = False, False, False
            if (black_board&(index>>board_index)) != 0:
                is_black = True
            if (white_board&(index>>board_index) != 0):
                is_white = True
            if actionables is not None and (actionables&(index>>board_index) != 0):
                is_actionable = True

            # 石を描画
            if is_black:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
            if is_white:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
            if is_actionable:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, outline="red")


if __name__ == "__main__": 
    # ---設定値---
    # ボードのサイズとマスのサイズ
    BOARD_SIZE = 8
    SQUARE_SIZE = 50
    black_board = 0x0000000810000000
    white_board = 0x0000001008000000
    action_player = PlayerId.BLACK_PLAYER_ID.value
    actionables = Env2.get_actionables(black_board, white_board, action_player)

    # ウィンドウの作成
    root = tk.Tk()
    try:
        out_player = "BLACK" if action_player == PlayerId.BLACK_PLAYER_ID.value else "WHITE"
        title = f"ACTION: {out_player}"
    except Exception:
        title = "Othello Board"
    root.title(title)
    # Canvasの作成
    canvas = tk.Canvas(root, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
    canvas.pack()
    canvas.delete("all")  # キャンバスをクリア
    # 初期描画
    draw_board(canvas, black_board, white_board, actionables, start_x=5, start_y=5, square_size=40)
    # ウィンドウのループ処理
    root.mainloop()
