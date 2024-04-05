import random

from env_v2.env import PlayerId, GameInfo, Env2


class RandomPlayer():
    def __init__(self, player_id=PlayerId.BLACK_PLAYER_ID.value):
        self.player_id = PlayerId.BLACK_PLAYER_ID.value if player_id==PlayerId.BLACK_PLAYER_ID.value else PlayerId.WHITE_PLAYER_ID.value
        self._env = Env2()
    def action(self, game_info: GameInfo) -> GameInfo:
        if game_info.actionables == 0:
            raise Exception("can not action")
        
        # ランダムにアクションを選択する
        actionables_list = []
        mask = 0x8000000000000000
        for i in range(64):
            if mask & game_info.actionables != 0:
                actionables_list.append(mask)
            mask = mask >> 1

        action = random.choice(actionables_list)
        
        # アクション
        next_game_info = self._env.step(game_info, action)
        
        return next_game_info
        
        
        
        