from env_v2.symmetory.symmetory import (
    get_symmetory_for_anality_batch, _get_y, _get_x, _get_right_z, _get_left_z,
    _get_rotato90, _get_rotato180, _get_rotato270)
def _get_old_sym(bb, wb):
    return get_symmetory_for_anality_batch(bb, wb)

def _get_new_sym(bb, wb):
    sym_black_board = bb
    sym_white_board = wb
    # 1. get_y
    tmp_black_board = _get_y(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_y(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_y(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 2. get_x
    tmp_black_board = _get_x(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_x(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_x(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 3. _get_right_z
    tmp_black_board = _get_right_z(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_right_z(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_right_z(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 4. _get_left_z
    tmp_black_board = _get_left_z(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_left_z(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_left_z(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 5. _get_rotato90
    tmp_black_board = _get_rotato90(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_rotato90(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_rotato90(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 6. _get_rotato180
    tmp_black_board = _get_rotato180(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_rotato180(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_rotato180(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    # 7. _get_rotato270
    tmp_black_board = _get_rotato270(bb)
    if tmp_black_board < sym_black_board:
        sym_black_board = tmp_black_board
        sym_white_board = _get_rotato270(wb)
    elif tmp_black_board == sym_black_board:
        tmp_white_board = _get_rotato270(wb)
        if tmp_white_board < sym_white_board:
            sym_black_board = tmp_black_board
            sym_white_board = tmp_white_board
    
    return sym_black_board, sym_white_board


bb=34697379840
wb=18374969127327302401

new_bb, new_wb = _get_old_sym(bb, wb)
print("---古い対称性---")
print("黒: ", new_bb)
print("白: ", new_wb)
new_bb, new_wb = _get_new_sym(bb, wb)
print("---新しい対称性---")
print("黒: ", new_bb)
print("白: ", new_wb)