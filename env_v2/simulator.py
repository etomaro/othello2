"""
ゲームを対戦させる
"""
from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer


env = Env2(is_out_game_info=True, is_out_board=True)
random_player_black = MiniMaxPlayer(PlayerId.BLACK_PLAYER_ID.value)
random_player_white = MiniMaxPlayer(PlayerId.WHITE_PLAYER_ID.value)

# 100回プレイしてエラーが発生しないこと
play_num = 1
for play_count in range(1, play_num+1):
    # ゲームの初期化
    game_info = env.get_game_init()

    while True:
        # アクションプレイヤーの選択
        if game_info.player_id == random_player_black.player_id:
            player = random_player_black
        else:
            player = random_player_white
            
        action = player.get_action(game_info)
        
        game_info = env.step(game_info, action)
        
        # ゲーム終了か判定
        if game_info.game_state.value[0] != GameState.IN_GAME.value[0]:
            env.output_game_info(game_info)
            break

