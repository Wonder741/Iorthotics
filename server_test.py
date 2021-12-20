import csv  # function server_check(order_number)
import subprocess


# Function to check the order id against the server using the CLI tool developed
# Inputs: Order number (Checks for 'cooling')
def server_check(sc_order_number):
    args = ['C:/iOrthotics/iorthoticsserver/roboapi.exe', 'get-order', '-s', 'aus', '-k',
            '1LpGQMtIo3oHy6D174fmj40p', '--order-number', str(sc_order_number), '-f',
            'C:/Google Cloud/ocr_data/order_export.csv', '-q']
    subprocess.call(args)
    with open('C:/Google Cloud/ocr_data/order_export.csv') as csvDataFile:
        sc_data = list(csv.reader(csvDataFile))

        sc_data_colour = None
        sc_data_thick = None
        sc_data_type = None

        # Extract data
        if sc_data[1][1] == 'Yes':
            sc_order_id_flag = True
            sc_order_state = sc_data[8][1]
            for sc_data_index in range(len(sc_data)):
                # search for colour information
                sc_data_name = sc_data[sc_data_index][0]
                if sc_data_name == 'FootOrthotic.finishing.top_covers.color':
                    sc_data_colour = str(sc_data[sc_data_index][1]).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.cover':
                    sc_data_type = str(sc_data[sc_data_index][1]).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.content':
                    sc_data_thick = str(sc_data[sc_data_index][1])
        else:
            sc_order_id_flag = False
            sc_order_state = None
            sc_data_type = None
            sc_data_colour = None
            sc_data_thick = None
            print("\n")
            print("ORDER ID INCORRECT:", sc_order_number)
        return sc_order_id_flag, sc_order_state, sc_data_type, sc_data_colour, sc_data_thick


a, b, c, d, e = server_check('Schurmann')
print(a, '\n', b, '\n', c, '\n', d, '\n', e)
