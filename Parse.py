import csv
import os
import platform
import subprocess
import requests
from bs4 import BeautifulSoup
from ParsePagesCount import find_number_of_search_pages
from SalaryRegexp import salary_re_max, salary_re_min, salary_re_cur
from timevars import dmyhms
from selenium import webdriver

chromedriver = '/Users/vikentijzerebov/Downloads/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)

url = 'https://career.habr.com/vacancies'
page_number = 1
question = 'Senior'
remote = 'true'
request_type = 'all'
salary = '380000'
with_salary = "true"

dmy = dmyhms()[0]
hms = dmyhms()[1]
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.128 Safari/537.36',
    'accept': '*/*'}
host = 'https://career.habr.com'

req = requests.get(url + f'?page={page_number}&q={question}&remote={remote}&type={request_type}', headers=headers)
src = req.text
csv_name = f"vacancies_{dmy}_{hms}.csv"
if not os.path.exists(f'{dmy}'):
    os.mkdir(f'{dmy}')

with open(f'{dmy}/{csv_name}', 'w', encoding='utf-8') as file:
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

soup = BeautifulSoup(src, 'lxml')
vacancy_card = soup.find_all(class_='vacancy-card')
no_content_title = soup.find(class_='no-content__title')

number_of_search_pages = find_number_of_search_pages(self=None, pn=page_number, q=question, r=remote, u=url, s=salary,
                                                     ws=with_salary)

for item in range(1, number_of_search_pages + 1):
    print(f'Парсим страницу выдачи с номером {page_number}')
    print('__________________________________________________')
    browser.get(url + f'?page={page_number}&q={question}&remote={remote}&salary={salary}&type={request_type}'
                      f'&with_salary={with_salary}')
    print('Анализирую HTML код')
    required_html = browser.page_source
    soup = BeautifulSoup(required_html, 'html5lib')
    vacancy_card = soup.find_all(class_='vacancy-card')
    no_content_title = soup.find(class_='no-content__title')
    for data in vacancy_card:
        title = data.find('a', class_='vacancy-card__title-link').text
        company_title = data.find('a', class_='link-comp link-comp--appearance-dark').text
        company_link = host + data.find('a', class_='link-comp link-comp--appearance-dark').get('href')
        title_link = host + data.find('a', class_='vacancy-card__title-link').get('href')
        date = data.find('div', class_='vacancy-card__date').find('time', class_='basic-date').text.strip()
        icon_link = data.find('a', class_='vacancy-card__icon-link').find('img', 'vacancy-card__icon').get('src')
        salary = data.find('div', class_='basic-salary').text
        low_salary = salary_re_min(salary)
        high_salary = salary_re_max(salary)
        currency = salary_re_cur(salary)
        skills_all = []
        skills_max_value = 0
        skill_elements = data.find('div', class_='vacancy-card__skills').find_all('span', 'preserve-line')
        for skill_element in skill_elements:
            skill_element = skill_element.find('a', class_='link-comp link-comp--appearance-dark').text
            skills_all.append(skill_element)
            if skills_max_value < len(skills_all):
                skills_max_value = len(skill_element)
        with open(f'{dmy}/vacancies_{dmy}_{hms}.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([title, company_title, company_link, title_link, date, icon_link, low_salary,
                             high_salary, currency])
    print(f'закончил парсить страницу с номером = {page_number}')
    print('____________________________________________________')
    page_number = page_number + 1

if platform.system() == 'Darwin':       # macOS
    subprocess.call(('open', f'{dmy}/{csv_name}'))
elif platform.system() == 'Windows':    # Windows
    os.startfile(f'{dmy}/{csv_name}')
else:                                   # linux variants
    subprocess.call(['xdg-open', f'{dmy}/{csv_name}'])
