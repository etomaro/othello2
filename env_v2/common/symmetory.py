"""
盤面の対称性に関する共通モジュール

対称性パターン
1. そのまま(0度回転)
2. 90度回転
3. 180度回転
4. 270度回転
5. 水平反転
5. 90度回転 + 水平反転
6. 180度回転 + 水平反転(=縦軸反転)
7. 270度回転 + 水平反転
"""

def normalization(black_board: int, white_board) -> tuple[int, int]:
    """
    正規化: 対称性の中から最小の(black_white)のペアを選ぶ
    """
    return min(_transformations(black_board, white_board))

def _reverse(board: int) -> int:
    """
    反転する(最下位ビットを最上位ビット入れ替え、下位2ビットを上位2ビットと入れ替え、、、)

    ※ 高速化のため処理に可読性がない
    処理の参考資料は「reverse.xlsx」に記載
    """
    board = ((board & 0x5555555555555555) << 1) | ((board >> 1) & 0x5555555555555555)  # 1,2と3,4と5,6と7,8列目を入れ替え
    board = ((board & 0x3333333333333333) << 2) | ((board >> 2) & 0x3333333333333333)  # 1,2と3,4列、5,6と7,8列目を入れ替え
    board = ((board & 0x0f0f0f0f0f0f0f0f) << 4) | ((board >> 4) & 0x0f0f0f0f0f0f0f0f)  # 1,2,3,4と5,6,7,8列目を入れ替え
    board = ((board & 0x00ff00ff00ff00ff) << 8) | ((board >> 8) & 0x00ff00ff00ff00ff)  # 1と2、3と4、5と6、7と8行目を入れ替え
    board = ((board & 0x0000ffff0000ffff) << 16)| ((board >>16) & 0x0000ffff0000ffff)  # 1,2と3,4行、5,6と7,8行目を入れ替え
    board = ((board & 0x00000000ffffffff) << 32)| ((board >>32) & 0x00000000ffffffff)  # 1,2,3,4と5,6,7,8行目を入れ替え

    return board

def _horizontal_flip(board: int) -> int:
    """
    各行8ビットを左右反転する

    8,6,...1行目の順で反転していく
    """
    def reverse_8(row: int) -> int:
        row = ((row & 0xF0) >> 4) | ((row & 0x0F) << 4)
        row = ((row & 0xCC) >> 2) | ((row & 0x33) << 2)
        row = ((row & 0xAA) >> 1) | ((row & 0x55) << 1)
        return row
    
    new_board = 0
    for row_index in range(8):
        row = (board >> (row_index*8)) & 0xFF  # 8行目に反転する行を持ってくる
        rev = reverse_8(row)
        new_board |= (rev << (row_index*8))  # 反転した行を元の行に戻す
    return new_board

def _transpose(board: int) -> int:
    """
    転置を行う(行と列を入れ替え)
    ex)
    1 2 3
    4 5 6
    ↓
    1 4
    2 5
    3 6
    """
    # ステップ1: 7ビットシフトを使った部分反転
    t = (board ^ (board << 7)) & 0x5500550055005500
    board = board ^ t ^ (t >> 7)

    # ステップ2: 14ビットシフト
    t = (board ^ (board << 14)) & 0x3333000033330000
    board = board ^ t ^ (t >> 14)

    # ステップ3: 28ビットシフト
    t = (board ^ (board << 28)) & 0x0f0f0f0f00000000
    board = board ^ t ^ (t >> 28)

    return board

def _rotate90(board: int) -> int:
    """
    90度回転

    1. 転置
    2. 水平反転
    """
    return(_horizontal_flip(_transpose(board)))

def _rotate180(board: int) -> int:
    """
    180度回転

    1. 反転
    """
    return _reverse(board)

def _rotate270(board: int) -> int:
    """
    270度回転
    
    1. 180度回転
    2. 90度回転
    """
    return _rotate90(_rotate180(board))

def _transformations(black_board: int, white_board: int):
    """
    対称性全パターン(8パターン)を取得

    1. そのまま(0度回転)
    2. 90度回転
    3. 180度回転
    4. 270度回転
    5. 水平反転
    6. 90度回転 + 水平反転
    7. 180度回転 + 水平反転(=縦軸反転)
    8. 270度回転 + 水平反転
    """
    # 1. そのまま(0度回転)
    yield (black_board, white_board)
    
    # 2. 90度回転
    black_board_90 = _rotate90(black_board)
    white_board_90 = _rotate90(white_board)
    yield (black_board_90, white_board_90)
    
    # 3. 180度回転
    black_board_180 = _rotate180(black_board)
    white_board_180 = _rotate180(white_board)
    yield (black_board_180, white_board_180)
    
    # 4. 270度回転
    black_board_270 = _rotate270(black_board)
    white_board_270 = _rotate270(white_board)
    yield (black_board_270, white_board_270)
    
    # 5. 水平反転
    black_board_horizontal = _horizontal_flip(black_board)
    white_board_horizontal = _horizontal_flip(white_board)
    yield (black_board_horizontal, white_board_horizontal)
    
    # 6. 90度回転 + 水平反転
    black_board_90_horizontal = _horizontal_flip(black_board_90)
    white_board_90_horizontal = _horizontal_flip(white_board_90)
    yield (black_board_90_horizontal, white_board_90_horizontal)
    
    # 7. 180度回転 + 水平反転(=縦軸反転)
    black_board_180_horizontal = _horizontal_flip(black_board_180)
    white_board_180_horizontal = _horizontal_flip(white_board_180)
    yield (black_board_180_horizontal, white_board_180_horizontal)
    
    # 8. 270度回転 + 水平反転
    black_board_270_horizontal = _horizontal_flip(black_board_270)
    white_board_270_horizontal = _horizontal_flip(white_board_270)
    yield (black_board_270_horizontal, white_board_270_horizontal)
