from typing import Optional, Union

from env_v2.env import PlayerId, GameInfo, Env2, GameState
from env_v2.evaluations.evaluate import simple_evaluate


class MiniMaxPlayer():
    def __init__(self, player_id: int = PlayerId.BLACK_PLAYER_ID.value, search_generation: int = 4) -> None:
        """
        MiniMax法でアクションを行う
        
        args:
            env: Env2
            search_generation: 探索世代数 TODO: のちのちベースノードの世代ごとに探索数を変えるかも。
        """
        self._env = Env2()
        self.player_id = player_id
        self._search_generation = search_generation
        self.MAX_VALUE = float("inf")
        self.MIN_VALUE = float("-inf")
        self.DRAW_VALUE = 0
    
    def action(self, game_info: GameInfo) -> int:
        """
        node_action: ベストなアクション
        """
        if game_info.actionables == 0:
            raise Exception("can not action")
        
        node_value, node_action = self._max(game_info, game_info["player_id"], 1)
        
        return node_action
        
        
    def _max(self, game_info: GameInfo, base_player_id: int, generation: int) -> tuple[int, int]:
        """
        args:
          env: Env2
          game_info: 現時点のベースノードのゲーム状態
          base_player_id: 探索が始まったベースノードのアクションPlayerId
          generation: ベースノードからの世代数(ベースノードを0とする)
        
        returns:
          node_value: ノードの評価値
          node_action: ノードが選択するアクション
        """
        max_node_value = self.MIN_VALUE
        
        for action in game_info["actionables"]:
            # action
            new_game_info = self._env.step(game_info=game_info, action=action)
            """
            judge game state
            ゲームが終了した場合それ以下のノードの探索は行わない(行えない)
            """
            new_game_state_value = new_game_info["game_state"].value[0]
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
                if generation >= self._search_generation:
                    # 探索終了のため末端ノードの評価値を取得
                    tmp_node_value = simple_evaluate(
                        new_game_info["black_board"], new_game_info["white_baord"], base_player_id
                    )
                else:
                    # 探索
                    if new_game_info["player_id"] == base_player_id:
                        tmp_node_value, _ = self._max(new_game_info, base_player_id, generation+1)
                    else:
                        tmp_node_value, _ = self._mini(new_game_info, base_player_id, generation+1)  

            # 更新
            if tmp_node_value == self.MAX_VALUE:
                return tmp_node_value, action
            
            if max_node_value < tmp_node_value:
                max_node_value = tmp_node_value 
                max_action = action 

        return max_node_value, max_action
            
    def _mini(self, game_info: GameInfo, base_player_id: int, generation: int) -> tuple[int, int]:
        """
        args:
          env: Env2
          game_info: 現時点のベースノードのゲーム状態
          base_player_id: 探索が始まったベースノードのアクションPlayerId
          generation: ベースノードからの世代数(ベースノードを0とする)
        
        returns:
          node_value: ノードの評価値
          node_action: ノードが選択するアクション
        """
        min_node_value = self.MAX_VALUE
        
        for action in game_info["actionables"]:
            # action
            new_game_info = self._env.step(game_info=game_info, action=action)
            """
            judge game state
            ゲームが終了した場合それ以下のノードの探索は行わない(行えない)
            """
            new_game_state_value = new_game_info["game_state"].value[0]
            if new_game_state_value == GameState.WIN_BLACK.value[0]:
                # win black player
                if base_player_id == PlayerId.BLACK_PLAYER_ID.value:
                    # win base player. 探索終了
                    tmp_node_value = self.MIN_VALUE 
                else:
                    # win opponent base player.
                    tmp_node_value = self.MAX_VALUE
            elif new_game_state_value == GameState.WIN_WHITE.value[0]:
                # win white plyaer
                if base_player_id == PlayerId.WHITE_PLAYER_ID.value:
                    # win base player. 探索終了
                    tmp_node_value = self.MIN_VALUE 
                else:
                    # win opponent base player.
                    tmp_node_value = self.MAX_VALUE
            elif new_game_state_value == GameState.DRAW.value[0]:
                tmp_node_value = self.DRAW_VALUE
            else:
                if generation >= self._search_generation:
                    # 探索終了のため末端ノードの評価値を取得
                    tmp_node_value = simple_evaluate(
                        new_game_info["black_board"], new_game_info["white_baord"], base_player_id
                    )
                else:
                    # 探索
                    if new_game_info["player_id"] == base_player_id:
                        tmp_node_value, _ = self._max(new_game_info, base_player_id, generation+1)
                    else:
                        tmp_node_value, _ = self._mini(new_game_info, base_player_id, generation+1)  

            # 更新
            if tmp_node_value == self.MIN_VALUE:
                return tmp_node_value, action
            
            if min_node_value > tmp_node_value:
                min_node_value = tmp_node_value 
                min_action = action 

        return min_node_value, min_action
        
        
        
        
        