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
        
        self._env = Env2(is_debug=False, is_debug_detail=False)
    
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
        play_num = 100
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
            
            
