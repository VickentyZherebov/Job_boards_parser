from contextlib import closing

from DataBase.CreateDB import create_db
from HabraParser import VacancySearchRequest, CompanyCardMini, HabrClient, VacancyCardMini
import datetime
from sqlite3 import Connection

request = VacancySearchRequest(question="",
                               remote="",
                               salary="",
                               search_type="all",
                               with_salary="",
                               qid="",
                               sort="salary_desc",
                               divisions="",
                               skills=239)
start_date = datetime.datetime.now()
print(start_date)


def import_habr_vacancies(search_request: VacancySearchRequest):
    vacancies = []
    connection = create_db()
    # todo найти последнюю добавленную вакансию
    with closing(HabrClient()) as habr_client:
        page_count = habr_client.get_vacancy_list_page(search_request, page_number=1).count_search_pages()
        for page in range(page_count):
            vacancy_list_page = habr_client.get_vacancy_list_page(search_request, page_number=page + 1)
            collected_data = vacancy_list_page.collect_vacancy_cards_from_page()
            vacancies.extend(collected_data)
            # todo проверить collected_data не содержит вакансии с линком самой последней вакансией добавленной в прошлый раз, если содержит то остановиться
    save_vacancies(connection, vacancies)


def import_habr_companies():
    companies = []
    connection = create_db()
    # todo найти последнюю добавленную вакансию
    with closing(HabrClient()) as habr_client:
        page_count = habr_client.get_company_list_page(with_vacancies=1, page_number=1).count_search_pages()
        print(f'Count of companies pages = {page_count}')
        for page in range(page_count):
            company_list_page = habr_client.get_company_list_page(with_vacancies=1, page_number=page + 1)
            collected_data = company_list_page.collect_company_cards_from_page()
            companies.extend(collected_data)
            print(f'parsed page № {page + 1}')
    save_vacancies(connection, companies)


def save_vacancies(db_connection: Connection, vacancies: [VacancyCardMini]):
    with closing(db_connection.cursor()) as cursor:
        for vacancy in vacancies:
            cursor.execute("INSERT OR IGNORE INTO kotlin_vacancies "
                           "(low_salary, "
                           "high_salary, "
                           "currency, "
                           "date_of_publication, "
                           "logo_link, "
                           "company_link, "
                           "company_name, "
                           "vacancy_link, "
                           "vacancy_name"") VALUES (?,?,?,?,?,?,?,?,?);",
                           [vacancy.low_salary,
                            vacancy.high_salary,
                            vacancy.currency,
                            vacancy.date_of_publication,
                            vacancy.logo_link,
                            vacancy.company_link,
                            vacancy.company_name,
                            vacancy.vacancy_link,
                            vacancy.vacancy_name])
    db_connection.commit()


def save_companies(db_connection: Connection, companies: [CompanyCardMini]):
    # @todo разобраться как работает closing
    with closing(db_connection.cursor()) as cursor:
        for page in range(len(companies)):
            company = companies[page]
            if cursor.empty:
                cursor.execute("INSERT INTO companies ("
                               "size, "
                               "location, "
                               "vacancies_count, "
                               "open_vacancies_link, "
                               "skills, "
                               "about, "
                               "rating, "
                               "company_link, "
                               "company_name, "
                               "logo_link) VALUES (?,?,?,?,?,?,?,?,?,?);",
                               [company.size,
                                company.location,
                                company.vacancies_count,
                                company.open_vacancies_link,
                                "Пропуск",
                                company.about,
                                company.rating,
                                company.company_link,
                                company.company_name,
                                company.logo_link])
                print(f'пишу в базу данных - {page + 1}')
            else:
                cursor.execute("UPDATE INTO companies ("
                               "size, "
                               "location, "
                               "vacancies_count, "
                               "open_vacancies_link, "
                               "skills, "
                               "about, "
                               "rating, "
                               "company_link, "
                               "company_name, "
                               "logo_link) VALUES (?,?,?,?,?,?,?,?,?,?);",
                               [company.size,
                                company.location,
                                company.vacancies_count,
                                company.open_vacancies_link,
                                "Пропуск",
                                company.about,
                                company.rating,
                                company.company_link,
                                company.company_name,
                                company.logo_link])
                print(f'пишу в базу данных - {page + 1}')
        db_connection.commit()


import_habr_vacancies(request)
# import_habr_companies()

finish_date = datetime.datetime.now() - start_date
print(finish_date)
