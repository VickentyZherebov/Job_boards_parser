import time

from bs4 import BeautifulSoup
import random
import csv
import requests

url = 'https://career.habr.com/vacancies'

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/88.0.4324.192 Safari/537.36',
    'accept': '*/*'}
host = 'https://career.habr.com'

page_number = 1
req = requests.get(url + f'/?page={page_number}&salary=350000&type=all', headers=headers)

src = req.text
# print(src)
with open('vacancies.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Название вакансии",
                     'Название компании',
                     'Ссылка на компанию',
                     'Ссылка на вакансию',
                     'Дата открытия вакансии',
                     'Ссылка на логотип',
                     "Вилка"])

soup = BeautifulSoup(src, 'lxml')
vacancy_card = soup.find_all(class_='vacancy-card')
no_content_title = soup.find(class_='no-content__title')
if isinstance(no_content_title, type(None)):
    for item in range(1, 10):
        print(f'Парсим страницу выдачи с номером {page_number}')
        req = requests.get(url + f'?page={page_number}&salary=350000&type=all', headers=headers)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')
        vacancy_card = soup.find_all(class_='vacancy-card')
        no_content_title = soup.find(class_='no-content__title')
        for item in vacancy_card:
            title = item.find('a', class_='vacancy-card__title-link').text
            company_title = item.find('a', class_='link-comp link-comp--appearance-dark').text
            company_link = host + item.find('a', class_='link-comp link-comp--appearance-dark').get('href')
            title_link = host + item.find('a', class_='vacancy-card__title-link').get('href')
            date = item.find('div', class_='vacancy-card__date').find('time', class_='basic-date').text.strip()
            icon_link = item.find('a', class_='vacancy-card__icon-link').find('img', 'vacancy-card__icon').get('src')
            salary = item.find('div', class_='basic-salary').text
            skills_all = []
            skills_max_value = 0
            skill_elements = item.find('div', class_='vacancy-card__skills').find_all('span', 'preserve-line')
            for skill_element in skill_elements:
                skill_element = skill_element.find('a', class_='link-comp link-comp--appearance-dark').text
                skills_all.append(skill_element)
                if skills_max_value < len(skills_all):
                    skills_max_value = len(skill_element)
            with open('vacancies.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([title, company_title, company_link, title_link, date, icon_link, salary])
        print(f'закончил парсить страницу с номером = {page_number}')
        page_number = page_number + 1
else:
    print('finish')
