"""
ゲームを対戦させる
"""
from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer


random_player_black = RandomPlayer(PlayerId.BLACK_PLAYER_ID.value)
random_player_white = MiniMaxPlayer(PlayerId.WHITE_PLAYER_ID.value)

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

