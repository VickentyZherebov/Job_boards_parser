from ParsePages import HabrClient, SearchRequestLink

question = ""
remote = "true"
salary = "350000"
type = "all"
with_salary = "true"
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


habr_client = HabrClient(search_request_link=search_request)
all_vacansies = habr_client.collect_all_vacancy_cards_from_request()

