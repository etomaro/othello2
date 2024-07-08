"""
出力系
"""
import tkinter as tk
from env_v2.env import Env2, GameInfo, PlayerId, GameState


# ボードを描画する関数
def draw_board(black_board: int, white_board: int, player_id: int = None, actionables: int = None):
    """
    Tinkerを用いてゲーム状態をGUIとして出力する
    """
    # ボードのサイズとマスのサイズ
    BOARD_SIZE = 8
    SQUARE_SIZE = 50
    
    # ウィンドウの作成
    root = tk.Tk()
    title = "Othello Board"
    if player_id is not None:
        action_player = "BLACK" if player_id == PlayerId.BLACK_PLAYER_ID.value else "WHITE"
        title = f"ACTION: {action_player}"
    root.title(title)
    
    # Canvasの作成
    canvas = tk.Canvas(root, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
    canvas.pack()
    canvas.delete("all")  # キャンバスをクリア

    # マス目を描画
    for i in range(BOARD_SIZE):  # 行
        for j in range(BOARD_SIZE):  # 列
            x1 = j * SQUARE_SIZE  # 左のx座標
            y1 = i * SQUARE_SIZE  # 上のy座標
            x2 = x1 + SQUARE_SIZE  # 右のx座標
            y2 = y1 + SQUARE_SIZE  # 下のy座標
            canvas.create_rectangle(x1, y1, x2, y2, outline="black")
            
            index = 0x8000000000000000
            board_index = j + i*8
            is_black, is_white, is_actionable = False, False, False
            if (black_board&(index>>board_index)) != 0:
                is_black = True
            if (white_board&(index>>board_index) != 0):
                is_white = True
            if (actionables&(index>>board_index) != 0):
                is_actionable = True

            # 石を描画
            if is_black:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
            if is_white:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")
            if is_actionable:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, outline="red")
    # ウィンドウのループ処理
    root.mainloop()


action_player = PlayerId.BLACK_PLAYER_ID.value
black_board = 0x0000000810000000
white_board = 0x0000001008000000
actionables = Env2.get_actionables(black_board, white_board, action_player)
# 初期描画
draw_board(black_board, white_board, action_player, actionables)
