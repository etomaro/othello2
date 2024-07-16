
def get_symmetorys(black_board:int, white_board:int) -> list[tuple]:
    """
    対称性
    1. y軸
    2. x軸
    3. 右斜め軸
    4. 左斜め軸
    5. 90度回転
    6. 180度回転
    7. 270度回転
    """
    symmetorys = []
    symmetorys.append(_get_y(black_board, white_board))
    symmetorys.append(_get_x(black_board, white_board))
    symmetorys.append(_get_right_z(black_board, white_board))
    symmetorys.append(_get_left_z(black_board, white_board))
    symmetorys.append(_get_rotato90(black_board, white_board))
    symmetorys.append(_get_rotato180(black_board, white_board))
    symmetorys.append(_get_rotato270(black_board, white_board))
    
    return symmetorys

def _get_y(board: int) -> int:
    """
    1. y軸
    """
    # 列ごとに反転する
    mask1 = 0x8080808080808080  # 列1
    mask2 = 0x4040404040404040  # 列2
    mask3 = 0x2020202020202020  # 列3
    mask4 = 0x1010101010101010  # 列4
    mask5 = 0x0808080808080808  # 列5
    mask6 = 0x0404040404040404  # 列6
    mask7 = 0x0202020202020202  # 列7
    mask8 = 0x0101010101010101  # 列8
    
    result_board = 0x0000000000000000
    
    result_board |= (board & mask1) >> 7
    result_board |= (board & mask2) >> 5
    result_board |= (board & mask3) >> 3
    result_board |= (board & mask4) >> 1
    result_board |= (board & mask5) << 1
    result_board |= (board & mask6) << 3
    result_board |= (board & mask7) << 5
    result_board |= (board & mask8) << 7
    
    return result_board
    

def _get_x(board:int) -> int:
    """
    2. x軸
    """
    # 行ごとに反転する
    mask1 = 0xff00000000000000  # 行1
    mask2 = 0x00ff000000000000  # 行2
    mask3 = 0x0000ff0000000000  # 行3
    mask4 = 0x000000ff00000000  # 行4
    mask5 = 0x00000000ff000000  # 行5
    mask6 = 0x0000000000ff0000  # 行6
    mask7 = 0x000000000000ff00  # 行7
    mask8 = 0x00000000000000ff  # 行8
    
    result_board = 0x0000000000000000
    
    result_board |= (board & mask1) >> 56  # 7*8
    result_board |= (board & mask2) >> 40
    result_board |= (board & mask3) >> 24
    result_board |= (board & mask4) >> 8
    result_board |= (board & mask5) << 8
    result_board |= (board & mask6) << 24
    result_board |= (board & mask7) << 40
    result_board |= (board & mask8) << 56
    
    return result_board

def _get_right_z(board:int) -> int:
    """
    3. 右斜め軸
    """
    # 右斜めごとに反転する
    mask1 = 0x8000000000000000  # 斜め1
    mask2 = 0x4080000000000000  # 斜め2
    mask3 = 0x2040800000000000  # 斜め3
    mask4 = 0x1020408000000000  # 斜め4
    mask5 = 0x0810204080000000  # 斜め5
    mask6 = 0x0408102040900000  # 斜め6
    mask7 = 0x0204081020408000  # 斜め7
    
    mask8 = 0x0102040810204080  # 斜め8
    
    mask9 = 0x0001020408102040  # 斜め9
    mask10 = 0x0000010204081020  # 斜め10
    mask11 = 0x0000000102040810  # 斜め11
    mask12 = 0x0000000001020408  # 斜め12
    mask13 = 0x0000000000010204  # 斜め13
    mask14 = 0x0000000000000102  # 斜め14
    mask15 = 0x0000000000000001  # 斜め15
    
    result_board = 0x0000000000000000
    
    result_board |= (board & mask1) >> 63
    result_board |= (board & mask2) >> 54  # 8*6+6
    result_board |= (board & mask3) >> 45  # 8*5+5
    result_board |= (board & mask4) >> 36  # 8*4+4
    result_board |= (board & mask5) >> 27  # 8*3+3
    result_board |= (board & mask6) >> 18  # 8*2+2 
    result_board |= (board & mask7) >> 9  # 8*1+1
    
    result_board |= (board & mask8)
    
    result_board |= (board & mask9) << 9  
    result_board |= (board & mask10) << 18
    result_board |= (board & mask11) << 27
    result_board |= (board & mask12) << 36
    result_board |= (board & mask13) << 45
    result_board |= (board & mask14) << 54
    result_board |= (board & mask15) << 63
    
    return result_board

def _get_left_z(board:int) -> tuple:
    """
    4. 左斜め軸
    """
    # 左斜めごとに反転する
    mask1 = 0x0100000000000000  # 斜め1
    mask2 = 0x0201000000000000  # 斜め2
    mask3 = 0x0402010000000000  # 斜め3
    mask4 = 0x0804020100000000  # 斜め4
    mask5 = 0x1008040201000000  # 斜め5
    mask6 = 0x2010080402010000  # 斜め6
    mask7 = 0x4020100804020100  # 斜め7
    
    mask8 = 0x8040201008040201  # 斜め8
    
    mask9 = 0x0080402010080402  # 斜め9
    mask10 = 0x0000804020100804  # 斜め10
    mask11 = 0x0000008040201008  # 斜め11
    mask12 = 0x0000000080402010  # 斜め12
    mask13 = 0x0000000000804020  # 斜め13
    mask14 = 0x0000000000008040  # 斜め14
    mask15 = 0x0000000000000080  # 斜め15
    
    result_board = 0x0000000000000000
    
    result_board |= (board & mask1) >> 49 # 8*6+1
    result_board |= (board & mask2) >> 42  # 8*5+2
    result_board |= (board & mask3) >> 35  # 8*4+3
    result_board |= (board & mask4) >> 28  # 8*3+4
    result_board |= (board & mask5) >> 21  # 8*2+5
    result_board |= (board & mask6) >> 14  # 8*1+6 
    result_board |= (board & mask7) >> 7  # 8*0+7
    
    result_board |= (board & mask8)
    
    result_board |= (board & mask9) << 7  
    result_board |= (board & mask10) << 14
    result_board |= (board & mask11) << 21
    result_board |= (board & mask12) << 28
    result_board |= (board & mask13) << 35
    result_board |= (board & mask14) << 42
    result_board |= (board & mask15) << 49
    
    return result_board

def _get_rotato90(board:int) -> tuple:
    """
    5. 90度回転
    
    横1列を縦1列に変換して90度回転する
    ex:横0->縦7
    """
    result_board = 0x0000000000000000
    base_mask = 0x8000000000000000
    
    for i in range(8):  # 行
        for j in range(8):  # 列
            mask = base_mask >> (i*8+j)
            move = (-j-i*8) + (7-i) + (j*8)  # (0,0)基点で計算
            if move >=0:
                result_board |= (board & mask) >> move
            else:
                result_board |= (board & mask) << -move
    
    return result_board

def _get_rotato180(board:int) -> tuple:
    """
    6. 180度回転
    """
    # TODO: 効率化できる
    for _ in range(2):
        board = _get_rotato90(board)
    
    return board

def _get_rotato270(board:int) -> tuple:
    """
    7. 270度回転
    """
    # TODO: 効率化できる
    for _ in range(3):
        board = _get_rotato90(board)
    
    return board

def _print_board(board: int):
    """
    debug用
    boardを64桁にして視覚的にprint出力する
    """
    result = format(board, '64b')  # 2進数で64桁で0で穴埋め
    out = "\n"
    for i, value in enumerate(result):
        if int(i)%8==7:
            out += f"{value}\n"
        else:
            out += value
    print(out)