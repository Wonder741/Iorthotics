from sys_setup import build_diction, write_csv, words_process, display_grid


def diction_fill_up(df_diction, df_part_index, df_part_number, df_part_keyword, df_order_flag):
    df_diction_index = 0
    if df_order_flag:
        for df_diction_index in range(df_part_index + 1):
            if df_diction[df_diction_index]['order_id'] == df_part_number \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['pair_found'] = True
                df_diction[df_diction_index]['source'] = 'IN'
                df_diction[df_diction_index]['keyword_2'] = df_part_keyword
                print('TWO internal parts paired at position: ', df_diction_index)
                break
            if df_diction[df_diction_index]['order_id'] != df_part_number \
                    and not df_diction[df_diction_index]['location_placed'] \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['order_id'] = df_part_number
                df_diction[df_diction_index]['keyword_1'] = df_part_keyword
                df_diction[df_diction_index]['location_placed'] = True
                df_diction[df_diction_index]['source'] = 'IN'
                print('Single internal part placed at position: ', df_diction_index)
                break
    else:
        for df_diction_index in range(df_part_index + 1):
            if df_diction[df_diction_index]['keyword_1'] == df_part_keyword \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['pair_found'] = True
                df_diction[df_diction_index]['source'] = 'EX'
                df_diction[df_diction_index]['keyword_2'] = df_part_keyword
                print('TWO external parts paired at position: ', df_diction_index)
                break
            if df_diction[df_diction_index]['keyword_1'] != df_part_keyword \
                    and not df_diction[df_diction_index]['location_placed'] \
                    and not df_diction[df_diction_index]['pair_found']:
                df_diction[df_diction_index]['keyword_1'] = df_part_keyword
                df_diction[df_diction_index]['location_placed'] = True
                df_diction[df_diction_index]['source'] = 'EX'
                print('Single internal part placed at position: ', df_diction_index)
                break
    print("Diction filled")
    return df_diction, df_diction_index


if __name__ == '__main__':
    part = {0: ['A', 'Data', '213055', '12/21'],
            1: ['B', 'Soda', '213122', '12/21'],
            2: ['C', 'Soda', '213068', '12/21'],
            3: ['A', 'Data', '213055', '12/2'],
            4: ['A', 'Quequester', '2131001', '12/21'],
            5: ['A', 'Quequester', '2131001', '12/21'],
            6: ['O', 'Bestball', 'Sydney', 'Clinic', '2526'],
            7: ['S', 'Happy', 'Sydney', 'Clinic', '1322'],
            8: ['B', 'Gates', 'My', 'podiatry', 'Foot', '12/12/21'],
            9: ['C', 'Xrismas', 'Myfoot', 'Dr'],
            10: ['Z', 'Peter', 'AFO', 'MyfootDr', '213150', '12/21'],
            11: ['C', 'Xrismas', 'MyfootDr'],
            12: ['B', 'soda', '213122', '12/21'],
            13: ['C', 'Soda', '213068', '12/21'],
            14: ['o', 'Bestball', 'Sydney', 'Clinic', '2526'],
            15: ['S', 'Happy', 'Sydney', 'Clinic', '1322'],
            16: ['B', 'Gates', 'My', 'podiatry', 'Foot', '12/12/21'],
            17: ['C', 'Xrismas', 'MyfootDr']}
    pair_diction = build_diction()
    order_id_flag = [True, True, True, True, True, True, False, False, False, False,
                     True, False, True, True, False, False, False, False]
    place_position = {}

    for part_index in range(len(part)):
        ocr_text = part[part_index]
        print(ocr_text)
        write_csv(part_index, ocr_text)
        part_number, part_keyword = words_process(ocr_text)
        pair_diction, place_position[part_index] = diction_fill_up(pair_diction, part_index, part_number,
                                                                   part_keyword, order_id_flag[part_index])
    print(place_position)
    display_grid(pair_diction)
