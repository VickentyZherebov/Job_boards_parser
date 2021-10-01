from ParsePages import HabrClient, SearchRequestLink
import datetime

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
#
# number_of_urls = HabrClient(search_request_link=search_request).get_page().find_number_of_search_pages()
# print(number_of_urls)
#
#
# url_list = HabrClient(search_request_link=search_request).make_urls_list()
# # print(url_list)
# # # make_json = HabrClient(search_request_link=search_request).make_json_from_search_request()
# finish_date = datetime.datetime.now()
# # print(finish_date)
# print(f'затрачено времени - {finish_date - start_date}')

# data_from_all_pages = HabrClient(search_request_link=search_request).get_data_from_all_pages()
all_vacs = HabrClient(search_request_link=search_request).collect_vacancy_cards_from_page_2()
print(len(all_vacs))


for vac in range(1, len(all_vacs) + 1):
    print(f'{vac}. {all_vacs[vac - 1].vacancy_link}')

finish_date = datetime.datetime.now()
print(f'затрачено времени - {finish_date - start_date}')

