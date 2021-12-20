import csv


def write_csv(image_name, csv_orc_words):
    data = [image_name, csv_orc_words]

    with open('C:/Google Cloud/ocr_data/countries.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the data
        writer.writerow(data)


image = '222222222'
csv_words = ['223344', 'bb', 'cc', 'dd']
write_csv(image, csv_words)
