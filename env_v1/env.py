from dataclasses import dataclass
from enum import Enum
from typing import Union, Optional

from env_v1.policy import Policy


BLACK_PLAYER_ID = 0
WHITE_PLAYER_ID = 1

@dataclass
class GameInfo:
    black_board: int  # 黒石
    white_board: int  # 白石
    player_id: Optional[int]  # アクションプレイヤーid
    actionables: Optional[int]  # 可能なハンド
    game_state: int  # ゲーム状態

class PlayerId(Enum):
    BLACK_PLAYER_ID: 0
    WHITE_PLAYER_ID: 1

class GameState(Enum):
    IN_GAME: 0  # ゲーム中
    WIN_BLACK: 1  # 先行(黒)の勝ち
    WIN_WHITE: 2  # 後攻(白)の勝ち
    
class ENV2():
    def __init__(self) -> dict:
        """
        args:
            policy_id: 方策アクションid
            evaluate_id: 評価関数id
            player_id: 0=先行(黒), 1=後攻(白)
        """
        pass
    
    @staticmethod
    def get_game_init() -> GameInfo:
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
            game_state=GameState.IN_GAME.value
        )
        
        return game_info
    
    def step(self, black_board: int, white_board: int, player_id: int, position: int) -> GameInfo:
        """
        アクション
            1. positionに石を置いてひっくり返す
            2. ゲームの勝敗を判定
            3. 次のアクションプレイヤーidとアクション可能な座標を算出

        args:
            black_board: 黒石の状態
            white_board: 白石の状態
            player_id: アクションプレイヤーid
            position: アクションする石の座標
        returns:
            {
                black_board: アクション後の黒石の状態
                white_board: アクション後の黒石の状態
                player_id: アクション後のアクションプレイヤーid
                actionables: アクション後のアクション可能な座標
                game_state: 0: ゲーム進行中, 1: 先行(黒)の勝ち, 2: 後攻(白)の勝ち
            }
        """
        
        # 1. positionに石を置いてひっくり返す
        next_black_board, next_white_board = self._set_stone(black_board, white_board, player_id, position)
        
        # 2. ゲームの勝敗を判定
        game_state = self._judge_geme_state(next_black_board, next_white_board)
        
        if game_state != 0:
            # ゲームが終了している場合
            
            game_info = GameInfo(
                black_board=next_black_board,
                white_board=next_white_board,
                player_id=None,
                actionables=None,
                game_state=game_state
            )
            
            return game_info
        
        # 3. 次のアクションプレイヤーidとアクション可能な座標を算出
        
    
    @staticmethod
    def _set_stone(black_board: int, white_board: int, player_id: int, position: int) -> tuple[int, int]:
        """
        positionに石を置いてひっくり返す
        returns:
            next_black_board:
            next_white_board:
        """
        next_black_board, next_white_board = 0x0, 0x0
        
        return next_black_board, next_white_board

    @staticmethod
    def _judge_geme_state(black_board: int, white_board: int) -> int:
        """
        ゲームの勝敗を判定
        
        returns:
            game_state: GameInfo.X.value: 0: ゲーム進行中, 1: 先行(黒)の勝ち, 2: 後攻(白)の勝ち
        """
        game_state = 0
        
        return game_state
    
    @staticmethod
    def _get_next_action_player_id_and_actionables(black_board: int, white_board: int, player_id: int) -> tuple[int, int]:
        """
        次のアクションプレイヤーidとアクション可能な座標を算出
        
        args:
            black_board:
            white_board:
            player_id:
        """
    


env = ENV2(1,1)