from bs4 import BeautifulSoup
from selenium import webdriver
import re
import math
from GSheetsConnect import write_vacancy_data_2_google_sheet
from WorkWithCSV import write_vacancies_2_csv_file
from SalaryRegexp import find_high_salary_value, find_lower_salary_value, find_salary_currency

chromedriver = 'selenium_files/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)

url = 'https://career.habr.com/vacancies'
question = ''
remote = 'true'
request_type = 'all'
salary_price = '350000'
with_salary = "true"
page_number = 1
qid = 5  # 1 - любая, 2 - intern, 3 - junior, 4 - middle, 5 - senior, 6 - lead
vacancy_card = []
host = 'https://career.habr.com'


def find_number_of_search_pages(pn=1, q=question, r=remote, s=salary_price, ws=with_salary, u=url, rt="all", level=qid):
    """ Функция ищет количество страниц в поисковой выдаче с https://career.habr.com/vacancies
    для того, чтобы знать точное количество страниц для парсинга
    :param level:
    :param s:
    :param ws:
    :param u: урл
    :param pn: номер страницы с которой сдирается html код
    :param q: любой поисковой запрос на сайте, для поиска вакансий
    :param r: remote - можно работать удаленно? Если да, то пиши значение true
    :param rt: я хз че это такое, постоянно стоит all
    :return: Количество страниц с вакансиями, соответствующих запросу
    """
    print('Отправляю поисковой запрос на Хабр')
    browser.get(u + f'?page={pn}&q={q}&remote={r}&salary={s}&type={rt}&with_salary={ws}&qid={level}')
    print(f'Взял HTML код для парсинга со страницы {pn}')
    required_html = browser.page_source
    soup = BeautifulSoup(required_html, 'html5lib')
    find_class = "search-total disable-font-boosting search-total--appearance-search-panel"
    print(f'Ищу строку с количеством вакансий')
    find_count_string = soup.find('div', class_=find_class).text
    find_count_string = int(re.findall('\\d+', find_count_string)[0])
    print(f'Твоему запросу соответстует {find_count_string} вакансий')
    number_of_search_pages = math.ceil(int(find_count_string) / 25)
    print(f'Это {number_of_search_pages} страниц надо спарсить, но не парься, я скоро все сделаю')
    return number_of_search_pages


def get_data_by_search_page(day_month_year, hour_minute_second, pn, q=question, r=remote, s=salary_price,
                            ws=with_salary, u=url, t=request_type):
    """ Функция сохраняет html код страницы и возвращает переменную soup в которой содержится html код страницы.
    :param day_month_year:
    :param hour_minute_second:
    :param s: salary - зарплата
    :param ws: with_salary - указана ли зарплата
    :param u: урл
    :param pn: номер страницы с которой сдирается html код
    :param q: любой поисковой запрос на сайте, для поиска вакансий
    :param r: можно ли работать удаленно? Если да, то пиши значение true
    :param t: я хз че это такое, постоянно стоит all
    :return: Количество страниц с вакансиями, соответствующих запросу
    """
    browser.get(u + f'?page={pn}&q={q}&remote={r}&salary={s}&type={t}&with_salary={ws}')
    required_html = browser.page_source
    soup = BeautifulSoup(required_html, 'html5lib')
    html_name = f"html_{pn}_{day_month_year}_{hour_minute_second}.html"
    html_file = open(f'scrapped_data/{day_month_year}/{html_name}', 'w')
    html_file.write(f'{soup}')
    return soup


def collecting_vacancies_data(day_month_year, hour_minute_second, number_of_search_pages, pn=page_number):
    for item in range(1, number_of_search_pages + 1):
        print(f'Парсим страницу выдачи с номером {pn}')
        print('__________________________________________________')
        soup = get_data_by_search_page(day_month_year=day_month_year, hour_minute_second=hour_minute_second,
                                       pn=pn)
        vacancy_card.extend(soup.find_all(class_='vacancy-card'))
        print(len(vacancy_card))
        print(f'закончил парсить страницу с номером = {pn}')
        print('____________________________________________________')
        pn = pn + 1
    return vacancy_card


def parse_vacancies_data(vacancy_cards):
    for data in vacancy_cards:
        vacancy_title = data.find('a', class_='vacancy-card__title-link').text
        company_title = data.find('a', class_='link-comp link-comp--appearance-dark').text
        company_link = host + data.find('a', class_='link-comp link-comp--appearance-dark').get('href')
        title_link = host + data.find('a', class_='vacancy-card__title-link').get('href')
        date = data.find('div', class_='vacancy-card__date').find('time', class_='basic-date').text.strip()
        icon_link = data.find('a', class_='vacancy-card__icon-link').find('img', 'vacancy-card__icon').get('src')
        salary = data.find('div', class_='basic-salary').text
        low_salary = find_lower_salary_value(salary)
        high_salary = find_high_salary_value(salary)
        currency = find_salary_currency(salary)
        # skills_all = []
        # skills_max_value = 0
        # skill_elements = data.find('div', class_='vacancy-card__skills').find_all('span', 'preserve-line')
        # for skill_element in skill_elements:
        #     skill_element = skill_element.find('a', class_='link-comp link-comp--appearance-dark').text
        #     skills_all.append(skill_element)
        #     if skills_max_value < len(skills_all):
        #         skills_max_value = len(skill_element)
        write_vacancies_2_csv_file(vacancy_title=vacancy_title, company_title=company_title, company_link=company_link,
                                   title_link=title_link, date=date, icon_link=icon_link, low_salary=low_salary,
                                   high_salary=high_salary, currency=currency)
        write_vacancy_data_2_google_sheet(vacancy_title, company_title, company_link, title_link, date, icon_link,
                                          low_salary, high_salary, currency)
