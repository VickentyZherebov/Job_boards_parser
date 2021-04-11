from bs4 import BeautifulSoup
import csv
import requests
import datetime
import re

url = 'https://career.habr.com/vacancies'

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/88.0.4324.192 Safari/537.36',
    'accept': '*/*'}
host = 'https://career.habr.com'

page_number = 1
req = requests.get(url + f'?page={page_number}&q=senior&remote=true&type=all', headers=headers)

src = req.text
dmy = datetime.datetime.today().strftime("%d_%m_%Y")
hms = datetime.datetime.today().strftime("%H_%M_%S")
with open(f"vacancies_{dmy}_{hms}.csv", 'w', encoding='utf-8') as file:
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

if isinstance(no_content_title, type(None)):
    for item in range(1, 7):
        print(f'Парсим страницу выдачи с номером {page_number}')
        print('__________________________________________________')
        req = requests.get(url + f'?page={page_number}&q=senior&remote=true&type=all', headers=headers)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')
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
            low_salary = ''
            high_salary = ''
            currency = ''
            if re.search('от', salary):  # проверяем в зепке наличие слова "от "
                first_split = re.split('от ', salary)  # чистим строку от слова "от "
                if re.search('до', first_split[1]):  # проверяем в цене наличие слова "До ", если есть, то:
                    second_split = re.split(' до ', first_split[1])  # отрезаем слово "До "
                    if re.search('₽', second_split[1]):  # Если находим символ рубля, то:
                        currency = 'rub'
                        low_salary = second_split[0].replace(' ', '')
                        high_salary = re.split(' ₽', second_split[1])[0].replace(' ', '')
                        print(f'Нижнее значение вилки равно {low_salary}')
                        print(f'Верхнее значение вилки равно {high_salary}')
                        print(f'Валюта зепки равна {currency}')
                        print('__________________________________________________')
                    else:
                        if re.search('\\$', second_split[1]):  # Если находим символ рубля, то:
                            currency = 'usd'
                            low_salary = second_split[0].replace(' ', '')
                            high_salary = re.split(' \\$', second_split[1])[0].replace(' ', '')
                            print(f'Нижнее значение вилки равно {low_salary}')
                            print(f'Верхнее значение вилки равно {high_salary}')
                            print(f'Валюта зепки равна {currency}')
                            print('__________________________________________________')
                        else:
                            if re.search('€', second_split[1]):  # Если находим символ евро, то:
                                currency = 'eur'
                                low_salary = second_split[0].replace(' ', '')
                                high_salary = re.split(' €', second_split[1])[1].replace(' ', '')
                                print(f'Нижнее значение вилки равно {low_salary}')
                                print(f'Верхнее значение вилки равно {high_salary}')
                                print(f'Валюта зепки равна {currency}')
                                print('__________________________________________________')
                            else:
                                print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
                                print('_____________________________________________')
                else:
                    if re.search('₽', first_split[1]):
                        currency = 'rub'
                        low_salary = re.split(' ₽', first_split[1])[0].replace(' ', '')
                        print(f'Нижнее значение вилки равно {low_salary}')
                        print(f'Верхнее значение вилки не указано')
                        print(f'Валюта зепки равна {currency}')
                        print('__________________________________________________')
                    else:
                        if re.search('\\$', first_split[1]):
                            currency = 'usd'
                            low_salary = re.split(' \\$', first_split[1])[0].replace(' ', '')
                            print(f'Нижнее значение вилки равно {low_salary}')
                            print(f'Верхнее значение вилки не указано')
                            print(f'Валюта зепки равна {currency}')
                            print('__________________________________________________')
                        else:
                            if re.search('€', first_split[1]):
                                currency = 'eur'
                                low_salary = re.split(' €', first_split[1])[0].replace(' ', '')
                                print(f'Нижнее значение вилки равно {low_salary}')
                                print(f'Верхнее значение вилки не указано')
                                print(f'Валюта зепки равна {currency}')
                                print('__________________________________________________')
                            else:
                                print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
            else:
                if re.search('До ', salary):
                    first_split = re.split('До ', salary)
                    if re.search('₽', first_split[1]):
                        low_salary = 'не указано'
                        currency = 'rub'
                        high_salary = re.split(' ₽', first_split[1])[0].replace(' ', '')
                        print(f'Нижнее значение вилки равно {low_salary}')
                        print(f'Верхнее значение вилки равно {high_salary}')
                        print(f'Валюта зепки равна {currency}')
                        print('__________________________________________________')
                    else:
                        if re.search('\\$', first_split[1]):
                            low_salary = 'не указано'
                            currency = 'usd'
                            high_salary = re.split(' \\$', first_split[1])[0].replace(' ', '')
                            print(f'Нижнее значение вилки равно {low_salary}')
                            print(f'Верхнее значение вилки равно {high_salary}')
                            print(f'Валюта зепки равна {currency}')
                            print('__________________________________________________')
                        else:
                            if re.search('€', first_split[1]):
                                low_salary = 'не указано'
                                currency = 'usd'
                                high_salary = re.split(' €', first_split[1])[0].replace(' ', '')
                                print(f'Нижнее значение вилки равно {low_salary}')
                                print(f'Верхнее значение вилки равно {high_salary}')
                                print(f'Валюта зепки равна {currency}')
                                print('__________________________________________________')
                else:
                    low_salary = 'нет значения'
                    high_salary = 'нет значения'
                    print(f'Нижнее значение вилки равно {low_salary}')
                    print(f'Верхнее значение вилки равно {high_salary}')
                    print('__________________________________________________')
            skills_all = []
            skills_max_value = 0
            skill_elements = data.find('div', class_='vacancy-card__skills').find_all('span', 'preserve-line')
            for skill_element in skill_elements:
                skill_element = skill_element.find('a', class_='link-comp link-comp--appearance-dark').text
                skills_all.append(skill_element)
                if skills_max_value < len(skills_all):
                    skills_max_value = len(skill_element)
            with open(f'vacancies_{dmy}_{hms}.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([title, company_title, company_link, title_link, date, icon_link, low_salary,
                                 high_salary, currency])
        print(f'закончил парсить страницу с номером = {page_number}')
        print('____________________________________________________')
        page_number = page_number + 1
else:
    print('finish')
