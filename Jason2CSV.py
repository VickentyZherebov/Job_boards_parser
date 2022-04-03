import pandas as pd
from datetime import datetime

now = datetime.now()
current_date = f'{now.day}_{now.month}_{now.year}_{now.hour}_{now.minute}_{now.second}'

# pd.set_option('display.max_columns', 50)  # display columns
# df = pd.read_json(r'/Users/vikentijzerebov/PycharmProjects/Job_Boards_Parser/SavedData/JsonFiles/parsed_hh_companies_28_12_2021_13_25_45.json')
# df.to_csv("hh_banks.csv")


class Converter:
    """Преобразовывает json файл в CSV, кодировка utf-8, разделитель - запятая"""
    def __init__(self,
                 file_name,
                 json_file_path,
                 csv_file_path='/Users/vikentijzerebov/PycharmProjects/Job_Boards_Parser/SavedData/CSVFiles/',
                 date=current_date):
        self.file_name = file_name
        self.csv_file_path = csv_file_path
        self.json_file_path = json_file_path
        self.date = date

    def convert_json_to_csv(self):
        pd.set_option('display.max_columns', 50)
        df = pd.read_json(self.json_file_path)
        df.to_csv(f'{self.csv_file_path}{self.file_name}_{self.date}.csv')
