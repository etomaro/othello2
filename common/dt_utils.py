def sec_to_str(calc_time: int) -> str:
    """
    秒を{hour}h{minute}m{seconds}sの形式に変換する
    """
    minute_slot = 60
    hour_slot = 60*60

    calc_time_str = ""
    if (calc_time // hour_slot) >= 1:
        # 1時間以上の場合
        hour = calc_time // hour_slot
        calc_time -= hour * hour_slot
        calc_time_str += f"{int(hour)}h"
    if (calc_time // minute_slot) >= 1:
        # 1分以上の場合
        minute = calc_time // minute_slot 
        calc_time -= minute * minute_slot 
        calc_time_str += f"{int(minute)}m"
    # 秒の追加
    calc_time_str += f"{int(calc_time)}s"

    return calc_time_str