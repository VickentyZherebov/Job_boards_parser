import json

from bs4 import BeautifulSoup
from selenium import webdriver
import re
import math

# from GSheetsConnect import write_vacancy_data_2_google_sheet
# from WorkWithCSV import write_vacancies_2_csv_file

chromedriver = 'selenium_files/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)


class SearchRequestLink:
    def __init__(self, question, remote, salary, search_type, with_salary, qid, sort, divisions, page_number: int):
        """
        :param question: поисковой запрос
        :param remote:
        :param salary:
        :param search_type: тип поиска - все вакансии или подходящие под твой профиль
        :param with_salary:
        :param qid: Квалификация специалиста. 1 - любая, 2 - intern, 3 - junior, 4 - middle, 5 - senior, 6 - lead
        :param sort: сортировка
        :param divisions: Сфера деятельности
        """
        self.page_number = page_number
        self.divisions = divisions
        self.sort = sort
        self.qid = qid
        self.with_salary = with_salary
        self.search_type = search_type
        self.salary = salary
        self.remote = remote
        self.question = question

    def make_search_string_for_habr(self) -> str:
        url = "https://career.habr.com/vacancies"
        search_string_for_habr = url + f'?page={self.page_number}&q={self.question}&remote={self.remote}' \
                                       f'&salary={self.salary}&type={self.search_type}&with_salary={self.with_salary}' \
                                       f'&qid={self.qid}&divisions[]={self.divisions}&sort={self.sort}'
        return search_string_for_habr


class VacancyCard:
    """карточка вакансии в поисковой выдаче habr career"""

    def __init__(self, vacancy_name: str, vacancy_link: str, company_name: str, company_link: str, logo_link: str,
                 date_of_publication: str, salary: str, low_salary, high_salary, currency: str):
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
        self.currency = currency
        self.high_salary = high_salary
        self.low_salary = low_salary
        self.salary = salary
        self.date_of_publication = date_of_publication
        self.logo_link = logo_link
        self.company_link = company_link
        self.company_name = company_name
        self.vacancy_link = vacancy_link
        self.vacancy_name = vacancy_name


class HabrPage:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def find_number_of_vacancies(self) -> int:
        find_count_string = self.soup.find(
            'div', class_="search-total disable-font-boosting search-total--appearance-search-panel").text
        number_of_vacancies = int(re.findall('\\d+', find_count_string)[0])
        return number_of_vacancies

    def find_number_of_search_pages(self) -> int:
        number_of_vacancies = self.find_number_of_vacancies()
        number_of_search_pages = math.ceil(number_of_vacancies / 25)
        return number_of_search_pages


class HabrClient:
    def __init__(self, search_request_link: SearchRequestLink):
        self.search_request_link = search_request_link

    def get_page(self) -> HabrPage:
        browser.get(f'{self.search_request_link.make_search_string_for_habr()}')
        required_html = browser.page_source
        soup = BeautifulSoup(required_html, 'html5lib')
        return HabrPage(soup)

    def get_data_from_all_pages(self) -> HabrPage:
        url_list = self.make_urls_list()
        soup = BeautifulSoup()
        for url in range(1, len(url_list) + 1):
            browser.get(f'{url_list[url - 1]}')
            required_html = browser.page_source
            soup.append(BeautifulSoup(required_html, 'html5lib'))
        return HabrPage(soup)

    def make_urls_list(self) -> []:
        question = self.search_request_link.question
        remote = self.search_request_link.remote
        salary = self.search_request_link.salary
        search_type = self.search_request_link.search_type
        with_salary = self.search_request_link.with_salary
        qid = self.search_request_link.qid
        sort = self.search_request_link.sort
        divisions = self.search_request_link.divisions
        number_of_search_pages = self.get_page().find_number_of_search_pages()
        urls_list = []
        for page in range(1, number_of_search_pages + 1):
            url = SearchRequestLink(question=question,
                                    remote=remote,
                                    salary=salary,
                                    search_type=search_type,
                                    with_salary=with_salary,
                                    qid=qid,
                                    sort=sort,
                                    divisions=divisions,
                                    page_number=page).make_search_string_for_habr()
            urls_list.append(url)
            print(url)
        return urls_list

    def salary_parser(self, salary):
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
                if re.search("до", salary):
                    low_salary = "не указано"
                    high_salary = re.split('до', salary)[1].replace(' ', '')[:-1]
                    salary_symbol = re.split('до', salary)[1].replace(' ', '')[-1:]
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
        return low_salary, high_salary, salary_symbol, currency

    def collect_vacancy_cards_from_page_2(self) -> [VacancyCard]:
        base_url: str = "https://career.habr.com"
        vacancy_cards = self.get_data_from_all_pages().soup.find_all(class_='vacancy-card')
        vacancies = []
        for vacancy_card in vacancy_cards:
            salary = vacancy_card.find('div', class_='basic-salary').text
            vacancy = VacancyCard(
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
                low_salary=self.salary_parser(salary)[0],
                high_salary=self.salary_parser(salary)[1],
                currency=self.salary_parser(salary)[3]
            )
            vacancies.append(vacancy)
        return vacancies

    def collect_vacancy_cards_from_page(self) -> [VacancyCard]:
        base_url: str = "https://career.habr.com"
        vacancy_cards = self.get_page().soup.find_all(class_='vacancy-card')
        vacancies = []
        for vacancy_card in vacancy_cards:
            salary = vacancy_card.find('div', class_='basic-salary').text
            vacancy = VacancyCard(
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
                low_salary=self.salary_parser(salary)[0],
                high_salary=self.salary_parser(salary)[1],
                currency=self.salary_parser(salary)[3]
            )
            vacancies.append(vacancy)
        return vacancies

    def collect_all_vacancy_cards_from_request(self) -> [VacancyCard]:
        question = self.search_request_link.question
        remote = self.search_request_link.remote
        salary = self.search_request_link.salary
        search_type = self.search_request_link.search_type
        with_salary = self.search_request_link.with_salary
        qid = self.search_request_link.qid
        sort = self.search_request_link.sort
        divisions = self.search_request_link.divisions
        vacancies = []
        for page in range(1, self.get_page().find_number_of_search_pages() + 1):
            search_request = SearchRequestLink(question=question,
                                               remote=remote,
                                               salary=salary,
                                               search_type=search_type,
                                               with_salary=with_salary,
                                               qid=qid,
                                               sort=sort,
                                               divisions=divisions,
                                               page_number=page)
            habr_client = HabrClient(search_request_link=search_request)
            collected_data = habr_client.collect_vacancy_cards_from_page()
            vacancies.append(collected_data)
        return vacancies

    def make_json_from_search_request(self):
        print(self.get_page().find_number_of_vacancies())
        dict_vacancies_json = []
        collect_all_vacancies = self.collect_all_vacancy_cards_from_request()
        for page in range(1, len(collect_all_vacancies) + 1):
            number_of_vacancies = len(collect_all_vacancies[page - 1])
            print(number_of_vacancies)
            for vacancy in range(1, number_of_vacancies + 1):
                print(collect_all_vacancies[page - 1][vacancy - 1])
                dict_vacancies_json.append(
                    {
                        "Имя вакансии": collect_all_vacancies[page - 1][vacancy - 1].vacancy_name,
                        "Имя компании": collect_all_vacancies[page - 1][vacancy - 1].company_name,
                        "Ссылка на компанию": collect_all_vacancies[page - 1][vacancy - 1].company_link,
                        "Ссылка на вакансию": collect_all_vacancies[page - 1][vacancy - 1].vacancy_link,
                        "Дата публикации": collect_all_vacancies[page - 1][vacancy - 1].date_of_publication,
                        "Ссылка на логотип": collect_all_vacancies[page - 1][vacancy - 1].logo_link,
                        "Зарплата": collect_all_vacancies[page - 1][vacancy - 1].salary,
                        "Зарплата от": collect_all_vacancies[page - 1][vacancy - 1].low_salary,
                        "Зарплата до": collect_all_vacancies[page - 1][vacancy - 1].high_salary,
                        "Валюта": collect_all_vacancies[page - 1][vacancy - 1].currency
                    }
                )
        with open("scrapped_data/parsed_vacancies.json", "a", encoding="utf-8") as file:
            json.dump(dict_vacancies_json, file, indent=4, ensure_ascii=False)
        browser.quit()
