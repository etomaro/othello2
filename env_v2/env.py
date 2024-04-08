from dataclasses import dataclass
from enum import Enum
from typing import Union, Optional



class PlayerId(Enum):
    BLACK_PLAYER_ID = 0
    WHITE_PLAYER_ID = 1

class GameState(Enum):
    WIN_BLACK = 0, "黒(先行)の勝ち"  # 黒(先行)の勝ち
    WIN_WHITE = 1, "白(後攻)の勝ち"  # 白(後攻)の勝ち
    IN_GAME = 2, "ゲーム中"  # ゲーム中
    DRAW = 3, "引き分け"  # 引き分け
    
@dataclass
class GameInfo:
    black_board: int  # 黒石
    white_board: int  # 白石
    player_id: Optional[int]  # アクションプレイヤーid
    actionables: Optional[int]  # 可能なハンド
    game_state: GameState  # ゲーム状態
    generation: int # 世代(何局目か)(石の数で計算する)


class Env2():
    def __init__(self, is_out_game_info: bool = False, is_out_board: bool = False) -> None:
        """
        args:
            is_out_game_info: 毎ターンごとにゲーム情報を出力
            is_out_board: 盤面も出力
        """
        self._is_out_game_info = is_out_game_info 
        self._is_out_board = is_out_board
        
    @staticmethod
    def change_action_int_to_matrix(action: int) -> str:
        """
        (行,列)の形でアクションを表示する
        
        args:
          action: int
        """
        action = bin(action)[2:].zfill(64)
        action_index = action.index("1")
        row = ((action_index) // 8) + 1
        column = (action_index % 8) + 1
        
        return f"({row}, {column})"
    
    def get_game_init(self) -> GameInfo:
        """
        状態の初期状態を取得
        """
        black_board = black_board = 0x0000000810000000
        white_board = 0x0000001008000000
        actionables = 0x0000102004080000
        
        game_info = GameInfo(
            black_board=black_board,
            white_board=white_board,
            player_id=PlayerId.BLACK_PLAYER_ID.value,
            actionables=actionables,
            game_state=GameState.IN_GAME,
            generation=self._calc_generation(black_board, white_board)  # 0スタート
        )
        
        # ゲーム状態を出力
        if self._is_out_game_info:
            self.output_game_info(game_info)
        
        return game_info
    
    @staticmethod
    def _calc_generation(black_board: int, white_board: int) -> int:
        """
        世代数を石の数で計算
        
        returns
          generation: 何世代か。最初の番面を0としてスタート
        """
        STONE_NUM_INIT = 4
        black_count = bin(black_board).count("1")
        white_count = bin(white_board).count("1")
        
        generation = black_count + white_count - STONE_NUM_INIT
        
        return generation

    
    def output_game_info(self, game_info: GameInfo) -> None:
        """
        ゲーム状態を出力
        
        args
            game_info
        """
        # ゲーム初期状態の出力
        if game_info.generation == 0:
            print("\n------------ゲーム開始------------")
        
        if game_info.game_state.value[0] == GameState.IN_GAME.value[0]:
            # ゲーム中
            out = (
                f"世代: {game_info.generation}\n"
                f"黒の石の数: {bin(game_info.black_board).count('1')}\n"
                f"白の石の数: {bin(game_info.white_board).count('1')}\n"
                f"アクションプレイヤー: {game_info.player_id}\n"
                f"ゲーム状態: {game_info.game_state.value[1]}\n"
            )
        else:
            # ゲーム終了時
            out = (
                f"[ゲーム終了]\n"
                f"勝者: {game_info.game_state.value[1]}\n"
                f"黒の石の数: {bin(game_info.black_board).count('1')}\n"
                f"白の石の数: {bin(game_info.white_board).count('1')}\n"
            )

        print(out)
        
        # ボードの状態を表示
        if self._is_out_board:
            self._out_board(game_info.black_board, game_info.white_board)
        
        print("------------------------")
    
    @staticmethod
    def _out_board(black_board, white_board):
        black_board = bin(black_board)[2:].zfill(64)
        white_board = bin(white_board)[2:].zfill(64)

        result = "  1 2 3 4 5 6 7 8"
        for i in range(64):
            if i % 8 == 0:
                result += f"\n{i//8 + 1} "
            if black_board[i] == "1":
                result += "○ "
            elif white_board[i] == "1":
                result += "● "
            else:
                result += "- "
        
        print(result + "\n")
    
    def step(self, game_info: GameInfo, action: int) -> GameInfo:
        """
        アクション
            1. actionに石を置いてひっくり返す
            2. ゲームの勝敗を判定
            3. 次のアクションプレイヤーidとアクション可能な座標を算出

        args:
            game_info: ゲーム情報
            action: アクションする石の座標
        returns:
            {
                black_board: アクション後の黒石の状態
                white_board: アクション後の黒石の状態
                player_id: アクション後のアクションプレイヤーid
                actionables: アクション後のアクション可能な座標
                game_state: 0: ゲーム進行中, 1: 先行(黒)の勝ち, 2: 後攻(白)の勝ち
            }
        """
        
        # 1. actionに石を置いてひっくり返す
        next_black_board, next_white_board = self._set_stone(
            game_info.black_board, game_info.white_board, game_info.player_id, action
        )
        
        # 2. ゲームの勝敗を判定
        game_state, black_actionables, white_actionables = self._judge_geme_state(next_black_board, next_white_board)
        
        if game_state.value[0] != GameState.IN_GAME.value[0]:
            # ゲームが終了している場合
            
            game_info = GameInfo(
                black_board=next_black_board,
                white_board=next_white_board,
                player_id=None,
                actionables=None,
                game_state=game_state,
                generation=self._calc_generation(next_black_board, next_white_board)
            )
            
            # ゲーム情報を出力
            if self._is_out_game_info:
                self.output_game_info(game_info)
        
            return game_info
        
        # 3. 次のアクションプレイヤーidとアクション可能な座標を算出
        next_player_id = 1 - game_info.player_id 
        actionables = black_actionables if next_player_id == PlayerId.BLACK_PLAYER_ID.value else white_actionables
        
        if actionables == 0:
            # アクションができない場合
            next_player_id = 1 - next_player_id
            actionables = black_actionables if next_player_id == PlayerId.BLACK_PLAYER_ID.value else white_actionables

        game_info = GameInfo(
            black_board=next_black_board,
            white_board=next_white_board,
            player_id=next_player_id,
            actionables=actionables,
            game_state=game_state,
            generation=self._calc_generation(next_black_board, next_white_board)
        )
        
        # ゲーム情報を出力
        if self._is_out_game_info:
            self.output_game_info(game_info)
        
        return game_info
    
    @staticmethod
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
        oppo_board = white_board if player_id == PlayerId.BLACK_PLAYER_ID.value else black_board
        my_board = white_board if player_id != PlayerId.BLACK_PLAYER_ID.value else black_board
        
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
        
        if player_id == PlayerId.BLACK_PLAYER_ID.value:
            next_black_board, next_white_board = my_board, oppo_board
        else:
            next_black_board, next_white_board = oppo_board, my_board
        
        return next_black_board, next_white_board

    def _judge_geme_state(self, black_board: int, white_board: int) -> tuple[GameState, int, int]:
        """
        ゲームの勝敗を判定
        
        returns:
            game_state: GameInfo.X.value: 0: ゲーム進行中, 1: 先行(黒)の勝ち, 2: 後攻(白)の勝ち
        """
        black_count = bin(black_board).count("1")
        white_count = bin(white_board).count("1")
        
        black_actionables = self._get_actionables(black_board, white_board, PlayerId.BLACK_PLAYER_ID.value)
        white_actionables = self._get_actionables(black_board, white_board, PlayerId.WHITE_PLAYER_ID.value)
        
        if bin(black_actionables).count("1") == 0 and bin(white_actionables).count("1") == 0:
            if black_count < white_count:
                game_state = GameState.WIN_WHITE
            elif black_count > white_count:
                game_state = GameState.WIN_BLACK
            else:
                game_state = GameState.DRAW
        else:
            game_state = GameState.IN_GAME
        
        return game_state, black_actionables, white_actionables
    
    def _get_next_action_player_id_and_actionables(self, black_board: int, white_board: int, player_id: int) -> tuple[int, int]:
        """
        次のアクションプレイヤーidとアクション可能な座標を算出
        
        args:
            black_board:
            white_board:
            player_id: action player id
        return:
        
        """
        actionables = self._get_actionables(black_board, white_board, player_id)
        # アクション出来ない場合
        if actionables == 0b0:
            player_id = 1 - player_id
            actionables = self._get_actionables(black_board, white_board, player_id)
            
        next_player_id = 1 - player_id
        
        return actionables, next_player_id
    
    @staticmethod
    def _get_actionables(black_board: int, white_board: int, player_id: int) -> int:
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
        
        oppo_board = white_board if player_id == PlayerId.BLACK_PLAYER_ID.value else black_board
        my_board = white_board if player_id != PlayerId.BLACK_PLAYER_ID.value else black_board
        
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
        
