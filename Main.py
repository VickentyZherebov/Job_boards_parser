from ParsePages import find_number_of_search_pages, collecting_vacancies_data, parse_vacancies_data
from timevars import find_time
from WorkWithCSV import make_csv_file, open_csv_file

dmy = find_time()[0]
hms = find_time()[1]
nosp = find_number_of_search_pages()

make_csv_file()
vacancy_cards = collecting_vacancies_data(day_month_year=dmy, hour_minute_second=hms, number_of_search_pages=nosp)
parse_vacancies_data(vacancy_data=vacancy_cards)
open_csv_file()
