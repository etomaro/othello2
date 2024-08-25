"""
状態数分析用(by_numpy)にenvを作成

分析の処理の流れ
1. 1世代前の状態(黒石、白石、アクションプレイヤー)を取得する
---下記分散処理---
2. アクション可能ハンドを取得
3. アクション
4. 次の状態を取得
5. 次の状態をファイルに作成
6. 分析結果ファイルを作成
"""
import numpy as np
from numba import jit, vectorize, prange, guvectorize, uint64


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

def get_actions(states: np.ndarray) -> np.ndarray:
    """
    アクション可能な座標を算出
    
    ※ 結果が可変長のためnumpyを使うのに不向き
    ※ numpyを使用しないためjitを使っても意味ないので使用していない
    
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
        states: [[black_board, white_board, player_id], ...]
    returns:
        actions: [[black_board, white_board, player_id, action], ...]
    """
    PLAYER_BLACK = 0
    PLAYER_WHITE = 1
    PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)

    mask_lr = 0x7e7e7e7e7e7e7e7e
    mask_ud = 0x00ffffffffffff00
    mask_lu_ru_ld_rd = 0x007e7e7e7e7e7e00
    
    actions = []
    for state in states:
        # 空白の場所
        bb, wb, pi = int(state[0]), int(state[1]), int(state[2])
        blank_board = ~(bb | wb)
        
        oppo_board = wb if pi == PLAYER_BLACK else bb
        my_board = wb if pi != PLAYER_BLACK else bb
        
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
        
        # アクションを作成
        mask = 0x8000000000000000
        for _ in range(64):  
            if (mask & legal) != 0:
                actions.append([bb,wb,pi,mask])
            mask = mask >> 1
    
    print("get actions calc done")
    return np.array(actions, dtype=np.uint64)

@guvectorize([(uint64[:], uint64[:])], '(n)->()', target='parallel')
def get_actionables_parallel(states, res):
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
        array: [black_board, white_board, player_id]
    returns:
        actionables:
    """
    PLAYER_BLACK = 0
    PLAYER_WHITE = 1
    PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)

    mask_lr = 0x7e7e7e7e7e7e7e7e
    mask_ud = 0x00ffffffffffff00
    mask_lu_ru_ld_rd = 0x007e7e7e7e7e7e00
    
    # 空白の場所
    blank_board = ~(states[0] | states[1])
    
    oppo_board = states[1] if states[2] == PLAYER_BLACK else states[0]
    my_board = states[1] if states[2] != PLAYER_BLACK else states[0]
    
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

    res[0] =  legal  # returnを設定

@guvectorize([(uint64[:], uint64[:], uint64[:])], '(n),(m)->(m)')
def step_parallel(actions, dummy, out):
    """
    アクションする
    
    1. アクションする
    2. ゲーム状態の判定をする
    
    ※ 入力で使用した要素数と出力の要素数を合わせる必要があるのでdummyを設定しているが、使用することはない
    ex)step_parallel(
        np.array([
            [black_board1, white_board1, player_id1, action1],
            [black_board2, white_board2, player_id2, action2],
        ]),
        np.array([0,0,0])
    )
    
    ※ 外部の関数を使用することができないので本関数内に使用する関数を定義
    
    ※ target='parallel'を指定するとrayから呼び出し時にエラーが出る
    
    TODO: アクションをシリアライズしてactionsもこの関数内で出力する方法もあり
    
    args:
      actions: [black_board, white_board, player_id, action]
    return:
      next_states[next_black_board, next_white_board, next_player]
    """
    def _set_stone(black_board: int, white_board: int, player_id: int, action: int) -> tuple[int, int]:
        """
        actionに石を置いてひっくり返す
        returns:
            next_black_board:
            next_white_board:
        """
        PLAYER_BLACK = 0
        PLAYER_WHITE = 1
        PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)
        
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

        for _ in range(5):
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
        PLAYER_BLACK = 0
        PLAYER_WHITE = 1
        PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)
        
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

    def _get_y(board: int) -> int:
        """
        1. y軸
        """
        # 列ごとに反転する
        mask1 = 0x8080808080808080  # 列1
        mask2 = 0x4040404040404040  # 列2
        mask3 = 0x2020202020202020  # 列3
        mask4 = 0x1010101010101010  # 列4
        mask5 = 0x0808080808080808  # 列5
        mask6 = 0x0404040404040404  # 列6
        mask7 = 0x0202020202020202  # 列7
        mask8 = 0x0101010101010101  # 列8
        
        result_board = 0x0000000000000000
        
        result_board |= (board & mask1) >> 7
        result_board |= (board & mask2) >> 5
        result_board |= (board & mask3) >> 3
        result_board |= (board & mask4) >> 1
        result_board |= (board & mask5) << 1
        result_board |= (board & mask6) << 3
        result_board |= (board & mask7) << 5
        result_board |= (board & mask8) << 7
        
        return result_board
        

    def _get_x(board:int) -> int:
        """
        2. x軸
        """
        # 行ごとに反転する
        mask1 = 0xff00000000000000  # 行1
        mask2 = 0x00ff000000000000  # 行2
        mask3 = 0x0000ff0000000000  # 行3
        mask4 = 0x000000ff00000000  # 行4
        mask5 = 0x00000000ff000000  # 行5
        mask6 = 0x0000000000ff0000  # 行6
        mask7 = 0x000000000000ff00  # 行7
        mask8 = 0x00000000000000ff  # 行8
        
        result_board = 0x0000000000000000
        
        result_board |= (board & mask1) >> 56  # 7*8
        result_board |= (board & mask2) >> 40
        result_board |= (board & mask3) >> 24
        result_board |= (board & mask4) >> 8
        result_board |= (board & mask5) << 8
        result_board |= (board & mask6) << 24
        result_board |= (board & mask7) << 40
        result_board |= (board & mask8) << 56
        
        return result_board

    def _get_right_z(board:int) -> int:
        """
        3. 右斜め軸
        """
        # 右斜めごとに反転する
        mask1 = 0x8000000000000000  # 斜め1
        mask2 = 0x4080000000000000  # 斜め2
        mask3 = 0x2040800000000000  # 斜め3
        mask4 = 0x1020408000000000  # 斜め4
        mask5 = 0x0810204080000000  # 斜め5
        mask6 = 0x0408102040800000  # 斜め6
        mask7 = 0x0204081020408000  # 斜め7
        
        mask8 = 0x0102040810204080  # 斜め8
        
        mask9 = 0x0001020408102040  # 斜め9
        mask10 = 0x0000010204081020  # 斜め10
        mask11 = 0x0000000102040810  # 斜め11
        mask12 = 0x0000000001020408  # 斜め12
        mask13 = 0x0000000000010204  # 斜め13
        mask14 = 0x0000000000000102  # 斜め14
        mask15 = 0x0000000000000001  # 斜め15
        
        result_board = 0x0000000000000000
        
        result_board |= (board & mask1) >> 63
        result_board |= (board & mask2) >> 54  # 8*6+6
        result_board |= (board & mask3) >> 45  # 8*5+5
        result_board |= (board & mask4) >> 36  # 8*4+4
        result_board |= (board & mask5) >> 27  # 8*3+3
        result_board |= (board & mask6) >> 18  # 8*2+2 
        result_board |= (board & mask7) >> 9  # 8*1+1
        
        result_board |= (board & mask8)
        
        result_board |= (board & mask9) << 9  
        result_board |= (board & mask10) << 18
        result_board |= (board & mask11) << 27
        result_board |= (board & mask12) << 36
        result_board |= (board & mask13) << 45
        result_board |= (board & mask14) << 54
        result_board |= (board & mask15) << 63
        
        return result_board

    def _get_left_z(board:int) -> tuple:
        """
        4. 左斜め軸
        """
        # 左斜めごとに反転する
        mask1 = 0x0100000000000000  # 斜め1
        mask2 = 0x0201000000000000  # 斜め2
        mask3 = 0x0402010000000000  # 斜め3
        mask4 = 0x0804020100000000  # 斜め4
        mask5 = 0x1008040201000000  # 斜め5
        mask6 = 0x2010080402010000  # 斜め6
        mask7 = 0x4020100804020100  # 斜め7
        
        mask8 = 0x8040201008040201  # 斜め8
        
        mask9 = 0x0080402010080402  # 斜め9
        mask10 = 0x0000804020100804  # 斜め10
        mask11 = 0x0000008040201008  # 斜め11
        mask12 = 0x0000000080402010  # 斜め12
        mask13 = 0x0000000000804020  # 斜め13
        mask14 = 0x0000000000008040  # 斜め14
        mask15 = 0x0000000000000080  # 斜め15
        
        result_board = 0x0000000000000000
        
        result_board |= (board & mask1) >> 49 # 8*6+1
        result_board |= (board & mask2) >> 42  # 8*5+2
        result_board |= (board & mask3) >> 35  # 8*4+3
        result_board |= (board & mask4) >> 28  # 8*3+4
        result_board |= (board & mask5) >> 21  # 8*2+5
        result_board |= (board & mask6) >> 14  # 8*1+6 
        result_board |= (board & mask7) >> 7  # 8*0+7
        
        result_board |= (board & mask8)
        
        result_board |= (board & mask9) << 7  
        result_board |= (board & mask10) << 14
        result_board |= (board & mask11) << 21
        result_board |= (board & mask12) << 28
        result_board |= (board & mask13) << 35
        result_board |= (board & mask14) << 42
        result_board |= (board & mask15) << 49
        
        return result_board

    def _get_rotato90(board:int) -> tuple:
        """
        5. 90度回転
        
        横1列を縦1列に変換して90度回転する
        ex:横0->縦7
        """
        result_board = 0x0000000000000000
        base_mask = 0x8000000000000000
        
        for i in range(8):  # 行
            for j in range(8):  # 列
                mask = base_mask >> (i*8+j)
                move = (-j-i*8) + (7-i) + (j*8)  # (0,0)基点で計算
                if move >=0:
                    result_board |= (board & mask) >> move
                else:
                    result_board |= (board & mask) << -move
        
        return result_board

    def _get_rotato180(board:int) -> tuple:
        """
        6. 180度回転
        """
        # TODO: 効率化できる
        for _ in range(2):
            board = _get_rotato90(board)
        
        return board

    def _get_rotato270(board:int) -> tuple:
        """
        7. 270度回転
        """
        # TODO: 効率化できる
        for _ in range(3):
            board = _get_rotato90(board)
        
        return board

    PLAYER_BLACK = 0
    PLAYER_WHITE = 1
    PLAYER_UNKNOW = 2  # ゲーム終了(誰が勝ったかの状態は持たない)
    
    # 1. アクションする
    next_black_board, next_white_board = _set_stone(
        actions[0], actions[1], actions[2], actions[3]
    )
    next_player = PLAYER_BLACK if actions[2] == PLAYER_WHITE else PLAYER_WHITE
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
    
    # 1つ目の要素が最小のタプルを取得
    # 1つ目の要素が最小の要素が複数ある場合、2つ目の要素が小さいタプルを取得
    sym_black_board = next_black_board
    sym_white_board = next_white_board

    # 1. get_y
    tmp_black_board = _get_y(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_y(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_y(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 2. get_x
    tmp_black_board = _get_x(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_x(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_x(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 3. _get_right_z
    tmp_black_board = _get_right_z(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_right_z(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_right_z(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 4. _get_left_z
    tmp_black_board = _get_left_z(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_left_z(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_left_z(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 5. _get_rotato90
    tmp_black_board = _get_rotato90(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_rotato90(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_rotato90(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 6. _get_rotato180
    tmp_black_board = _get_rotato180(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_rotato180(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_rotato180(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 7. _get_rotato270
    tmp_black_board = _get_rotato270(next_black_board)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_rotato270(next_white_board)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_rotato270(next_white_board)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
        
    out[0] = sym_black_board
    out[1] = sym_white_board
    out[2] = next_player

def get_actionables_list(actionables: int) -> list:
    actionables_list = []
    mask = 0x8000000000000000
    for i in range(64):
        if mask & actionables != 0:
            actionables_list.append(mask)
        mask = mask >> 1
    return actionables_list

# @jit(nopython=True)
# def get_actions(states: np.ndarray, actionables: np.ndarray) -> np.ndarray:
#     """
#     ※ statesとactionablesのshape[0]の要素数は同じ
    
#     args:
#         states: [[BLACK_BOARD, WHITE_BOARD, PLAYER_ID],..]
#         actionables: [actionables1, ..]
#     returns:
#         actions: [BLACK_BOARD, WHITE_BOARD, PLAYER_ID, ACTION]
#     """
#     def get_actionables_list(actionables: int) -> list:
#         actionables_list = []
#         mask = 0x8000000000000000
#         for _ in range(64):
#             if mask & actionables != 0:
#                 actionables_list.append(mask)
#             mask = mask >> 1
#         return actionables_list
#     """
#     1. 1stateに対してアクション数を取得
#     2. アクション数分stateをコピー
#     3. stateにアクションを追加
#     """
#     actions = np.array([[0,0,0,0]])
#     for i in prange(actionables.shape[0]):
#         actionables_list = get_actionables_list(actionables[i])
#         tmp_actions = [np.concatenate([states[i], actionables_list[i]]) for i in prange(actionables_list)]
#         actions = np.concatenate([actions, tmp_actions])
#     actions =  np.delete(actions, 0, axis=0)
    
#     return actions
    