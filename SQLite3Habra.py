import sqlite3
from HabraParser import HabrClient, SearchRequestLink, CompanyParser
import datetime

vacancies_db = sqlite3.connect('vacancies.db')
companies_db = sqlite3.connect('companies.db')
cursor_vac = vacancies_db.cursor()
cursor_comp = companies_db.cursor()

cursor_vac.execute("""CREATE TABLE IF NOT EXISTS vacancies(
    currency TEXT,                   
    high_salary TEXT,                   
    low_salary TEXT,                   
    salary TEXT,                   
    date_of_publication TEXT,
    logo_link TEXT,                   
    company_link TEXT,                   
    company_name TEXT,                   
    vacancy_link TEXT PRIMARY KEY,                  
    vacancy_name TEXT,
    FOREIGN KEY (company_link) REFERENCES companies (company_link))""")

vacancies_db.commit()

cursor_comp.execute("""CREATE TABLE IF NOT EXISTS companies(
    size TEXT,
    location TEXT,
    vacancies_count TEXT,
    open_vacancies_link TEXT,
    skills TEXT,
    about TEXT,
    rating TEXT,
    company_link TEXT PRIMARY KEY,
    company_name TEXT,
    logo_link TEXT)""")
companies_db.commit()

question = ""
remote = ""
salary = ""
search_type = "all"
with_salary = ""
qid = ""
sort = "salary_desc"
divisions = ""
page_number = 1

search_request = SearchRequestLink(question=question,
                                   remote=remote,
                                   salary=salary,
                                   search_type=search_type,
                                   with_salary=with_salary,
                                   qid=qid,
                                   sort=sort,
                                   divisions=divisions,
                                   page_number=page_number)
start_date = datetime.datetime.now()
print(start_date)
# collect_all_vacancies = HabrClient(search_request_link=search_request).collect_all_vacancy_cards_from_request()
collect_all_companies = CompanyParser(with_vacancies=1).collect_all_companies_with_vacancies()

# for page in range(1, len(collect_all_vacancies) + 1):
#     number_of_vacancies = len(collect_all_vacancies[page - 1])
#     for vacancy in range(1, number_of_vacancies + 1):
#         cursor_vac.execute("INSERT OR IGNORE INTO vacancies VALUES (?,?,?,?,?,?,?,?,?,?);",
#                            [collect_all_vacancies[page - 1][vacancy - 1].currency,
#                             collect_all_vacancies[page - 1][vacancy - 1].high_salary,
#                             collect_all_vacancies[page - 1][vacancy - 1].low_salary,
#                             collect_all_vacancies[page - 1][vacancy - 1].salary,
#                             collect_all_vacancies[page - 1][vacancy - 1].date_of_publication,
#                             collect_all_vacancies[page - 1][vacancy - 1].logo_link,
#                             collect_all_vacancies[page - 1][vacancy - 1].company_link,
#                             collect_all_vacancies[page - 1][vacancy - 1].company_name,
#                             collect_all_vacancies[page - 1][vacancy - 1].vacancy_link,
#                             collect_all_vacancies[page - 1][vacancy - 1].vacancy_name])
# vacancies_db.commit()

for page in range(1, len(collect_all_companies) + 1):
    cursor_comp.execute("INSERT OR IGNORE INTO companies VALUES (?,?,?,?,?,?,?,?,?,?);",
                        [collect_all_companies[page - 1].size,
                         collect_all_companies[page - 1].location,
                         collect_all_companies[page - 1].vacancies_count,
                         collect_all_companies[page - 1].open_vacancies_link,
                         "Пропуск",
                         collect_all_companies[page - 1].about,
                         collect_all_companies[page - 1].rating,
                         collect_all_companies[page - 1].company_link,
                         collect_all_companies[page - 1].company_name,
                         collect_all_companies[page - 1].logo_link])
companies_db.commit()

# cursor_vac.execute("""DELETE FROM vacancies WHERE vacancy_link IS NULL OR trim(vacancy_link) = ''""")
# vacancies_db.commit()
