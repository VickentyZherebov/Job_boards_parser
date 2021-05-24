from ParsePages import HabrClient
# from timevars import get_now
# from WorkWithCSV import make_csv_file, open_csv_file

habr_client = HabrClient
number_of_pages = habr_client.load_vacancies(self=HabrClient)
print(len(number_of_pages))
# now = get_now()
# habr_client = HabrClient()
# number_of_pages = habr_client.get_page(1).find_number_of_search_pages()
# print(number_of_pages)
#
# make_csv_file()
# vacancies = []
# vacancies = HabrClient.load_vacancies()
# # for page_number in range(1, number_of_pages + 1):
# #     page = habr_client.get_page(page_number)
# #     vacancies.extend(page.find_vacancies('https://career.habr.com'))
#
# vacancy_cards = collecting_vacancies_data(
#     day_month_year=now.date,
#     hour_minute_second=now.time,
#     number_of_search_pages=number_of_pages)
# parse_vacancies_data(vacancy_cards=vacancy_cards)
# open_csv_file()
