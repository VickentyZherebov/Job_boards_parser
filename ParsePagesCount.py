from bs4 import BeautifulSoup
from selenium import webdriver
import re
import math
import datetime

chromedriver = '/Users/vikentijzerebov/Downloads/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(chromedriver, options=options)


def find_number_of_search_pages(self, pn, q, r, u, s, ws, t="all"):
    """ Функция помогает найти количество страниц в поисковой выдаче с https://career.habr.com/vacancies
    для того, чтобы знать точное количество страниц для парсинга
    :param s:
    :param ws:
    :param u: урл
    :param self: я хз че сюда писать
    :param pn: номер страницы с которой сдирается html код
    :param q: любой поисковой запрос на сайте, для поиска вакансий
    :param r: можно ли работать удаленно? Если да, то пиши значение true
    :param t: я хз че это такое, постоянно стоит all
    :return: Количество страниц с вакансиями, соответствующих запросу
    """
    print('Отправляю поисковой запрос на Хабре')
    browser.get(u + f'?page={pn}&q={q}&remote={r}&salary={s}&type={t}&with_salary={ws}')
    print('Анализирую HTML код')
    required_html = browser.page_source
    soup = BeautifulSoup(required_html, 'html5lib')
    find_class = "search-total disable-font-boosting search-total--appearance-search-panel"
    find_count_string = soup.find('div', class_=find_class).text
    find_count_string = int(re.findall('\\d+', find_count_string)[0])
    print(f'Твоему запросу соответстует {find_count_string} вакансий')
    number_of_search_pages = math.ceil(int(find_count_string) / 25)
    print(f'Это {number_of_search_pages} страниц надо спарсить, но не парься, я скоро все сделаю')
    dmy = datetime.datetime.today().strftime("%d_%m_%Y")
    hms = datetime.datetime.today().strftime("%H_%M_%S")
    html_name = f"html_{pn}_{dmy}_{hms}.html"
    html_file = open(f'{dmy}/{html_name}', 'w')
    html_file.write(f'{soup}')
    return number_of_search_pages
