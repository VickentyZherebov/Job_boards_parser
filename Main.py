from ParsePages import HabrClient, SearchRequestLink, CompanyParser
import datetime

question = ""
remote = ""
salary = "450000"
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
# make_json = HabrClient(search_request_link=search_request).make_json_from_search_request()
parse_pages = CompanyParser(with_vacancies=1).collect_all_companies_with_vacancies()
finish_date = datetime.datetime.now()
print(finish_date)
print(f'затрачено времени - {finish_date - start_date}')
