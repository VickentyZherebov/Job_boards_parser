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
    def __init__(self, question, remote, salary, type, with_salary, qid, sort, divisions, page_number: int):
        """
        :param question: поисковой запрос
        :param remote:
        :param salary:
        :param type: Узнать, что это такое
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
        self.type = type
        self.salary = salary
        self.remote = remote
        self.question = question

    def make_search_string_for_habr(self) -> str:
        url = "https://career.habr.com/vacancies"
        search_string_for_habr = url + f'?page={self.page_number}&q={self.question}&remote={self.remote}' \
                                       f'&salary={self.salary}&type={self.type}&with_salary={self.with_salary}' \
                                       f'&qid={self.qid}&divisions[]={self.divisions}&sort={self.sort}'
        # print(search_string_for_habr)
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

    def number_of_search_pages(self) -> int:
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

    def find_lower_salary_value(self, salary):
        low_salary = ''
        if re.search('от', salary):  # проверяем в зепке наличие слова "от "
            first_split = re.split('от ', salary)  # чистим строку от слова "от "
            if re.search('до', first_split[1]):  # проверяем в цене наличие слова "До ", если есть, то:
                second_split = re.split(' до ', first_split[1])  # отрезаем слово "До "
                if re.search('₽', second_split[1]):  # Если находим символ рубля, то:
                    low_salary = second_split[0].replace(' ', '')  # убиваем пробелы
                else:
                    if re.search('\\$', second_split[1]):  # Если находим символ доллара, то:
                        low_salary = second_split[0].replace(' ', '')  # убиваем пробелы
                    else:
                        if re.search('€', second_split[1]):  # Если находим символ евро, то:
                            low_salary = second_split[0].replace(' ', '')  # убиваем пробелы
                        else:
                            print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
                            print('_____________________________________________')
            else:
                if re.search('₽', first_split[1]):
                    low_salary = re.split(' ₽', first_split[1])[0].replace(' ', '')
                else:
                    if re.search('\\$', first_split[1]):
                        low_salary = re.split(' \\$', first_split[1])[0].replace(' ', '')
                    else:
                        if re.search('€', first_split[1]):
                            low_salary = re.split(' €', first_split[1])[0].replace(' ', '')
                        else:
                            print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
        else:
            if re.search('До ', salary):
                first_split = re.split('До ', salary)
                if re.search('₽', first_split[1]):
                    low_salary = 'не указано'
                else:
                    if re.search('\\$', first_split[1]):
                        low_salary = 'не указано'
                    else:
                        if re.search('€', first_split[1]):
                            low_salary = 'не указано'
            else:
                low_salary = 'нет указано'

        return low_salary

    def find_high_salary_value(self, salary):
        high_salary = ''
        if re.search('от', salary):  # проверяем в зепке наличие слова "от "
            first_split = re.split('от ', salary)  # чистим строку от слова "от "
            if re.search('до', first_split[1]):  # проверяем в цене наличие слова "До ", если есть, то:
                second_split = re.split(' до ', first_split[1])  # отрезаем слово "До "
                if re.search('₽', second_split[1]):  # Если находим символ рубля, то:
                    high_salary = re.split(' ₽', second_split[1])[0].replace(' ', '')
                else:
                    if re.search('\\$', second_split[1]):  # Если находим символ рубля, то:
                        high_salary = re.split(' \\$', second_split[1])[0].replace(' ', '')
                    else:
                        if re.search('€', second_split[1]):  # Если находим символ евро, то:
                            high_salary = re.split(' €', second_split[1])[0].replace(' ', '')
                        else:
                            print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
                            print('_____________________________________________')
            else:
                if re.search('₽', first_split[1]):
                    high_salary = 'не указано'
                else:
                    if re.search('\\$', first_split[1]):
                        high_salary = 'не указано'
                    else:
                        if re.search('€', first_split[1]):
                            high_salary = 'не указано'
                        else:
                            print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
        else:
            if re.search('До ', salary):
                first_split = re.split('До ', salary)
                if re.search('₽', first_split[1]):
                    high_salary = re.split(' ₽', first_split[1])[0].replace(' ', '')
                else:
                    if re.search('\\$', first_split[1]):
                        high_salary = re.split(' \\$', first_split[1])[0].replace(' ', '')
                    else:
                        if re.search('€', first_split[1]):
                            high_salary = re.split(' €', first_split[1])[0].replace(' ', '')
            else:
                high_salary = 'не указано'

        return high_salary

    def find_salary_currency(self, salary) -> str:
        if re.search('₽', salary):
            currency = 'rub'
        else:
            if re.search('\\$', salary):
                currency = 'usd'
            else:
                if re.search('€', salary):
                    currency = 'eur'
                else:
                    currency = 'не указано'
        return currency

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
                low_salary=self.find_lower_salary_value(salary),
                high_salary=self.find_high_salary_value(salary),
                currency=self.find_salary_currency(salary)
                                )
            vacancies.append(vacancy)
        return vacancies

    def collect_all_vacancy_cards_from_request(self) -> [VacancyCard]:
        question = self.search_request_link.question
        remote = self.search_request_link.remote
        salary = self.search_request_link.salary
        type = self.search_request_link.type
        with_salary = self.search_request_link.with_salary
        qid = self.search_request_link.qid
        sort = self.search_request_link.sort
        divisions = self.search_request_link.divisions
        vacancies = []
        for page in range(1, self.get_page().number_of_search_pages() + 1):
            search_request = SearchRequestLink(question=question,
                                               remote=remote,
                                               salary=salary,
                                               type=type,
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
                        "Имя вакансии:": collect_all_vacancies[page - 1][vacancy - 1].vacancy_name,
                        "Имя компании:": collect_all_vacancies[page - 1][vacancy - 1].company_name,
                        "Ссылка на компанию:": collect_all_vacancies[page - 1][vacancy - 1].company_link,
                        "Ссылка на вакансию:": collect_all_vacancies[page - 1][vacancy - 1].vacancy_link,
                        "Дата публикации:": collect_all_vacancies[page - 1][vacancy - 1].date_of_publication,
                        "Ссылка на логотип:": collect_all_vacancies[page - 1][vacancy - 1].logo_link,
                        "Зепка": collect_all_vacancies[page - 1][vacancy - 1].salary,
                        "Зепка от:": collect_all_vacancies[page - 1][vacancy - 1].low_salary,
                        "Зепка до:": collect_all_vacancies[page - 1][vacancy - 1].high_salary,
                        "Валюта:": collect_all_vacancies[page - 1][vacancy - 1].currency
                    }
                )
        with open("scrapped_data/parsed_vacancies.json", "a", encoding="utf-8") as file:
            json.dump(dict_vacancies_json, file, indent=4, ensure_ascii=False)
        browser.quit()
