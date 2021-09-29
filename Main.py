from ParsePages import HabrClient, SearchRequestLink
import datetime

question = ""
remote = ""
salary = ""
type = "all"
with_salary = ""
qid = ""
sort = "salary_desc"
divisions = ""
page_number = 1

search_request = SearchRequestLink(question=question,
                                   remote=remote,
                                   salary=salary,
                                   type=type,
                                   with_salary=with_salary,
                                   qid=qid,
                                   sort=sort,
                                   divisions=divisions,
                                   page_number=page_number)
start_date = datetime.datetime.now()
print(start_date)
make_json = HabrClient(search_request_link=search_request).make_json_from_search_request()
finish_date = datetime.datetime.now()
print(finish_date)
print(f'затрачено времени - {finish_date - start_date}')
