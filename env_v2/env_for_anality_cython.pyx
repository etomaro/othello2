"""
状態数分析用(for anality)にenvを作成

分析の処理の流れ
1. 1世代前の状態(黒石、白石、アクションプレイヤー)を取得する
---下記分散処理---
2. アクション可能ハンドを取得
3. アクション
4. 次の状態を取得
5. 次の状態をファイルに作成
6. 分析結果ファイルを作成
"""

PLAYER_BLACK = 0
PLAYER_WHITE = 1
PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)


def get_initial_board() -> tuple:
    """
    ボードの初期状態を取得する
    
    returns:
      black_board
      white_board
      action_player_id
    """
    return 0x0000000810000000, 0x0000001008000000, PLAYER_BLACK

def get_actionables(black_board: int, white_board: int, player_id: int) -> int:
    """
    アクション可能な座標を算出
    
    処理:
    (自身の駒の左に対して検索する場合)
    自身の駒の左方向に対して連続で相手の駒が続いているものを(続くまでを)1として保持
    連続して続いた先が空白の場合その空白を置ける場所として登録

    1. 左方向に対してい置ける場所を取得
    2. 右方向に対してい置ける場所を取得
    3. 上方向に対してい置ける場所を取得
    4. 下方向に対してい置ける場所を取得
    5. 左上方向に対してい置ける場所を取得
    6. 右上方向に対してい置ける場所を取得
    7. 左下方向に対してい置ける場所を取得
    8. 右下方向に対してい置ける場所を取得
    
    [mask_lr: 0x7e7e7e7e7e7e7e7e]
    01111110
    01111110
    01111110
    01111110
    01111110
    01111110
    01111110
    01111110
    
    [mask_ud: 0x00ffffffffffff00] 
    00000000
    11111111
    11111111
    11111111
    11111111
    11111111
    11111111
    00000000
    
    [mask_lu_ru_ld_rd: 0x007e7e7e7e7e7e00]
    00000000
    01111110
    01111110
    01111110
    01111110
    01111110
    01111110
    00000000

    args:
        black_board:
        white_board:
        player_id: action player id
    returns:
        actionables:
    """
    
    mask_lr = 0x7e7e7e7e7e7e7e7e
    mask_ud = 0x00ffffffffffff00
    mask_lu_ru_ld_rd = 0x007e7e7e7e7e7e00
    
    # 空白の場所
    blank_board = ~(black_board | white_board)
    
    oppo_board = white_board if player_id == PLAYER_BLACK else black_board
    my_board = white_board if player_id != PLAYER_BLACK else black_board
    
    # 相手の位置かつマスク
    oppo_mask_lr = oppo_board & mask_lr
    oppo_mask_ud = oppo_board & mask_ud
    oppo_mask_lu_ru_ld_rd = oppo_board & mask_lu_ru_ld_rd
    
    # 相手の位置かつマスクかつ自分の1つとなり位置(自分のとなりに相手のマスクの場所があるかどうか)
    l_oppo = (my_board << 1) & oppo_mask_lr
    r_oppo = (my_board >> 1) & oppo_mask_lr
    u_oppo = (my_board << 8) & oppo_mask_ud
    d_oppo = (my_board >> 8) & oppo_mask_ud
    lu_oppo = (my_board << 9) & oppo_mask_lu_ru_ld_rd
    ru_oppo = (my_board << 7) & oppo_mask_lu_ru_ld_rd
    ld_oppo = (my_board >> 7) & oppo_mask_lu_ru_ld_rd
    rd_oppo = (my_board >> 9) & oppo_mask_lu_ru_ld_rd

    l_oppo |= (l_oppo << 1) & oppo_mask_lr  # 上記に当てはまる場所(l_oppo)かつ1つ左の白かつ列1-6の場所(oppo_mask_lrに当てはまる箇所)を追加
    r_oppo |= (r_oppo >> 1) & oppo_mask_lr
    u_oppo |= (u_oppo << 8) & oppo_mask_ud
    d_oppo |= (d_oppo >> 8) & oppo_mask_ud
    lu_oppo |= (lu_oppo << 9) & oppo_mask_lu_ru_ld_rd
    ru_oppo |= (ru_oppo << 7) & oppo_mask_lu_ru_ld_rd
    ld_oppo |= (ld_oppo >> 7) & oppo_mask_lu_ru_ld_rd
    rd_oppo |= (rd_oppo >> 9) & oppo_mask_lu_ru_ld_rd

    l_oppo |= (l_oppo << 1) & oppo_mask_lr  # 上記に当てはまる場所(l_oppo)かつ1つ左の白かつ列1-6の場所(oppo_mask_lrに当てはまる箇所)を追加
    r_oppo |= (r_oppo >> 1) & oppo_mask_lr
    u_oppo |= (u_oppo << 8) & oppo_mask_ud
    d_oppo |= (d_oppo >> 8) & oppo_mask_ud
    lu_oppo |= (lu_oppo << 9) & oppo_mask_lu_ru_ld_rd
    ru_oppo |= (ru_oppo << 7) & oppo_mask_lu_ru_ld_rd
    ld_oppo |= (ld_oppo >> 7) & oppo_mask_lu_ru_ld_rd
    rd_oppo |= (rd_oppo >> 9) & oppo_mask_lu_ru_ld_rd

    l_oppo |= (l_oppo << 1) & oppo_mask_lr  # 上記に当てはまる場所(l_oppo)かつ1つ左の白かつ列1-6の場所(oppo_mask_lrに当てはまる箇所)を追加
    r_oppo |= (r_oppo >> 1) & oppo_mask_lr
    u_oppo |= (u_oppo << 8) & oppo_mask_ud
    d_oppo |= (d_oppo >> 8) & oppo_mask_ud
    lu_oppo |= (lu_oppo << 9) & oppo_mask_lu_ru_ld_rd
    ru_oppo |= (ru_oppo << 7) & oppo_mask_lu_ru_ld_rd
    ld_oppo |= (ld_oppo >> 7) & oppo_mask_lu_ru_ld_rd
    rd_oppo |= (rd_oppo >> 9) & oppo_mask_lu_ru_ld_rd

    l_oppo |= (l_oppo << 1) & oppo_mask_lr  # 上記に当てはまる場所(l_oppo)かつ1つ左の白かつ列1-6の場所(oppo_mask_lrに当てはまる箇所)を追加
    r_oppo |= (r_oppo >> 1) & oppo_mask_lr
    u_oppo |= (u_oppo << 8) & oppo_mask_ud
    d_oppo |= (d_oppo >> 8) & oppo_mask_ud
    lu_oppo |= (lu_oppo << 9) & oppo_mask_lu_ru_ld_rd
    ru_oppo |= (ru_oppo << 7) & oppo_mask_lu_ru_ld_rd
    ld_oppo |= (ld_oppo >> 7) & oppo_mask_lu_ru_ld_rd
    rd_oppo |= (rd_oppo >> 9) & oppo_mask_lu_ru_ld_rd

    l_oppo |= (l_oppo << 1) & oppo_mask_lr  # 上記に当てはまる場所(l_oppo)かつ1つ左の白かつ列1-6の場所(oppo_mask_lrに当てはまる箇所)を追加
    r_oppo |= (r_oppo >> 1) & oppo_mask_lr
    u_oppo |= (u_oppo << 8) & oppo_mask_ud
    d_oppo |= (d_oppo >> 8) & oppo_mask_ud
    lu_oppo |= (lu_oppo << 9) & oppo_mask_lu_ru_ld_rd
    ru_oppo |= (ru_oppo << 7) & oppo_mask_lu_ru_ld_rd
    ld_oppo |= (ld_oppo >> 7) & oppo_mask_lu_ru_ld_rd
    rd_oppo |= (rd_oppo >> 9) & oppo_mask_lu_ru_ld_rd

    legal_left = (l_oppo << 1) & blank_board
    legal_right = (r_oppo >> 1) & blank_board
    legal_up = (u_oppo << 8) & blank_board
    legal_down = (d_oppo >> 8) & blank_board
    legal_lu = (lu_oppo << 9) & blank_board
    legal_ru = (ru_oppo << 7) & blank_board
    legal_ld = (ld_oppo >> 7) & blank_board
    legal_rd = (rd_oppo >> 9) & blank_board
    
    # 合計
    legal = legal_left | legal_right | legal_up | legal_down | legal_lu | legal_ru | legal_ld | legal_rd

    return legal

def step(black_board: int, white_board: int, player_id: int, action: int):
    """
    アクションする
    
    1. アクションする
    2. ゲーム状態の判定をする
    
    return:
      next_black_board
      next_white_board
      next_player
    """
    # 1. アクションする
    next_black_board, next_white_board = _set_stone(
        black_board, white_board, player_id, action
    )
    next_player = PLAYER_BLACK if player_id == PLAYER_WHITE else PLAYER_WHITE
    # 2. ゲーム状態の判定をする
    next_black_actionables = get_actionables(next_black_board, next_white_board, PLAYER_BLACK)
    next_white_actionables = get_actionables(next_black_board, next_white_board, PLAYER_WHITE)
    if next_black_actionables == 0 and next_white_actionables == 0:
        # どちらもアクション出来ない場合ゲーム終了
        next_player = PLAYER_UNKNOW
    elif next_player == PLAYER_BLACK:
        # 黒のアクションができない場合、次のプレイヤーは白
        if next_black_actionables == 0:
            next_player = PLAYER_WHITE
        else:
            next_player = PLAYER_BLACK
    else:
        # 白のアクションができない場合、次のプレイヤーは黒
        if next_white_actionables == 0:
            next_player = PLAYER_BLACK
        else:
            next_player = PLAYER_WHITE
    
    return next_black_board, next_white_board, next_player

def _set_stone(black_board: int, white_board: int, player_id: int, action: int) -> tuple[int, int]:
    """
    actionに石を置いてひっくり返す
    returns:
        next_black_board:
        next_white_board:
    """
    mask_lr = 0x7e7e7e7e7e7e7e7e
    mask_ud = 0x00ffffffffffff00
    mask_lu_ru_ld_rd = 0x007e7e7e7e7e7e00

    reverse = 0x0000000000000000

    # 自分と相手の座標を取得
    oppo_board = white_board if player_id == PLAYER_BLACK else black_board
    my_board = white_board if player_id != PLAYER_BLACK else black_board
    
    mask_left = mask_lr & oppo_board  # 左方向
    mask_right = mask_lr & oppo_board
    mask_up = mask_ud & oppo_board
    mask_down = mask_ud & oppo_board
    mask_left_up = mask_lu_ru_ld_rd & oppo_board
    mask_right_up = mask_lu_ru_ld_rd & oppo_board
    mask_left_down = mask_lu_ru_ld_rd & oppo_board
    mask_right_down = mask_lu_ru_ld_rd & oppo_board
    
    l_rev = (action << 1) & mask_left
    r_rev = (action >> 1) & mask_right
    u_rev = (action << 8) & mask_up
    d_rev = (action >> 8) & mask_down
    lu_rev = (action << 7) & mask_left_up
    ru_rev = (action << 9) & mask_right_up
    ld_rev = (action >> 9) & mask_left_down
    rd_rev = (action >> 7) & mask_right_down

    for i in range(5):
        l_rev |= (l_rev << 1) & mask_left
        r_rev |= (r_rev >> 1) & mask_right
        u_rev |= (u_rev << 8) & mask_up
        d_rev |= (d_rev >> 8) & mask_down
        lu_rev |= (lu_rev << 7) & mask_left_up
        ru_rev |= (ru_rev << 9) & mask_right_up
        ld_rev |= (ld_rev >> 9) & mask_left_down
        rd_rev |= (rd_rev >> 7) & mask_right_down

    if (l_rev << 1) & my_board != 0:
        reverse |= l_rev
    if (r_rev >> 1) & my_board != 0:
        reverse |= r_rev
    if (u_rev << 8) & my_board != 0:
        reverse |= u_rev
    if (d_rev >> 8) & my_board != 0:
        reverse |= d_rev
    if (lu_rev << 7) & my_board != 0:
        reverse |= lu_rev
    if (ru_rev << 9) & my_board != 0:
        reverse |= ru_rev
    if (ld_rev >> 9) & my_board != 0:
        reverse |= ld_rev
    if (rd_rev >> 7) & my_board != 0:
        reverse |= rd_rev

    my_board |= (action | reverse)
    oppo_board ^= reverse
    
    if player_id == PLAYER_BLACK:
        next_black_board, next_white_board = my_board, oppo_board
    else:
        next_black_board, next_white_board = oppo_board, my_board
    
    return next_black_board, next_white_board

def get_actionables_list(actionables: int) -> list:
    actionables_list = []
    mask = 0x8000000000000000
    for i in range(64):
        if mask & actionables != 0:
            actionables_list.append(mask)
        mask = mask >> 1
    return actionables_list