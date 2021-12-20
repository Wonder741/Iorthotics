import csv  # function server_check(order_number)
import subprocess


# Function to check the order id against the server using the CLI tool developed
# Inputs: Order number (Checks for 'cooling')
def server_check(sc_order_number, sc_csv_path, sc_tool_path):
    args = [sc_tool_path, 'get-order', '-s', 'aus', '-k', '1LpGQMtIo3oHy6D174fmj40p',
            '--order-number', str(sc_order_number), '-f', sc_csv_path, '-q']
    subprocess.call(args)
    with open(sc_csv_path) as csvDataFile:
        sc_data = list(csv.reader(csvDataFile))

        sc_order_state = None
        sc_data_colour = None
        sc_data_thick = None
        sc_data_type = None
        for sc_data_index in range(len(sc_data)):
            sc_data_name = sc_data[sc_data_index][0]
            sc_data_data = sc_data[sc_data_index][1]
            if sc_data_name == 'OrderNumber' and str(sc_data_data) == '00217':
                sc_order_id_flag = False
                print("ORDER ID INCORRECT:", sc_order_number)
                return sc_order_id_flag, sc_order_state, sc_data_type, sc_data_colour, sc_data_thick
            else:
                if sc_data_name == 'Status':
                    sc_order_state = str(sc_data_data).lower()
                # search for colour information
                if sc_data_name == 'FootOrthotic.finishing.top_covers.color':
                    sc_data_colour = str(sc_data_data).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.cover':
                    sc_data_type = str(sc_data_data).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.content':
                    sc_data_thick = str(sc_data_data).lower()
    sc_order_id_flag = True
    print('ORDER ID found: ', sc_order_number)
    return sc_order_id_flag, sc_order_state, sc_data_type, sc_data_colour, sc_data_thick


csv_temp_path = 'C:/Google Cloud/ocr_data/order_export.csv'
# path for server check tool
CLI_tool_path = 'C:/iOrthotics/iorthoticsserver/roboapi.exe'
a, b, c, d, e = server_check('xxx', csv_temp_path, CLI_tool_path)
print(a, '\n', b, '\n', c, '\n', d, '\n', e)
