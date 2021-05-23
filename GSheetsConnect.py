# I Used this article - https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
import pygsheets

spread_sheet_key = '1x-sH24tHATDshSmXs07gDzb7DETyiEfiLH6shMn8Vzc'
client_secret = 'google_auth_files/client_secret.json'


def write_vacancy_data_2_google_sheet(vacancy_title, company_title, company_link, vacancy_title_link, date, icon_link,
                                      low_salary, high_salary, currency):
    gc = pygsheets.authorize(client_secret=client_secret)
    sh = gc.open_by_key(spread_sheet_key)
    work_sheet_data_base = sh[0]
    list_of_matches = work_sheet_data_base.find(vacancy_title_link, matchEntireCell=True)
    if list_of_matches:
        print(f"Найден дубликат - {list_of_matches}")
    if not list_of_matches:
        print("Добавляю новую вакансию в табличку")
        work_sheet_data_base.insert_rows(row=1)
        work_sheet_data_base.update_value(f'A2', f'{vacancy_title}')
        work_sheet_data_base.update_value(f'B2', f'{company_title}')
        work_sheet_data_base.update_value(f'C2', f'{company_link}')
        work_sheet_data_base.update_value(f'D2', f'{vacancy_title_link}')
        work_sheet_data_base.update_value(f'E2', f'{date}')
        work_sheet_data_base.update_value(f'F2', f'{icon_link}')
        work_sheet_data_base.update_value(f'G2', f'{low_salary}')
        work_sheet_data_base.update_value(f'H2', f'{high_salary}')
        work_sheet_data_base.update_value(f'I2', f'{currency}')
