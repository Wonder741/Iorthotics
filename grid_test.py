import tkinter as tk  # function display_grid()


# Function to display matched order id or order key word on computer
# Inputs: order_diction
def display_grid(order_diction):
    root = tk.Tk()
    root.title("Sorted Grid")
    cols = ["", "A", "B", "C", "D", "E", "F", "G"]
    rows = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    od_index = 0

    for grid_i in range(11):
        for grid_j in range(8):
            if grid_i == 0:
                tk.Label(root, relief='groove', height=2, width=10,
                         text=cols[grid_j]).grid(row=grid_i, column=grid_j, sticky='NSEW')
            elif grid_j == 0:
                tk.Label(root, relief='groove', height=2, width=10,
                         text=rows[grid_i]).grid(row=grid_i, column=grid_j, sticky='NSEW')
            else:
                filled_words = str(order_diction[od_index]['order_id']) + '\n' + \
                               str(order_diction[od_index]['keyword_1']) + '\n' + \
                               str(order_diction[od_index]['keyword_2']) + '\n' + \
                               str(order_diction[od_index]['keyword_3'])
                tk.Label(root, bg="white", height=4, width=12, relief='ridge',
                         text=filled_words).grid(row=grid_i, column=grid_j, sticky='NSEW')
                od_index = od_index + 1
    root.mainloop()


def build_diction(part_count):
    if part_count > 70:
        part_count = 70
    diction = {}
    for diction_index in range(part_count):
        diction[diction_index] = {'location': diction_index, 'order_id': str(223344 + diction_index),
                                  'pair_found': False, 'keyword_1': 'a', 'keyword_2': 'b', 'keyword_3': 'c'}
    return diction


d = build_diction(70)
display_grid(d)
