


def get_with_jp_unit(value: int) -> str:
    """
    万や億などの単位をつけて返す
    """
    # 単位(key=10の乗数, value=万や億などの単位)
    unit_map = {
        0: "",
        4: "万",
        8: "億",
        12: "兆",
        16: "京",
        20: "垓",
        24: "秭",
        28: "穣",
    }
    power_of_ten = get_powers_of_ten(value)
    if power_of_ten >= 32:
        raise Exception("value is over 10^32.")
    
    value_with_jp_unit_list = []
    for i in range(0, len(str(value)), 4):
        if i == 0:
            sdx = -4
            _value = str(value)[sdx:]
            value_with_jp_unit_list.append(str(int(_value)) + unit_map[i])
        else:
            sdx = -1 * (i+4) 
            edx = -1 * i 
            _value = str(value)[sdx:edx]
            value_with_jp_unit_list.append(str(int(_value)) + unit_map[i])

    # num = str(value)[-4:]  # 最初
    # value_with_jp_unit_list.append(str(value)[-4:])  # 最初
    # for key, unit in unit_map.items():
    #     if key > power_of_ten:
    #         value_with_jp_unit_list.append(str(value)[-key-4: -key])
    #         break
    #     else:
    #         value_with_jp_unit_list.append(str(value)[-key-4: -key] + unit)
    
    value_with_jp_unit_list.reverse()
    return "".join(value_with_jp_unit_list)


def get_powers_of_ten(value: int) -> int:
    """
    10の乗数を求める
    """
    power_of_ten = len(str(value)) - 1

    return power_of_ten