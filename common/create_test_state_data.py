import random


def create_data(state_num: int) -> list[tuple]:
    """スピード比較用にデータ作成
    
    登録するデータ
      1. 黒石: 0x0-0x1111111111111111
      2. 白石: 0x0-0x1111111111111111
      3. player: 0 or 1
    
    args:
      state_num: 登録する件数
    returns:
      create_data: 登録するデータ
    """
    lower_bound = 0x0
    upper_bound = 0x1111111111111111
    
    data = [
        (random.randint(lower_bound, upper_bound),
         random.randint(lower_bound, upper_bound),
         random.randint(0, 1)
         ) for _ in range(state_num)]

    return data