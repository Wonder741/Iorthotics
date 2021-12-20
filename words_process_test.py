import re


def words_process(string_list):
    # find 6 digital number
    result_number = re.findall(r'\d{6}', str(string_list))
    # find non-digital characters
    result_word = re.findall(r'\D+', str(string_list))
    # remove symbols
    result_word = re.findall(r'\w+', str(result_word))
    if result_number:
        print('find order number: ', result_number)
    else:
        print('NOT find order number')
        print('use keyword instead: ', result_word)
    return result_number, result_word


diction = {}
list1 = ['22334', 'rwgrewgw', 'fwfewe', '12/05/21', 'D.Date']
list2 = ['223344', 'rwgrewgw', 'fwfewe', '12/05/21', 'D.Date']
diction[0] = list1
diction[1] = list2

for i in range(len(diction)):
    order_number, order_keyword = words_process(diction[i])
    print(order_number, order_keyword)





