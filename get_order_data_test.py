import csv
import re
import subprocess


def server_check(sc_order_number, sc_csv_path, sc_tool_path):
    args = [sc_tool_path, 'get-order', '-s', 'aus', '-k', '1LpGQMtIo3oHy6D174fmj40p',
            '--order-number', str(sc_order_number), '-f', sc_csv_path, '-q']
    subprocess.call(args)

    sc_order_state = None
    sc_data_list = []

    with open(sc_csv_path) as csvDataFile:
        sc_data = list(csv.reader(csvDataFile))
        # print(sc_data)

        for sc_data_index in range(len(sc_data)):
            # print(sc_data_index)
            sc_data_name = sc_data[sc_data_index][0]
            sc_data_data = sc_data[sc_data_index][1]
            if sc_data_name == 'OrderNumber' and str(sc_data_data) == '00217':
                print("ORDER ID INCORRECT or FAILED to connect server: ", sc_order_number)
                return sc_order_state, sc_data_list
            else:
                if sc_data_name == 'Status':
                    sc_order_state = str(sc_data_data).lower()
                # search for colour information
                if sc_data_name == 'FootOrthotic.finishing.top_covers.cover':
                    sc_data_list.append(str(sc_data_data).lower())
                if sc_data_name == 'FootOrthotic.finishing.top_covers.content':
                    sc_data_list.append(str(sc_data_data).lower())
                if sc_data_name == 'FootOrthotic.finishing.top_covers.color':
                    sc_data_list.append(str(sc_data_data).lower())
                    break
    print('ORDER information found: ', sc_order_number)
    return sc_order_state, sc_data_list


def write_csv(wc_csv_path, wc_number, wc_list):
    data = [wc_number, wc_list]

    with open(wc_csv_path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the data
        writer.writerow(data)


if __name__ == '__main__':
    csv_temp_path = 'C:/Users/iOrthotics/Desktop/Robot/Data/order_export.csv'
    CLI_tool_path = 'C:/Users/iOrthotics/Desktop/Robot/iOrthoticsAPI/roboapi.exe'
    csv_list_path = 'C:/Users/iOrthotics/Desktop/Robot/Data/order_list.csv'


    for i in range(500):
        part_number = 210500 + i
        order_state, order_list = server_check(part_number, csv_temp_path, CLI_tool_path)
        write_csv(csv_list_path, part_number, order_list)
