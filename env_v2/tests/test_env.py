import pytest
import unittest

from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer


class TestEnv2(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # print("setUpClass")
        pass
    
    def setUp(self):
        # print("setup")
        
        self._env = Env2(is_out_game_info=False, is_out_board=False)
    
    def tearDown(self) -> None:
        # print("tearDown")
        pass
    
    @classmethod
    def tearDownClass(cls):
        # print("tearDownClass")
        pass
        
    def test_random_play(self):
        """ 
        randomでプレイさせてエラーにならないこと(ゲームができること)
        """
        random_player_black = RandomPlayer(PlayerId.BLACK_PLAYER_ID.value)
        random_player_white = RandomPlayer(PlayerId.WHITE_PLAYER_ID.value)
        
        # 100回プレイしてエラーが発生しないこと
        play_num = 1000
        for play_count in range(1, play_num+1):
            # ゲームの初期化
            game_info = self._env.get_game_init()
        
            while True:
                # アクションプレイヤーの選択
                if game_info.player_id == random_player_black.player_id:
                    player = random_player_black
                else:
                    player = random_player_white
                    
                game_info = player.action(self._env, game_info)
                
                # ゲーム終了か判定
                if game_info.game_state.value[0] != GameState.IN_GAME.value[0]:
                    print(f"test play count: {play_count} is ok")
                    break
    
    # TODO: テストを追加する
    """
    通常のストーリーを3つくらい
    どっちも打つ手がなくなって途中でゲームが終了するパターン
    途中でどちらかの打つ手がなくなって連続でアクションするパターン
    途中ですべてどちらかの駒で埋まるパターン
    最後までいって引き分けで終了するパターン
    途中で終わるが引き分けのパターン
    """
    
            
            
