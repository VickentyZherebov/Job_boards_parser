from HabraParser import HabrClient, VacancySearchRequest, CompanyParser
import datetime

question = "ios"
remote = ""
salary = ""
search_type = "all"
with_salary = ""
qid = ""
sort = "salary_desc"
divisions = ""
skills = ""
page_number = 1

search_request = VacancySearchRequest(question=question,
                                      remote=remote,
                                      salary=salary,
                                      search_type=search_type,
                                      with_salary=with_salary,
                                      qid=qid,
                                      sort=sort,
                                      divisions=divisions,
                                      skills=skills)
start_date = datetime.datetime.now()
make_json = HabrClient(search_request_link=search_request).make_json_from_search_request()
# parse_pages = CompanyParser(with_vacancies="").collect_all_companies_with_vacancies()
finish_date = datetime.datetime.now()
print(f'затрачено времени - {finish_date - start_date}')
