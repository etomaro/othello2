"""
ゲームを対戦させる
"""
import time

from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo


env = Env2(is_out_game_info=True, is_out_board=True)
random_player_black = MiniMaxPlayer(PlayerId.BLACK_PLAYER_ID.value, search_generation=5)
random_player_white = MiniMaxPlayer(PlayerId.WHITE_PLAYER_ID.value, search_generation=6)


def analytics(analytics_list: list[AnalyticsInfo]):
    """
    ゲーム結果を分析する
      1. 1アクションの探索時間
      2. 1アクションの探索ノード数
    """
    out = ""
    out_summary = "[分析結果-概要]\n"
    out_detail = "[分析結果-詳細]\n"
    
    max_search_time_info = None
    max_search_all_num_info = None
    max_search_num_info = None
    
    for analytics_info in analytics_list:
        out_detail += (
            f"世代: {analytics_info.generation}\n"
            f"探索時間: {analytics_info.search_time}\n"
            f"全探索数(カットしたノードも含む): {analytics_info.search_all_num}\n"
            f"実際の探索数: {analytics_info.search_num}\n"
            f"カットした探索数: {analytics_info.search_all_num - analytics_info.search_num}\n\n"
        )
        
        # 探索時間の最大値
        if max_search_time_info is None or\
            max_search_time_info.search_time < analytics_info.search_time:
            max_search_time_info = analytics_info
        # 全探索数の最大値
        if max_search_all_num_info is None or\
            max_search_all_num_info.search_all_num < analytics_info.search_all_num:
            max_search_all_num_info = analytics_info
        # 実際の探索数の最大値
        if max_search_num_info is None or\
            max_search_num_info.search_num < analytics_info.search_num:
            max_search_num_info = analytics_info
    
    out_summary += (
        f"・最大の探索時間\n"
        f"世代: {max_search_time_info.generation}\n"
        f"探索時間: {max_search_time_info.search_time}\n\n"
    )
    out_summary += (
        f"・最大の全探索数(カットしたノードも含む)\n"
        f"世代: {max_search_all_num_info.generation}\n"
        f"全探索数(カットしたノードも含む): {max_search_all_num_info.search_all_num}\n\n"
    )
    out_summary += (
        f"・最大の実際の探索数\n"
        f"世代: {max_search_num_info.generation}\n"
        f"探索時間: {max_search_num_info.search_num}\n\n"
    )
    
    out += out_summary + "\n"
    out += out_detail
    out += "------------------------"
    print(out)

play_num = 1
for play_count in range(1, play_num+1):
    # ゲームの初期化
    game_info = env.get_game_init()
    analytics_list = []
    
    while True:
        # アクションプレイヤーの選択
        if game_info.player_id == random_player_black.player_id:
            player = random_player_black
        else:
            player = random_player_white
            
        action, analytics_info = player.get_action(game_info)
        analytics_list.append(analytics_info)
        
        game_info = env.step(game_info, action)
        
        # ゲーム終了か判定
        if game_info.game_state.value[0] != GameState.IN_GAME.value[0]:
            break
    
    # ゲーム結果を出力
    analytics(analytics_list)
    env.output_game_info(game_info)
