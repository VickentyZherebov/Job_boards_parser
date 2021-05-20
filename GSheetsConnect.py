# I Used this article - https://medium.com/game-of-data/play-with-google-spreadsheets-with-python-301dd4ee36eb
import pygsheets


SpreadSheetKey = '1x-sH24tHATDshSmXs07gDzb7DETyiEfiLH6shMn8Vzc'
ClientSecret = 'client_secret_1048929673010-2ntibj9akn66p7883in6n0gok8ssqf36.apps.googleusercontent.com.json'

# def FindVacansyTitleDublicate(vacancy_title):
#     gc = pygsheets.authorize(ClientSecret)
#     sh = gc.open_by_key(SpreadSheetKey)
#     WorkSheetDataBase = sh[0]
#     WorkSheetDataBase.find(vacancy_title, )


def WriteVacansyTitle(vacancy_title, company_title, company_link, title_link, date, icon_link, low_salary, high_salary, currency):
    gc = pygsheets.authorize(ClientSecret)
    sh = gc.open_by_key(SpreadSheetKey)
    WorkSheetDataBase = sh[0]
    LastRowNumber = WorkSheetDataBase.rows
    ListOfMatches = WorkSheetDataBase.find(vacancy_title, matchEntireCell=True)
    if ListOfMatches:
        print(f"Найден дубликат - {ListOfMatches}")
    if not ListOfMatches:
        print("Добавляю новую вакансию в табличку")
        WorkSheetDataBase.add_rows(1)
        WorkSheetDataBase.update_value(f'A{LastRowNumber + 1}', f'{vacancy_title}')
        WorkSheetDataBase.update_value(f'B{LastRowNumber + 1}', f'{company_title}')
        WorkSheetDataBase.update_value(f'C{LastRowNumber + 1}', f'{company_link}')
        WorkSheetDataBase.update_value(f'D{LastRowNumber + 1}', f'{title_link}')
        WorkSheetDataBase.update_value(f'E{LastRowNumber + 1}', f'{date}')
        WorkSheetDataBase.update_value(f'F{LastRowNumber + 1}', f'{icon_link}')
        WorkSheetDataBase.update_value(f'G{LastRowNumber + 1}', f'{low_salary}')
        WorkSheetDataBase.update_value(f'H{LastRowNumber + 1}', f'{high_salary}')
        WorkSheetDataBase.update_value(f'I{LastRowNumber + 1}', f'{currency}')
