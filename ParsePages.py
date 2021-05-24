from bs4 import BeautifulSoup
from selenium import webdriver
import re
import math
from GSheetsConnect import write_vacancy_data_2_google_sheet
# from WorkWithCSV import write_vacancies_2_csv_file
from SalaryRegexp import find_high_salary_value, find_lower_salary_value, find_salary_currency

chromedriver = 'selenium_files/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)


class Vacancy:
    def __init__(self,
                 vacancy_title,
                 company_title,
                 company_link,
                 title_link,
                 date,
                 icon_link,
                 salary,
                 low_salary,
                 high_salary,
                 currency
                 ):
        self.vacancy_title = vacancy_title
        self.company_title = company_title
        self.company_link = company_link
        self.title_link = title_link
        self.date = date
        self.icon_link = icon_link
        self.salary = salary
        self.low_salary = low_salary
        self.high_salary = high_salary
        self.currency = currency
        # todo init properties
        # todo функции для сохранения в гугл таблицы + csv (отдельные)
        # todo убрать все ненужное


class HabrPage:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def find_number_of_vacancies(self) -> int:
        """ Функция ищет количество вакансий, соответствующих поисковому запросу
        :return: Количество вакансий, соответствующих запросу
        """
        find_count_string = self.soup \
            .find('div', class_="search-total disable-font-boosting search-total--appearance-search-panel") \
            .text
        number_of_vacancies = int(re.findall('\\d+', find_count_string)[0])
        return number_of_vacancies

    def find_number_of_search_pages(self) -> int:
        """ Функция ищет количество страниц, соответствующих поисковому запросу
        :return: Количество страниц с вакансиями, соответствующих запросу
        """
        number_of_vacancies = self.find_number_of_vacancies()
        number_of_search_pages = math.ceil(number_of_vacancies / 25)
        return number_of_search_pages

    def find_vacancies(self) -> [Vacancy]:
        base_url: str = 'https://career.habr.com'
        vacancy_cards = self.soup.find_all(class_='vacancy-card')
        vacancies = []
        for vacancy_card in vacancy_cards:
            salary = vacancy_card.find('div', class_='basic-salary').text
            vacancy = Vacancy(vacancy_title=vacancy_card.find('a', class_='vacancy-card__title-link').text,
                              company_title=vacancy_card.find('a', class_='link-comp link-comp--appearance-dark').text,
                              company_link=base_url + vacancy_card.find(
                                  'a', class_='link-comp link-comp--appearance-dark').get('href'),
                              title_link=base_url + vacancy_card.find(
                                  'a', class_='vacancy-card__title-link').get('href'),
                              date=vacancy_card.find(
                                  'div', class_='vacancy-card__date').find(
                                  'time', class_='basic-date').text.strip(),
                              icon_link=vacancy_card.find(
                                  'a', class_='vacancy-card__icon-link').find(
                                  'img', 'vacancy-card__icon').get(
                                  'src'),
                              salary=salary, low_salary=find_lower_salary_value(salary),
                              high_salary=find_high_salary_value(salary),
                              currency=find_salary_currency(salary)
                              )
            vacancies.append(vacancy)
        return vacancies


class HabrClient:
    def __init__(self, url: str = 'https://career.habr.com/vacancies'):
        self.url = url

    def get_page(self, page_number: int = 1, search_query='', remote='true', salary_price='400000',
                 with_salary='true', request_type='all') -> HabrPage:
        """ Функция сохраняет html код страницы и возвращает переменную soup в которой содержится html код страницы.
        :param salary_price: salary - зарплата
        :param with_salary: with_salary - указана ли зарплата
        :param page_number: номер страницы с которой сдирается html код
        :param search_query: любой поисковой запрос на сайте, для поиска вакансий
        :param remote: можно ли работать удаленно? Если да, то пиши значение true
        :param request_type: я хз че это такое, постоянно стоит all
        :return: # todo
        """
        browser.get('https://career.habr.com/vacancies' +
                    f'?page={page_number}'
                    f'&q={search_query}'
                    f'&remote={remote}'
                    f'&salary={salary_price}'
                    f'&type={request_type}'
                    f'&with_salary={with_salary}')
        required_html = browser.page_source
        soup = BeautifulSoup(required_html, 'html5lib')
        return HabrPage(soup)

    def load_vacancies(self, search_query='', remote='true', salary_price='400000',
                       with_salary='true', request_type='all') -> [Vacancy]:
        number_of_pages = self.get_page(1, search_query, remote, salary_price, with_salary,
                                        request_type).find_number_of_search_pages()
        vacancies = []
        for page_number in range(1, number_of_pages + 1):
            page = self.get_page(page_number, search_query, remote, salary_price, with_salary, request_type)
            vacancies.extend(page.find_vacancies())
        return vacancies


def parse_vacancies_data(vacancy_cards):
    for data in vacancy_cards:
        base_url = 'https://career.habr.com'
        vacancy_title = data.find('a', class_='vacancy-card__title-link').text
        company_title = data.find('a', class_='link-comp link-comp--appearance-dark').text
        company_link = base_url + data.find('a', class_='link-comp link-comp--appearance-dark').get('href')
        title_link = base_url + data.find('a', class_='vacancy-card__title-link').get('href')
        date = data.find('div', class_='vacancy-card__date').find('time', class_='basic-date').text.strip()
        icon_link = data.find('a', class_='vacancy-card__icon-link').find('img', 'vacancy-card__icon').get('src')
        salary = data.find('div', class_='basic-salary').text
        low_salary = find_lower_salary_value(salary)
        high_salary = find_high_salary_value(salary)
        currency = find_salary_currency(salary)
        write_vacancies_2_csv_file(vacancy_title=vacancy_title, company_title=company_title,
                                   company_link=company_link,
                                   title_link=title_link, date=date, icon_link=icon_link, low_salary=low_salary,
                                   high_salary=high_salary, currency=currency)
        write_vacancy_data_2_google_sheet(vacancy_title, company_title, company_link, title_link, date, icon_link,
                                          low_salary, high_salary, currency)

# def get_data_by_search_page(day_month_year, hour_minute_second, pn, q=question, r=remote, s=salary_price,
#                             ws=with_salary, u=url, t=request_type):
#     """ Функция сохраняет html код страницы и возвращает переменную soup в которой содержится html код страницы.
#     :param day_month_year:
#     :param hour_minute_second:
#     :param s: salary - зарплата
#     :param ws: with_salary - указана ли зарплата
#     :param u: урл
#     :param pn: номер страницы с которой сдирается html код
#     :param q: любой поисковой запрос на сайте, для поиска вакансий
#     :param r: можно ли работать удаленно? Если да, то пиши значение true
#     :param t: я хз че это такое, постоянно стоит all
#     :return: Количество страниц с вакансиями, соответствующих запросу
#     """
#     browser.get(u + f'?page={pn}&q={q}&remote={r}&salary={s}&type={t}&with_salary={ws}')
#     required_html = browser.page_source
#     soup = BeautifulSoup(required_html, 'html5lib')
#     html_name = f"html_{pn}_{day_month_year}_{hour_minute_second}.html"
#     html_file = open(f'scrapped_data/{day_month_year}/{html_name}', 'w')
#     html_file.write(f'{soup}')
#     return soup


# def collecting_vacancies_data(day_month_year, hour_minute_second, number_of_search_pages, pn=1):
#     for item in range(1, number_of_search_pages + 1):
#         print(f'Парсим страницу выдачи с номером {pn}')
#         print('__________________________________________________')
#         soup = get_data_by_search_page(day_month_year=day_month_year, hour_minute_second=hour_minute_second,
#                                        pn=pn)
#         vacancy_card.extend(soup.find_all(class_='vacancy-card'))
#         print(len(vacancy_card))
#         print(f'закончил парсить страницу с номером = {pn}')
#         print('____________________________________________________')
#         pn = pn + 1
#     return vacancy_card
