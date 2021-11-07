import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver

chromedriver = 'selenium_files/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)


# @todo Придумать как парсить контакты рекрутера - они указаны в некоторых вакансиях и открываются только если
#   ты залогинен как кандидат. То есть тут можно хапнуть бан, поэтому либо придется рандомизировать тайминги парсинга,
#   либо делать левый аккаунт, либо забить болт и просто парсить надеясь на удачу. Чтобы контакты увидеть - надо
#   взаимодействовать с кнопкой "Показать контакты" - это тоже надобно понять как делать.

class VacancyCardMini:
    """
    Объект карточки вакансии, которая отображается в результатах поисковой выдачи HeadHunter,
    тут например https://clck.ru/YeQqw.
    """
    def __init__(self,
                 vacancy_title,
                 vacancy_url,
                 company_title,
                 company_url,
                 vacancy_compensation_from,
                 vacancy_compensation_to,
                 vacancy_currency,
                 ):
        """
        :param vacancy_title: Название вакансии
        :param vacancy_url: Ссылка на вакансию
        :param company_title: Название компании
        :param company_url: Ссылка на компанию
        """
        self.vacancy_currency = vacancy_currency
        self.vacancy_compensation_to = vacancy_compensation_to
        self.vacancy_compensation_from = vacancy_compensation_from
        self.vacancy_title = vacancy_title
        self.vacancy_url = vacancy_url
        self.company_title = company_title
        self.company_url = company_url


class SearchRequestLink:
    """
    Создает поисковую ссылку для скачивания вакансий на HeadHunter
    """
    def __init__(self, search_field: str, clusters: str, enable_snippets: str, ored_clusters: str, schedule: str,
                 text: str, order_by: str, salary: str, page: int, only_with_salary: str, label):
        """
        :param label: Можно указывать "label=not_from_agency"
        :param only_with_salary: Показывать только вакансии с зарплатами. = true
        :param search_field: где искать - в названии вакансии ("name"), в описании вакансии (description), компании(company_name), везде
        :param clusters: ХЗ что такое, по дефолту стоит значение true
        :param enable_snippets: ХЗ что такое, по дефолту стоит значение true
        :param ored_clusters: ХЗ что такое, по дефолту стоит значение true
        :param schedule: График работы - если удаленная, то ставим значение remote
        :param text: Текст поискового запрос
        :param order_by: Сортировка поисковой выдачи. Если по зарплате от большего к меньшему, то ставим "salary_desc"
        :param salary: показывать вакансии с зарплатой от указанного значения, например "125000" - покажет соответствующие вакансии
        :param page: Номер поисковой страницы. Начинается как ни странно с 0 страницы. Это ВАЖНО учитывать.
        """
        self.label = label
        self.only_with_salary = only_with_salary
        self.search_field = search_field
        self.page = page
        self.salary = salary
        self.order_by = order_by
        self.text = text
        self.schedule = schedule
        self.ored_clusters = ored_clusters
        self.enable_snippets = enable_snippets
        self.clusters = clusters

    def make_search_string_for_hh(self) -> str:
        """
        :return:  Метод возвращает итоговую ссылку
        """
        url = "https://hh.ru/search/vacancy?"
        search_string_for_hh = url + f'clusters=true&' \
                                     f'enable_snippets=true&' \
                                     f'ored_clusters=true&' \
                                     f'text={self.text}&' \
                                     f'order_by={self.order_by}&' \
                                     f'salary={self.salary}&' \
                                     f'schedule={self.schedule}&' \
                                     f'page={self.page}&' \
                                     f'search_field={self.search_field}&' \
                                     f'only_with_salary={self.only_with_salary}&' \
                                     f'label={self.label}'
        print(search_string_for_hh)
        return search_string_for_hh


class Salary:
    """
    Сей класс получает значение зарплаты в виде строки и возвращает лист, в котором указана минимальная зарплата,
    максимальная зарплата и валюта. Если какой-то из параметров в вакансии отсутствует - заменяем на "Не указано"
    """
    def __init__(self, salary: str) -> []:
        self.salary = salary

    def salary_parser(self):
        if re.search("от", self.salary):
            low_salary = re.split(' ', self.salary)[1]
            low_salary = re.split("\\u202f", low_salary)[0] + re.split("\\u202f", low_salary)[1]
            high_salary = "Не указано"
            salary_symbol = re.split(' ', self.salary)[2]
        else:
            if re.search("до", self.salary):
                low_salary = "Не указано"
                high_salary = re.split(' ', self.salary)[1]
                high_salary = re.split("\\u202f", high_salary)[0] + re.split("\\u202f", high_salary)[1]
                salary_symbol = re.split(' ', self.salary)[2]
            else:
                if re.search("–", self.salary):
                    low_salary = re.split(" ", self.salary)[0]
                    low_salary = re.split("\\u202f", low_salary)[0] + re.split("\\u202f", low_salary)[1]
                    high_salary = re.split(" ", self.salary)[2]
                    high_salary = re.split("\\u202f", high_salary)[0] + re.split("\\u202f", high_salary)[1]
                    salary_symbol = re.split(' ', self.salary)[3]
                else:
                    low_salary = "не указано"
                    high_salary = "не указано"
                    salary_symbol = "не указано"
        if salary_symbol == 'USD':
            currency = "usd"
        else:
            if salary_symbol == 'USD':
                currency = "usd"
            else:
                if salary_symbol == 'руб.':
                    currency = "rub"
                else:
                    if salary_symbol == 'EUR':
                        currency = "eur"
                    else:
                        currency = "не указано"
        return low_salary, high_salary, salary_symbol, currency


class HhPage:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def find_number_of_vacancies(self) -> int:
        find_count_string = self.soup.find('h1', class_="bloko-header-section-3").text
        number_of_vacancies = int(re.findall('\\d+', find_count_string)[0])
        return number_of_vacancies

    def number_of_search_pages(self) -> int:
        pagination = self.soup.find_all('a', attrs={'data-qa': 'pager-page'})
        count = int(pagination[-1].text)
        print(f'count of search pages = {count}')
        return count


class HhClient:
    def __init__(self, search_request_link: SearchRequestLink):
        self.search_request_link = search_request_link

    def get_page(self) -> HhPage:
        browser.get(f'{self.search_request_link.make_search_string_for_hh()}')
        required_html = browser.page_source
        soup = BeautifulSoup(required_html, 'html5lib')
        return HhPage(soup)

    def collect_vacancy_cards_from_page(self) -> [VacancyCardMini]:
        vacancy_cards = self.get_page().soup.find_all(class_="vacancy-serp-item")
        vacancies = []
        for vacancy_card in vacancy_cards:
            # условие ниже нужно для того, чтобы выявлять вакансии без зарплаты и корректно их обрабатывать
            if len(vacancy_card.find_all('span', class_="bloko-header-section-3 bloko-header-section-3_lite")) > 1:
                salary = Salary(vacancy_card.find_all('span', class_="bloko-header-section-3 bloko-header-section-3_lite")[1].text).salary_parser()
                vac_url = vacancy_card.find('a', class_="bloko-link").get('href')
                vac_url = re.split("\\?", vac_url)[0]
                company_title = vacancy_card.find('a', class_="bloko-link bloko-link_secondary").text
                if re.search("\\xa0", company_title):
                    company_title = re.split("\\xa0", company_title)[0] + " " + re.split("\\xa0", company_title)[1]
                # @todo выяснить, как убрать символ nnbsp. Вот кусок говнокода:
                #   <div class="vacancy-serp-item__sidebar">
                #   <span data-qa="vacancy-serp__vacancy-compensation"
                #   class="bloko-header-section-3 bloko-header-section-3_lite">
                #   от <!-- -->150 000<!-- --> <!-- -->руб.</span></div>
                vacancy = VacancyCardMini(
                    vacancy_title=vacancy_card.find('a', class_="bloko-link").text,
                    company_title=company_title,
                    company_url="https://hh.ru" + vacancy_card.find('a', class_="bloko-link bloko-link_secondary").get('href'),
                    vacancy_url=vac_url,
                    vacancy_compensation_from=salary[0],
                    vacancy_compensation_to=salary[1],
                    vacancy_currency=salary[3]
                )
                vacancies.append(vacancy)
            else:
                salary = ["Не указано", "Не указано", "Не указано", "Не указано"]
                vac_url = vacancy_card.find('a', class_="bloko-link").get('href')
                vac_url = re.split("\\?", vac_url)[0]
                company_title = vacancy_card.find('a', class_="bloko-link bloko-link_secondary").text
                if re.search("\\xa0", company_title):
                    company_title = re.split("\\xa0", company_title)[0] + " " + re.split("\\xa0", company_title)[1]
                vacancy = VacancyCardMini(
                    vacancy_title=vacancy_card.find('a', class_="bloko-link").text,
                    company_title=company_title,
                    company_url="https://hh.ru" + vacancy_card.find('a', class_="bloko-link bloko-link_secondary").get(
                        'href'),
                    vacancy_url=vac_url,
                    vacancy_compensation_from=salary[0],
                    vacancy_compensation_to=salary[1],
                    vacancy_currency=salary[3]
                )
                vacancies.append(vacancy)
            print(f'{vacancy.vacancy_title}, {vacancy.vacancy_url}, {vacancy.company_title}')
        return vacancies

    def collect_all_vacancy_cards_from_request(self) -> [VacancyCardMini]:
        search_field = self.search_request_link.search_field
        clusters = self.search_request_link.clusters
        enable_snippets = self.search_request_link.enable_snippets
        ored_clusters = self.search_request_link.ored_clusters
        text = self.search_request_link.text
        order_by = self.search_request_link.order_by
        salary = self.search_request_link.salary
        schedule = self.search_request_link.schedule
        only_with_salary = self.search_request_link.only_with_salary
        label = self.search_request_link.label
        vacancies = []
        for page in range(0, self.get_page().number_of_search_pages()):
            search_request = SearchRequestLink(search_field=search_field,
                                               clusters=clusters,
                                               enable_snippets=enable_snippets,
                                               ored_clusters=ored_clusters,
                                               text=text,
                                               order_by=order_by,
                                               salary=salary,
                                               page=page,
                                               schedule=schedule,
                                               only_with_salary=only_with_salary,
                                               label=label)
            hh_client = HhClient(search_request_link=search_request)
            collected_data = hh_client.collect_vacancy_cards_from_page()
            vacancies.extend(collected_data)
        print(len(vacancies))
        return vacancies

    def make_json_from_search_request(self):
        dict_vacancies_json = []
        collect_all_vacancies = self.collect_all_vacancy_cards_from_request()
        for vacancy in range(1, len(collect_all_vacancies) + 1):
            dict_vacancies_json.append(
                {
                    "Имя вакансии": collect_all_vacancies[vacancy - 1].vacancy_title,
                    "Имя компании": collect_all_vacancies[vacancy - 1].company_title,
                    "Ссылка на компанию": collect_all_vacancies[vacancy - 1].company_url,
                    "Ссылка на вакансию": collect_all_vacancies[vacancy - 1].vacancy_url,
                    "Зарплата от": collect_all_vacancies[vacancy - 1].vacancy_compensation_from,
                    "Зарплата до": collect_all_vacancies[vacancy - 1].vacancy_compensation_to,
                    "Валюта": collect_all_vacancies[vacancy - 1].vacancy_currency
                }
            )
        with open(f"scrapped_data/parsed_hh_vacancies_{current_date}.json", "a", encoding="utf-8") as file:
            json.dump(dict_vacancies_json, file, indent=4, ensure_ascii=False)
        browser.quit()


# @todo придумать, как генерить поисковую строку с несколькими одинаковыми параметрами, но разным содержанием
#   например такой параметр, как Ключевые слова (label)
search_link = SearchRequestLink(clusters="true",
                                enable_snippets="true",
                                ored_clusters="true",
                                schedule="remote",
                                text="IT-рекрутер",
                                order_by="salary_desc",
                                salary="",
                                page=0,
                                search_field="name",
                                only_with_salary="",
                                label="not_from_agency")
now = datetime.now()
current_date = f'{now.day}_{now.month}_{now.year}_{now.hour}_{now.minute}_{now.second}'
client = HhClient(search_request_link=search_link)
# @todo выяснить почему тут ругается, что функция ничего не возвращает, а на мейне не ругается
make_json = client.make_json_from_search_request()
