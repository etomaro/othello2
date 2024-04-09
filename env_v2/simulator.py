"""
ゲームを対戦させる
"""
import time
import csv
from dataclasses import dataclass
from typing import Union, Optional
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from env_v2.env import Env2, GameInfo, PlayerId, GameState
from env_v2.policy.random_player import RandomPlayer
from env_v2.policy.minimax_player import MiniMaxPlayer, AnalyticsInfo
from env_v2.evaluations.evaluate import SimpleEvaluate, SimpleEvaluateV2, HuristicEvaluate


@dataclass
class DetailReportRow:
    # 分析データ
    generation: int 
    black_board: int
    white_board: int
    action: Optional[int]
    search_time: Optional[float]
    search_all_num: Optional[int]
    search_num: Optional[int]
    search_cut_num: Optional[int]

def analytics(
    is_print_analytics: bool,
    detail_report_rows: list[DetailReportRow], last_game_info: GameInfo,
    game_time: float,
    black_model_name: str, white_model_name: str,
    black_search_depth: int, white_search_depth: int,
    black_evaluate_name: str, white_evaluate_name: str
):
    """
    ゲーム結果を分析する(ターミナルに出力とcsvとして保存)
      [csvとして保存]
        1. 概要レポート
          ファイル名: summary_{BLACK_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_vs_{WHITE_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_{作成日時(yyyymmdd(JS))}.csv
          header: 
            勝者
            黒の石の数
            白の石の数
            最大の探索時間の世代
            最大の探索時間
            最大の全探索数
            最大の実際の探索数
          row key:
            ※ 1行のみ
        2. 詳細レポート
          ファイル名: detail_{BLACK_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_vs_{WHITE_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_{作成日時(yyyymmdd(JS))}.csv
          header: 
            世代
            黒のボード
            白のボード
            アクション: ※ 最後の状態はアクションなし(空文字)
            探索時間
            全探索数
            実際の探索数
            カットした探索数
          row key:
            世代(0-59)
    """
    # ターミナル出力用
    out = ""
    out_summary = "[分析結果-概要]\n"
    out_detail = "[分析結果-詳細]\n"
    
    # 概要レポート
    date_now_str = datetime.now(tz=ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    # ファイル名: summary_{BLACK_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_vs_{WHITE_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_{作成日時(yyyymmdd(JS))}.csv
    summary_file_name =\
        f"summary_{black_model_name}_{black_search_depth}_{black_evaluate_name}_vs_"\
        f"{white_model_name}_{white_search_depth}_{white_evaluate_name}_{date_now_str}.csv"
    summary_folder = f"report/summary/{black_model_name}_{black_search_depth}_{white_model_name}_{white_search_depth}/"
    summary_folder_path = os.path.abspath(os.path.dirname(__file__)) + "/" + summary_folder
    # フォルダが存在しない場合作成
    if not os.path.exists(summary_folder_path):
        os.makedirs(summary_folder_path)
    summary_file_path = os.path.join(summary_folder_path, summary_folder_path+summary_file_name)
    summary_header = [
        "勝者", "黒の石の数", "白の石の数",
        "最大の探索時間の世代", "最大の探索時間", "最大の全探索数", "最大の実際の探索数",
        "ゲームにかかった時間"
    ]
    
    # 詳細レポート
    # ファイル名: detail_{BLACK_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_vs_{WHITE_MODEL_NAME}_{DEPTH}_{EVALUATE_NAME}_{作成日時(yyyymmdd(JS))}.csv
    detail_file_name =\
        f"detail_{black_model_name}_{black_search_depth}_{black_evaluate_name}_vs_"\
        f"{white_model_name}_{white_search_depth}_{white_evaluate_name}_{date_now_str}.csv"
    detail_folder = f"report/detail/{black_model_name}_{black_search_depth}_{white_model_name}_{white_search_depth}/"
    detail_folder_path = os.path.abspath(os.path.dirname(__file__)) + "/" +detail_folder
    # ディレクトリが存在しない場合作成する
    if not os.path.exists(detail_folder_path):
        os.makedirs(detail_folder_path)
    detail_file_path = os.path.join(detail_folder_path, detail_file_name)
    detail_header = [
        "世代", "黒のボード", "白のボード", "アクション",
        "探索時間", "全探索数", "実際の探索数", "カットした探索数"
    ]

    max_search_time_info = None
    
    for analytics_info in detail_report_rows:
        # analyticsがない場合はスキップ(最後の盤面など)
        if analytics_info.search_time is None:
            continue

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
    
    out_summary += (
        f"・最大の探索時間のゲーム情報\n"
        f"世代: {max_search_time_info.generation}\n"
        f"探索時間: {max_search_time_info.search_time}\n"
        f"全探索数(カットしたノードも含む): {max_search_time_info.search_all_num}\n"
        f"実際の探索数: {max_search_time_info.search_num}\n\n"
    )
    
    # ターミナル出力
    out += out_summary + "\n"
    out += out_detail
    out += "------------------------"
    if is_print_analytics:
        print(out)
    
    # レポート作成
    
    summary_row = [
        last_game_info.game_state.value[1], bin(last_game_info.black_board).count("1"),
        bin(last_game_info.white_board).count("1"),
        max_search_time_info.generation, max_search_time_info.search_time,
        max_search_time_info.search_all_num, max_search_time_info.search_num,
        game_time
    ]
    with open(summary_file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(summary_header)  # header
        writer.writerow(summary_row)
            
    with open(detail_file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(detail_header)
        for detail_report_row in detail_report_rows:
            writer.writerow(
                [
                    detail_report_row.generation,
                    detail_report_row.black_board,
                    detail_report_row.white_board,
                    detail_report_row.action,
                    detail_report_row.search_time,
                    detail_report_row.search_all_num,
                    detail_report_row.search_num,
                    detail_report_row.search_cut_num
                ]
            )

# ----------------simulation----------------
# debugフラグ
is_print_last_game_info = False  # ゲーム結果を出力するかどうか
is_print_analytics = False  # 探索情報を出力するかどうか
is_out_game_info = True  # 1手ごとのゲーム情報を出力するかどうか
is_out_board = True  # 1手ごとのボードを出力するかどうか
is_search_debug = False  # 探索で選択したノードを出力するかどうか

env = Env2(is_out_game_info=is_out_game_info, is_out_board=is_out_board)
player_black = MiniMaxPlayer(
    PlayerId.BLACK_PLAYER_ID.value, search_depth=5,
    evaluate_model=SimpleEvaluate, is_search_debug=is_search_debug
)
player_white = MiniMaxPlayer(
    PlayerId.WHITE_PLAYER_ID.value, search_depth=6,
    evaluate_model=SimpleEvaluate, is_search_debug=is_search_debug
)

play_num = 1
for play_count in range(1, play_num+1):
    # ゲームの初期化
    game_info = env.get_game_init()
    detail_report_rows = []
    
    # 1ゲームにかかる時間を計測
    start_game_time = time.time()
    while True:
        # アクションプレイヤーの選択
        if game_info.player_id == player_black.player_id:
            player = player_black
        else:
            player = player_white
        
        # アクションを選択する
        action, analytics_info = player.get_action(game_info)
        detail_report_row = DetailReportRow(
            generation=game_info.generation,
            black_board=game_info.black_board,
            white_board=game_info.white_board,
            action=action,
            search_time=analytics_info.search_time,
            search_all_num=analytics_info.search_all_num,
            search_num=analytics_info.search_num,
            search_cut_num=analytics_info.search_all_num-analytics_info.search_num
        )
        detail_report_rows.append(detail_report_row)
        
        # action
        game_info = env.step(game_info, action)
        
        # ゲーム終了か判定
        if game_info.game_state.value[0] != GameState.IN_GAME.value[0]:
            detail_report_row = DetailReportRow(
                generation=game_info.generation,
                black_board=game_info.black_board,
                white_board=game_info.white_board,
                action=None,
                search_time=None,
                search_all_num=None,
                search_num=None,
                search_cut_num=None
            )
            detail_report_rows.append(detail_report_row)
            break
    
    # ゲーム結果を出力
    analytics(
        is_print_analytics=is_print_analytics,
        detail_report_rows=detail_report_rows,
        last_game_info=game_info,
        game_time=time.time() - start_game_time,
        black_model_name=player_black.MODEL_NAME,
        white_model_name=player_white.MODEL_NAME,
        black_search_depth=player_black.search_depth,
        white_search_depth=player_white.search_depth,
        black_evaluate_name=player_black.evaluate_model.EVALUATE_NAME,
        white_evaluate_name=player_white.evaluate_model.EVALUATE_NAME
    )
    if is_print_last_game_info:
        env.output_game_info(game_info)
