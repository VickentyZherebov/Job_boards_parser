import json
from copy import copy

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
import re
import math

# from GSheetsConnect import write_vacancy_data_2_google_sheet
# from WorkWithCSV import write_vacancies_2_csv_file
from selenium.webdriver.remote.webdriver import WebDriver





class SalaryRange:
    def __init__(self, salary: str, low_salary: str, high_salary: str, salary_symbol: str, currency: str):
        self.salary = salary
        self.currency = currency
        self.salary_symbol = salary_symbol
        self.high_salary = high_salary
        self.low_salary = low_salary

    @staticmethod
    def parse(salary: str) -> SalaryRange:
        if re.search("от", salary) and re.search("до", salary):
            low_salary = re.split('от ', salary)[1].split(' до')[0].replace(' ', '')
            high_salary = re.split('от ', salary)[1].split(' до')[1].replace(' ', '')[:-1]
            salary_symbol = re.split('от ', salary)[1].split(' до')[1].replace(' ', '')[-1:]
        else:
            if re.search("от", salary):
                low_salary = re.split('от ', salary)[1].replace(' ', '')[:-1]
                high_salary = "не указано"
                salary_symbol = re.split('от ', salary)[1].replace(' ', '')[-1:]
            else:
                if re.search("До", salary):
                    low_salary = "не указано"
                    high_salary = re.split('До', salary)[1].replace(' ', '')[:-1]
                    salary_symbol = re.split('До', salary)[1].replace(' ', '')[-1:]
                else:
                    low_salary = "не указано"
                    high_salary = "не указано"
                    salary_symbol = "не указано"
        if salary_symbol == '$':
            currency = "usd"
        else:
            if salary_symbol == '$':
                currency = "usd"
            else:
                if salary_symbol == '₽':
                    currency = "rub"
                else:
                    if salary_symbol == '€':
                        currency = "eur"
                    else:
                        if salary_symbol == '₸':
                            currency = "kzt"
                        else:
                            if salary_symbol == '₴':
                                currency = "uah"
                            else:
                                currency = "не указано"
        return SalaryRange(salary, low_salary, high_salary, salary_symbol, currency)


class VacancyCardMini:
    """
    карточка вакансии в поисковой выдаче habr career
    """

    # todo salary
    def __init__(self, vacancy_name: str, vacancy_link: str, company_name: str, company_link: str, logo_link: str,
                 date_of_publication: str, salary_range: SalaryRange):
        """
        :param vacancy_name: Название вакансии
        :param vacancy_link: Ссылка на страницу вакансии
        :param company_name: Название компании
        :param company_link: Ссылка на карточку компании
        :param logo_link: Ссылка на логотип компании
        :param date_of_publication: Дата публикации или обновления вакансии
        :param salary: Зарплата
        :param low_salary: Нижняя часть вилки
        :param high_salary: Верхняя часть вилки
        :param currency: валюта зарплаты
        """
        self.salary_range = salary_range
        self.date_of_publication = date_of_publication
        self.logo_link = logo_link
        self.company_link = company_link
        self.company_name = company_name
        self.vacancy_link = vacancy_link
        self.vacancy_name = vacancy_name


class VacancySearchRequest:
    def __init__(self, question: str, remote: str, salary: int, search_type, with_salary, qid, sort, divisions):
        """
        :param question: поисковой запрос
        :param remote: пиши true, если работа удаленная нужно, либо не пиши ничего
        :param salary:
        :param search_type: Узнать, что это такое
        :param with_salary:
        :param qid: Квалификация специалиста. 1 - любая, 2 - intern, 3 - junior, 4 - middle, 5 - senior, 6 - lead
        :param sort: сортировка
        :param divisions: Сфера деятельности
        """
        self.divisions = divisions
        self.sort = sort
        self.qid = qid
        self.with_salary = with_salary
        self.search_type = search_type
        self.salary = salary
        self.remote = remote
        self.question = question

    def build_url(self, page_number: int) -> str:
        url = "https://career.habr.com/vacancies"
        search_string_for_habr = url + f'?page={page_number}&' \
                                       f'q={self.question}&' \
                                       f'remote={self.remote}&' \
                                       f'salary={self.salary}&' \
                                       f'type={self.search_type}&' \
                                       f'with_salary={self.with_salary}&' \
                                       f'qid={self.qid}&' \
                                       f'divisions[]={self.divisions}&' \
                                       f'sort={self.sort}'
        return search_string_for_habr


class CompanyCardMini:
    """
    Карточка компании, посмотреть можно по ссылке https://career.habr.com/companies
    """

    def __init__(self, logo_link: str, company_name: str, company_link: str, rating: float, about: str, location: str,
                 size: str, vacancies_count: str, open_vacancies_link: str, skills: []):
        """
        Пока не очень пока понимаю зачем это. Похоже, что для документирования, чтобы тому кто наводит мышь на объект
        класса было понятно что к чему и чем является, но описывать все параметры не вижу смысла - они и так очевидные
        :param logo_link: Ссылка на логотип компании
        :param company_name: Название компании
        :param company_link: Ссылка на карточку компании на Хабре. Скорее всего буду использовать как ID
        :param rating: Рейтинг компании
        :param about: Текст о компании
        :param location: Локация офиса
        :param size: Размер компании
        :param vacancies_count: Количество открытых вакансий на момент скачивания данных
        :param open_vacancies_link: Ссылка на открытые вакансии
        :param skills: Основные навыки в компании
        """
        self.size = size
        self.location = location
        self.vacancies_count = vacancies_count
        self.open_vacancies_link = open_vacancies_link
        self.skills = skills
        self.about = about
        self.rating = rating
        self.company_link = company_link
        self.company_name = company_name
        self.logo_link = logo_link


class HabrVacancyListPage:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def count_vacancies(self) -> int:
        find_count_string = self.soup.find(
            'div', class_="search-total disable-font-boosting search-total--appearance-search-panel").text
        number_of_vacancies = int(re.findall('\\d+', find_count_string)[0])
        return number_of_vacancies

    def count_search_pages(self) -> int:
        number_of_vacancies = self.count_vacancies()
        number_of_search_pages = math.ceil(number_of_vacancies / 25)
        return number_of_search_pages


class HabrCompanyListPage:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def count_companies(self) -> int:
        find_count_string = self.soup.find(
            'div', class_="search-total disable-font-boosting search-total--appearance-search-panel").text
        number_of_companies = int(re.findall('\\d+', find_count_string)[0])
        return number_of_companies

    def count_search_pages(self) -> int:
        number_of_companies = self.count_companies()
        number_of_search_pages = math.ceil(number_of_companies / 25)
        return number_of_search_pages


class HabrClient:

    def __init__(self):
        chromedriver = 'selenium_files/chromedriver'
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # для открытия headless-браузера
        self.browser = webdriver.Chrome(chromedriver, options=options)

    def close(self):
        self.browser.close()

    def get_vacancy_list_page(self, search_request: VacancySearchRequest, page_number: int) -> HabrVacancyListPage:
        soup = self.__get_soup(search_request.build_url(page_number))
        return HabrVacancyListPage(soup)

    def get_company_list_page(self, with_vacancies: bool, page_number: int) -> HabrCompanyListPage:
        url = f"https://career.habr.com/companies?page={page_number}&with_vacancies={'1' if with_vacancies else ''}"
        soup = self.__get_soup(url)
        return HabrCompanyListPage(soup)

    def __get_soup(self, url: str) -> BeautifulSoup:
        self.browser.get(url)
        required_html = self.browser.page_source
        soup = BeautifulSoup(required_html, 'html5lib')
        return soup

    # todo 1. перенести в HabrVacancyListPage. Начать использовать self soup, не использовать habrclient
    def collect_vacancy_cards_from_page(self) -> [VacancyCardMini]:
        base_url: str = "https://career.habr.com"
        vacancy_cards = self.get_vacancy_list_page().soup.find_all(class_='vacancy-card')
        vacancies = []
        for vacancy_card in vacancy_cards:
            # @todo make method
            vacancy = self.__fetch_vacancy(base_url, vacancy_card)
            vacancies.append(vacancy)
        return vacancies

    def __fetch_vacancy(self, base_url: str, vacancy_card: Tag):
        salary = vacancy_card.find('div', class_='basic-salary').text
        vacancy = VacancyCardMini(
            vacancy_name=vacancy_card.find('a', class_='vacancy-card__title-link').text,
            company_name=vacancy_card.find('a', class_='link-comp link-comp--appearance-dark').text,
            company_link=base_url + vacancy_card.find(
                'a', class_='link-comp link-comp--appearance-dark').get('href'),
            vacancy_link=base_url + vacancy_card.find('a', class_='vacancy-card__title-link').get('href'),
            date_of_publication=vacancy_card.find(
                'div', class_='vacancy-card__date').find('time', class_='basic-date').text.strip(),
            logo_link=vacancy_card.find(
                'a', class_='vacancy-card__icon-link').find('img', 'vacancy-card__icon').get('src'),
            salary=salary,
            low_salary=self.parse_salary(salary)[0],
            high_salary=self.parse_salary(salary)[1],
            currency=self.parse_salary(salary)[3]
        )
        return vacancy

    # todo move to call site ()


    # todo move to call site ()
    def save_as_json(self, vacancies: [VacancyCardMini]):
        jsons = []
        for vacancy in vacancies:
            jsons.append(
                {
                    "Имя вакансии": vacancy.vacancy_name,
                    "Имя компании": vacancy.company_name,
                    "Ссылка на компанию": vacancy.company_link,
                    "Ссылка на вакансию": vacancy.vacancy_link,
                    "Дата публикации": vacancy.date_of_publication,
                    "Ссылка на логотип": vacancy.logo_link,
                    "Зарплата": {
                        "Зарплата от": vacancy.salary_range.low_salary,
                        "Зарплата до": vacancy.salary_range.high_salary,
                        "Валюта": vacancy.salary_range.currency
                    }
                }
            )
        with open("scrapped_data/parsed_vacancies.json", "a", encoding="utf-8") as file:
            json.dump(jsons, file, indent=4, ensure_ascii=False)


class CompanyParser:
    def __init__(self, with_vacancies: str):
        """
        :param with_vacancies: значение 1 (скачать компании с вакансиями) либо "" (скачать все компании)
        """
        self.with_vacancies = with_vacancies

    def get_page(self, page_number) -> HabrVacancyListPage:
        url = f"https://career.habr.com/companies?page={page_number}&with_vacancies={self.with_vacancies}"
        browser.get(f'{url}')
        required_html = browser.page_source
        soup = BeautifulSoup(required_html, 'html5lib')
        print(f"Скачал {page_number} страницу")
        return HabrVacancyListPage(soup)

    def find_search_pages_count(self) -> int:
        find_count_string = self.get_page(page_number="1").soup.find(
            'div', class_="search-total disable-font-boosting search-total--appearance-search-panel").text
        number_of_companies = int(re.sub(pattern=r'\D+', repl='', string=find_count_string))
        search_pages_count = math.ceil(number_of_companies / 25)
        print(f"Нашел количество страниц с компаниями - {search_pages_count}, а компаний всего - {number_of_companies}")
        return search_pages_count

    def get_all_pages_in_soup(self):
        search_pages_count = self.find_search_pages_count()
        all_pages_in_soup = []
        for page in range(1, search_pages_count + 1):
            all_pages_in_soup.append(self.get_page(page))
            print(f'Добавил в Суп {page} страницу')
        return all_pages_in_soup

    def collect_all_company_cards_from_soup(self) -> [CompanyCardMini]:
        all_pages_in_soup = self.get_all_pages_in_soup()
        print(f'количество страниц в объекте супа = {len(all_pages_in_soup)}')
        base_url: str = "https://career.habr.com"
        company_cards = []
        for pages in range(1, len(all_pages_in_soup) + 1):
            company_cards.extend(all_pages_in_soup[pages - 1].soup.find_all(class_='companies-item'))
            print(len(company_cards))
            for company_card in range(0, 25):
                print(company_cards[company_card])
        print(len(company_cards))
        companies = []
        for company_card in company_cards:
            try:
                location = company_card.find('div', class_='location').text
            except AttributeError:
                location = "N/A"
            try:
                rating = 1.0
            except AttributeError:
                rating = 1.0
            try:
                about = company_card.find('div', class_='about').text
            except AttributeError:
                about = 'N/A'
            try:
                company_name = company_card.find('a', class_='title').text
            except AttributeError:
                company_name = 'N/A'
            try:
                company_link = base_url + company_card.find('a', class_='title').get('href')
            except AttributeError:
                company_link = 'N/A'
            try:
                logo_link = company_card.find('a', class_='logo').get('style')
                logo_link = re.split('url\\(\'', logo_link)[1].split('\');')[0]
            except AttributeError:
                logo_link = 'N/A'
            try:
                open_vacancies_link = base_url + \
                                      company_card.find('div', class_='vacancies_count').find('a').get('href')
            except AttributeError:
                open_vacancies_link = 'N/A'
            try:
                vacancies_count = company_card.find('div', class_='vacancies_count').find('a').text
            except AttributeError:
                vacancies_count = 0
            try:
                size = company_card.find('div', class_='size').text
            except AttributeError:
                size = 'N/A'
            company = CompanyCardMini(
                location=location,
                rating=rating,
                about=about,
                company_name=company_name,
                company_link=company_link,
                logo_link=logo_link,
                open_vacancies_link=open_vacancies_link,
                vacancies_count=vacancies_count,
                size=size,
                skills=[]
            )
            companies.append(company)
            print("*******" * 5)
            print(company.company_name)
            print(company.company_link)
            print(company.logo_link)
            print(company.size)
            print(company.about)
            print(company.vacancies_count)
            print(company.open_vacancies_link)
            print(company.location)
            print(company.skills)
            print(company.rating)
        return companies

    # def collect_company_cards_from_page(self, page_number) -> [CompanyCardMini]:
    #     base_url: str = "https://career.habr.com"
    #     company_cards = self.get_page(page_number=page_number).soup.find_all(class_='companies-item')
    #     companies = []
    #     for company_card in company_cards:
    #         try:
    #             location = company_card.find('div', class_='location').text
    #         except AttributeError:
    #             location = "N/A"
    #         try:
    #             rating = 1.0
    #         except AttributeError:
    #             rating = 1.0
    #         try:
    #             about = company_card.find('div', class_='about').text
    #         except AttributeError:
    #             about = 'N/A'
    #         try:
    #             company_name = company_card.find('a', class_='title').text
    #         except AttributeError:
    #             company_name = 'N/A'
    #         try:
    #             company_link = base_url + company_card.find('a', class_='title').get('href')
    #         except AttributeError:
    #             company_link = 'N/A'
    #         try:
    #             logo_link = company_card.find('a', class_='logo').get('style')
    #             logo_link = re.split('url\\(\'', logo_link)[1].split('\');')[0]
    #         except AttributeError:
    #             logo_link = 'N/A'
    #         try:
    #             open_vacancies_link = base_url + \
    #                                   company_card.find('div', class_='vacancies_count').find('a').get('href')
    #         except AttributeError:
    #             open_vacancies_link = 'N/A'
    #         try:
    #             vacancies_count = company_card.find('div', class_='vacancies_count').find('a').text
    #         except AttributeError:
    #             vacancies_count = 0
    #         try:
    #             size = company_card.find('div', class_='size').text
    #         except AttributeError:
    #             size = 'N/A'
    #         company = CompanyCardMini(
    #             location=location,
    #             rating=rating,
    #             about=about,
    #             company_name=company_name,
    #             company_link=company_link,
    #             logo_link=logo_link,
    #             open_vacancies_link=open_vacancies_link,
    #             vacancies_count=vacancies_count,
    #             size=size,
    #             skills=[]
    #         )
    #         companies.append(company)
    #         # print("*******" * 5)
    #         # print(company.company_name)
    #         # print(company.company_link)
    #         # print(company.logo_link)
    #         # print(company.size)
    #         # print(company.about)
    #         # print(company.vacancies_count)
    #         # print(company.open_vacancies_link)
    #         # print(company.location)
    #         # print(company.skills)
    #         # print(company.rating)
    #     return companies

    def collect_all_companies_with_vacancies(self) -> [CompanyCardMini]:
        all_company_cards = []
        all_company_cards.extend(self.collect_all_company_cards_from_soup())
        dict_companies_json = []
        for number in range(1, len(all_company_cards) + 1):
            print(number, all_company_cards[number - 1].company_name)
            dict_companies_json.append(
                {
                    "Название компании": all_company_cards[number - 1].company_name,
                    "Ссылка на компанию": all_company_cards[number - 1].company_link,
                    "Локация": all_company_cards[number - 1].location,
                    "Рейтинг": all_company_cards[number - 1].rating,
                    "Ссылка на логотип": all_company_cards[number - 1].logo_link,
                    "Навыки": all_company_cards[number - 1].skills,
                    "Ссылка на открытые вакансии": all_company_cards[number - 1].open_vacancies_link,
                    "Количество открытых вакансий": all_company_cards[number - 1].vacancies_count,
                    "О компании": all_company_cards[number - 1].about,
                    "Размер компании": all_company_cards[number - 1].size
                }
            )
        with open("scrapped_data/parsed_companies.json", "a", encoding="utf-8") as file:
            json.dump(dict_companies_json, file, indent=4, ensure_ascii=False)
        return all_company_cards
