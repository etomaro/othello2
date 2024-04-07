from typing import Optional, Union
import time
from dataclasses import dataclass

from env_v2.env import PlayerId, GameInfo, Env2, GameState
from env_v2.evaluations.evaluate import SimpleEvaluate

@dataclass
class AnalyticsInfo:
    generation: int  # 世代
    search_time: float  # 処理時間
    search_num: int  # 探索数(カットしたノードは含まない)
    search_all_num: int  # 全探索数
    

class MiniMaxPlayer():
    MODEL_NAME = "MINIMAX"
    def __init__(
        self, player_id: int = PlayerId.BLACK_PLAYER_ID.value,
        search_depth: int = 4,
        evaluate_model=SimpleEvaluate
    ) -> None:
        """
        MiniMax法でアクションを行う
        
        args:
            env: Env2
            search_depth: 探索世代数 TODO: のちのちベースノードの世代ごとに探索数を変えるかも。
        """
        self._env = Env2(is_out_game_info=False, is_out_board=False)
        self.player_id = player_id
        self.search_depth = search_depth
        self.evaluate_model = evaluate_model
        self.evaluate = evaluate_model.evaluate
        self.MAX_VALUE = float("inf")
        self.MIN_VALUE = float("-inf")
        self.DRAW_VALUE = 0
    
    def get_action(self, game_info: GameInfo) -> tuple[int, AnalyticsInfo]:
        """
        node_action: ベストなアクション
        """
        if game_info.actionables == 0:
            raise Exception("can not action")
        
        start_time = time.time()  # 処理時間を計算
        
        analytics_info = AnalyticsInfo(
            generation = game_info.generation,
            search_time = None,
            search_num = 0,
            search_all_num = 0
        )
        
        # アクションを選択
        node_value, node_action = self._max(
            game_info=game_info, base_player_id=game_info.player_id, depth=1,
            analytics_info=analytics_info
        )
        
        analytics_info.search_time = time.time() - start_time
        
        return node_action, analytics_info
        
        
    def _max(
        self, game_info: GameInfo, base_player_id: int, depth: int,
       analytics_info: AnalyticsInfo
    ) -> tuple[int, int]:
        """
        args:
          env: Env2
          game_info: 現時点のベースノードのゲーム状態
          base_player_id: 探索が始まったベースノードのアクションPlayerId
          depth: ベースノードからの世代数(ベースノードを0とする)
          analytics_info
        
        returns:
          node_value: ノードの評価値
          node_action: ノードが選択するアクション
        """
        
        # 探索数をカウント
        analytics_info.search_all_num += bin(game_info.actionables).count("1")
        
        max_node_value = self.MIN_VALUE
        max_action = None
        
        for action in self._get_actionables_list(game_info.actionables):
            
            # 実際の探索数をカウント
            analytics_info.search_num += 1
            
            # action
            new_game_info = self._env.step(game_info=game_info, action=action)
            """
            judge game state
            ゲームが終了した場合それ以下のノードの探索は行わない(行えない)
            """
            new_game_state_value = new_game_info.game_state.value[0]
            if new_game_state_value == GameState.WIN_BLACK.value[0]:
                # win black player
                if base_player_id == PlayerId.BLACK_PLAYER_ID.value:
                    # win base player. 探索終了
                    tmp_node_value = self.MAX_VALUE 
                else:
                    # win opponent base player.
                    tmp_node_value = self.MIN_VALUE
            elif new_game_state_value == GameState.WIN_WHITE.value[0]:
                # win white plyaer
                if base_player_id == PlayerId.WHITE_PLAYER_ID.value:
                    # win base player. 探索終了
                    tmp_node_value = self.MAX_VALUE 
                else:
                    # win opponent base player.
                    tmp_node_value = self.MIN_VALUE
            elif new_game_state_value == GameState.DRAW.value[0]:
                tmp_node_value = self.DRAW_VALUE
            else:
                if depth >= self.search_depth:
                    # 探索終了のため末端ノードの評価値を取得
                    tmp_node_value = self.evaluate(
                        new_game_info.black_board, new_game_info.white_board, base_player_id
                    )
                else:
                    # 探索
                    if new_game_info.player_id == base_player_id:
                        tmp_node_value, _ = self._max(new_game_info, base_player_id, depth+1, analytics_info)
                    else:
                        tmp_node_value, _ = self._mini(new_game_info, base_player_id, depth+1, analytics_info)  

            # 更新
            if tmp_node_value == self.MAX_VALUE:
                return tmp_node_value, action
            
            if max_action is None:
                max_action = action
                max_node_value = tmp_node_value 
            elif max_node_value < tmp_node_value:
                max_node_value = tmp_node_value 
                max_action = action
            else:
                pass

        return max_node_value, max_action
            
    def _mini(
        self, game_info: GameInfo, base_player_id: int, depth: int, analytics_info: AnalyticsInfo
    ) -> tuple[int, int]:
        """
        args:
          env: Env2
          game_info: 現時点のベースノードのゲーム状態
          base_player_id: 探索が始まったベースノードのアクションPlayerId
          depth: ベースノードからの世代数(ベースノードを0とする)
        
        returns:
          node_value: ノードの評価値
          node_action: ノードが選択するアクション
        """
        # 探索数をカウント
        analytics_info.search_all_num += bin(game_info.actionables).count("1")

        min_node_value = self.MAX_VALUE
        min_action = None
        
        for action in self._get_actionables_list(game_info.actionables):
            # 実際の探索数をカウント
            analytics_info.search_num += 1

            # action
            new_game_info = self._env.step(game_info=game_info, action=action)
            """
            judge game state
            ゲームが終了した場合それ以下のノードの探索は行わない(行えない)
            """
            new_game_state_value = new_game_info.game_state.value[0]
            if new_game_state_value == GameState.WIN_BLACK.value[0]:
                # win black player
                if base_player_id == PlayerId.BLACK_PLAYER_ID.value:
                    # win base player. 探索終了
                    tmp_node_value = self.MAX_VALUE 
                else:
                    # win opponent base player.
                    tmp_node_value = self.MIN_VALUE
            elif new_game_state_value == GameState.WIN_WHITE.value[0]:
                # win white plyaer
                if base_player_id == PlayerId.WHITE_PLAYER_ID.value:
                    # win base player. 探索終了
                    tmp_node_value = self.MAX_VALUE 
                else:
                    # win opponent base player.
                    tmp_node_value = self.MIN_VALUE
            elif new_game_state_value == GameState.DRAW.value[0]:
                tmp_node_value = self.DRAW_VALUE
            else:
                if depth >= self.search_depth:
                    # 探索終了のため末端ノードの評価値を取得
                    tmp_node_value = self.evaluate(
                        new_game_info.black_board, new_game_info.white_board, base_player_id
                    )
                else:
                    # 探索
                    if new_game_info.player_id == base_player_id:
                        tmp_node_value, _ = self._max(new_game_info, base_player_id, depth+1, analytics_info)
                    else:
                        tmp_node_value, _ = self._mini(new_game_info, base_player_id, depth+1, analytics_info)  

            # 更新
            if tmp_node_value == self.MIN_VALUE:
                return tmp_node_value, action
            
            if min_action is None:
                min_action = action 
            elif min_node_value > tmp_node_value:
                min_node_value = tmp_node_value 
                min_action = action 
            else:
                pass

        return min_node_value, min_action

    @staticmethod
    def _get_actionables_list(actionables: int) -> list:
        actionables_list = []
        mask = 0x8000000000000000
        for i in range(64):
            if mask & actionables != 0:
                actionables_list.append(mask)
            mask = mask >> 1
        return actionables_list
        
        
        
        
        