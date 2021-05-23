from timevars import find_time
import csv
import os
import platform
import subprocess

day_month_year = find_time()[0]
hour_minute_second = find_time()[1]
csv_name = f"vacancies_{day_month_year}_{hour_minute_second}.csv"


def make_csv_file(dmy=day_month_year, csv_n=csv_name):
    if not os.path.exists(f'scrapped_data/{day_month_year}'):
        os.mkdir(f'scrapped_data/{day_month_year}')
    with open(f'scrapped_data/{dmy}/{csv_n}', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Название вакансии",
                         'Название компании',
                         'Ссылка на компанию',
                         'Ссылка на вакансию',
                         'Дата открытия вакансии',
                         'Ссылка на логотип',
                         'Нижнее значение вилки',
                         'Верхнее значение вилки',
                         'Валюта'])


def write_vacancies_2_csv_file(vacancy_title, company_title, company_link, title_link, date, icon_link, low_salary,
                               high_salary, currency):
    with open(f'scrapped_data/{day_month_year}/vacancies_{day_month_year}_{hour_minute_second}.csv', 'a',
              encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([vacancy_title, company_title, company_link, title_link, date, icon_link, low_salary,
                         high_salary, currency])


def open_csv_file():
    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', f'scrapped_data/{day_month_year}/{csv_name}'))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(f'scrapped_data/{day_month_year}/{csv_name}')
    else:  # linux variants
        subprocess.call(['xdg-open', f'scrapped_data/{day_month_year}/{csv_name}'])
