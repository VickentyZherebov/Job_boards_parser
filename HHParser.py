# import requests
import json
import re
# import csv
# import math
from bs4 import BeautifulSoup
from selenium import webdriver

chromedriver = 'selenium_files/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)


class VacancyCardMini:
    """
    Объект карточки вакансии, которая отображается в результатах поисковой выдачи HeadHunter
    """
    def __init__(self, vacancy_title, vacancy_url, company_title, company_url, vacancy_compensation):
        """
        :param vacancy_title: Название вакансии
        :param vacancy_url: Ссылка на вакансию
        :param company_title: Название компании
        :param company_url: Ссылка на компанию
        :param vacancy_compensation: Зарплата
        """
        self.vacancy_compensation = vacancy_compensation
        self.vacancy_title = vacancy_title
        self.vacancy_url = vacancy_url
        self.company_title = company_title
        self.company_url = company_url


class SearchRequestLink:
    """
    Создает поисковую ссылку для скачивания результатов поиска вакансий на HeadHunter
    """
    def __init__(self, search_field: str, clusters: str, enable_snippets: str, ored_clusters: str, schedule: str,
                 text: str, order_by: str, salary: str, page: int, only_with_salary: str, label):
        """
        :param label: Можно указывать "label=not_from_agency"
        :param only_with_salary: Показывать только вакансии с зарплатами. = true
        :param search_field: где искать - в вакансии, компании, везде
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
                                     f'only_with_salary={self.only_with_salary}'
        print(search_string_for_hh)
        return search_string_for_hh


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
            salary = vacancy_card.find_all('span', class_="bloko-header-section-3 bloko-header-section-3_lite")[1].text
            vac_url = vacancy_card.find('a', class_="bloko-link").get('href')
            vac_url = re.split("\\?", vac_url)[0]
            # @todo выяснить, как убрать символ nnbsp. Вот кусок говнокода:
            #   <div class="vacancy-serp-item__sidebar">
            #   <span data-qa="vacancy-serp__vacancy-compensation"
            #   class="bloko-header-section-3 bloko-header-section-3_lite">
            #   от <!-- -->150 000<!-- --> <!-- -->руб.</span></div>
            vacancy = VacancyCardMini(
                vacancy_title=vacancy_card.find('a', class_="bloko-link").text,
                company_title=vacancy_card.find('a', class_="bloko-link bloko-link_secondary").text,
                company_url="https://hh.ru" + vacancy_card.find('a', class_="bloko-link bloko-link_secondary").get('href'),
                vacancy_url=vac_url,
                vacancy_compensation=salary
            )
            vacancies.append(vacancy)
            print(f'{vacancy.vacancy_title} - {vacancy.vacancy_url} - {vacancy.vacancy_compensation}')
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
        for page in range(0, self.get_page().number_of_search_pages() + 1):
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
            vacancies.append(collected_data)
        return vacancies

    def make_json_from_search_request(self):
        dict_vacancies_json = []
        collect_all_vacancies = self.collect_all_vacancy_cards_from_request()
        for page in range(1, len(collect_all_vacancies) + 1):
            number_of_vacancies = len(collect_all_vacancies[page - 1])
            for vacancy in range(1, number_of_vacancies + 1):
                dict_vacancies_json.append(
                    {
                        "Имя вакансии": collect_all_vacancies[page - 1][vacancy - 1].vacancy_title,
                        "Имя компании": collect_all_vacancies[page - 1][vacancy - 1].company_title,
                        "Ссылка на компанию": collect_all_vacancies[page - 1][vacancy - 1].company_url,
                        "Ссылка на вакансию": collect_all_vacancies[page - 1][vacancy - 1].vacancy_url,
                        "Зарплата": collect_all_vacancies[page - 1][vacancy - 1].vacancy_compensation
                    }
                )
        with open("scrapped_data/parsed_hh_vacancies.json", "a", encoding="utf-8") as file:
            json.dump(dict_vacancies_json, file, indent=4, ensure_ascii=False)
        browser.quit()

# @todo выяснить, как генерить поисковую строку с несколькими одинаковыми параметрами, но разным содержанием
#   например такой параметр, как Ключевые слова (label)
search_link = SearchRequestLink(clusters="true",
                                enable_snippets="true",
                                ored_clusters="true",
                                schedule="remote",
                                text="IT-рекрутер",
                                order_by="salary_desc",
                                salary="140000",
                                page=0,
                                search_field="",
                                only_with_salary="true",
                                label="not_from_agency")

client = HhClient(search_request_link=search_link)
# @todo выяснить почему тут ругается, что функция ничего не возвращает, а на мейне не ругается
make_json = client.make_json_from_search_request()
