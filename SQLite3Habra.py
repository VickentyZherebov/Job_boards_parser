from contextlib import closing

from CreateDB import create_db
from HabraParser import VacancySearchRequest, CompanyParser, CompanyCardMini, HabrClient, VacancyCardMini
import datetime
from sqlite3 import Connection

question = ""
remote = ""
salary = ""
search_type = "all"
with_salary = ""
qid = ""
sort = "salary_desc"
divisions = ""
page_number = 1

search_request = VacancySearchRequest(question=question,
                                      remote=remote,
                                      salary=salary,
                                      search_type=search_type,
                                      with_salary=with_salary,
                                      qid=qid,
                                      sort=sort,
                                      divisions=divisions)
start_date = datetime.datetime.now()
print(start_date)


def import_habr_vacancies(self, search_request: VacancySearchRequest):
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


def save_vacancies(db_connection: Connection, vacancies: [VacancyCardMini]):
    with closing(db_connection.cursor()) as cursor:
        for vacancy in vacancies:
            cursor.execute("INSERT OR IGNORE INTO vacancies "
                           "(currency, "
                           "high_salary, "
                           "low_salary, "
                           "salary, "
                           "date_of_publication, "
                           "logo_link, "
                           "company_link, "
                           "company_name, "
                           "vacancy_link, "
                           "vacancy_name"") VALUES (?,?,?,?,?,?,?,?,?,?);",
                           [vacancy.currency,
                            vacancy.salary_range.high_salary,
                            vacancy.salary_range.low_salary,
                            vacancy.salary_range.salary,
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
            cursor.execute("INSERT OR IGNORE INTO companies VALUES (?,?,?,?,?,?,?,?,?,?);", [
                company.size,
                company.location,
                company.vacancies_count,
                company.open_vacancies_link,
                "Пропуск",
                company.about,
                company.rating,
                company.company_link,
                company.company_name,
                company.logo_link
            ])
            print(f'пишу в базу данных - {page + 1}')
        db_connection.commit()
