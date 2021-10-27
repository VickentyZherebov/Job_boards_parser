# import requests
import re
# import csv
import math
from bs4 import BeautifulSoup
from selenium import webdriver

chromedriver = 'selenium_files/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)

# headers = {'accept': '*/*',
#            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                          'Chrome/78.0.3904.108 Safari/537.36'}
# base_url = 'https://spb.hh.ru/search/vacancy?' \
#            'clusters=true&' \
#            'enable_snippets=true&' \
#            'salary=&' \
#            'st=searchVacancy&' \
#            'text=Агропромышленный&' \
#            'page=0'


# О чем эта функция:
# 1. на входе принимает урл откуда будет происходить парсинг и заголовки для работы bs4
# f возвращает список jobs который должен в себе содержать название и две ссылки

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
    def __init__(self, search_field: str, clusters: str, enable_snippets: str, ored_clusters: str, schedule: str, text: str, order_by: str, salary: str, page: int):
        """
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
                                     f'page={self.page}' \
                                     f'search_field={self.search_field}'
        return search_string_for_hh


class HhPage:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def find_number_of_vacancies(self) -> int:
        find_count_string = self.soup.find('h1', class_="bloko-header-section-3").text
        number_of_vacancies = int(re.findall('\\d+', find_count_string)[0])
        return number_of_vacancies

    def number_of_search_pages(self) -> int:
        number_of_vacancies = self.find_number_of_vacancies()
        number_of_search_pages = math.ceil(number_of_vacancies / 50)
        return number_of_search_pages


class HhClient:
    def __init__(self, search_request_link: SearchRequestLink):
        self.search_request_link = search_request_link

    def get_page(self) -> HhPage:
        browser.get(f'{self.search_request_link.make_search_string_for_hh()}')
        required_html = browser.page_source
        soup = BeautifulSoup(required_html, 'html5lib')
        return HhPage(soup)

    def collect_vacancy_cards_from_page(self) -> [VacancyCardMini]:
        base_url: str = "https://hh.ru"
        vacancy_cards = self.get_page().soup.find_all(class_="vacancy-serp-item")
        vacancies = []
        for vacancy_card in vacancy_cards:
            salary = vacancy_card.find('span', class_="bloko-header-section-3 bloko-header-section-3_lite").text
            vac_url = vacancy_card.find('a', class_="bloko-link").get('href')
            vac_url = re.split("\\?", vac_url)[0]
            vacancy = VacancyCardMini(
                vacancy_title=vacancy_card.find('a', class_="bloko-link").text,
                company_title=vacancy_card.find('a', class_="bloko-link bloko-link_secondary").text,
                company_url=vacancy_card.find('a', class_="bloko-link bloko-link_secondary").get('href'),
                vacancy_url=vac_url,
                vacancy_compensation=salary
            )
            vacancies.append(vacancy)
            print(f'{vacancy.vacancy_title} - {vacancy.vacancy_url} - {vacancy.vacancy_compensation}')
        return vacancies


search_link = SearchRequestLink(clusters="true",
                                enable_snippets="true",
                                ored_clusters="true",
                                schedule="remote",
                                text="IT-рекрутер",
                                order_by="salary_desc",
                                salary="",
                                page=0,
                                search_field="description")

print(search_link.make_search_string_for_hh())
hh_client = HhClient(search_request_link=search_link)
hh_client.collect_vacancy_cards_from_page()

#
# def hh_parse(base_url, headers):
#     jobs = []
#     urls = []
#     pagination = []
#     urls.append(base_url)
#     session = requests.Session()
#     request = session.get(base_url, headers=headers)
#
#     if request.status_code == 200:
#         soup = BeautifulSoup(request.content, 'lxml')
#         try:
#             pagination = soup.find_all('a', attrs={'data-qa': 'pager-page'})
#             count = int(pagination[-1].text)
#             for i in range(count):
#                 url = f'https://spb.hh.ru/search/vacancy?' \
#                       f'clusters=true&' \
#                       f'enable_snippets=true&' \
#                       f'salary=&' \
#                       f'st=searchVacancy&' \
#                       f'text=Агропромышленный&' \
#                       f'page={i}'
#                 print(url)
#                 if url not in urls:
#                     urls.append(url)
#         except Exception as e:
#             print(f'{e} Это что ещё такое?')
#     print(f'количество url = {len(urls)}')
#
#     for url in urls:
#         request = session.get(url, headers=headers)
#         soup = BeautifulSoup(request.content, 'lxml')
#         print(soup)
#         divs = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
#         for div in divs:
#             try:
#                 title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
#                 print(title)
#                 href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})['href']
#                 href_vac = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
#                 # try:
#                 #     contact_datas = soup.find_all('div', {'class': 'vacancy-contacts vacancy-contacts_opened'})
#                 #     name = contact_datas.find('p', attrs={'data-qa': 'vacancy-contacts__fio'}).text
#                 #     tel = contact_datas.find('p', attrs={'data-qa': 'vacancy-contacts__phone'}).text
#                 #     print(name, tel)
#                 # except:
#                 #     pass
#                 jobs.extend(
#                     {'title': title,
#                      'href': f'https://spb.hh.ru{href}',
#                      'href_vac': href_vac
#                      })
#                 print(title)
#             except Exception as e:
#                 print(f'{e} Это что ещё такое?')
#         print(len(jobs))
#     else:
#         print('Error or Done ' + str(request.status_code))
#     return jobs
#
#
# def hh_page_parse(jobs, headers):
#     page_url = jobs.__getitem__(href_vac)
#     session = requests.Session()
#     r_page = session.get(page_url, headers=headers)
#     if r_page.status_code == 200:
#         soup = BeautifulSoup(r_page.content, 'lxml')
#
#
# def file_writer(jobs):
#     with open('parsed_jobs.csv', 'w',  encoding='utf-8') as file:
#         a_pen = csv.writer(file)
#         a_pen.writerow(('Название компании', 'URL компании', 'Название вакансии'))
#         for job in jobs:
#             a_pen.writerow((job['title'], job['href'], job['href_vac']))
#
#
# # get data from each page
# jobs = hh_parse(base_url, headers)
# page_data = hh_page_parse(jobs, headers)
# file_writer(jobs)
