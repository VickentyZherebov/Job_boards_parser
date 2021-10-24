import requests
import csv
from bs4 import BeautifulSoup as bs

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
base_url = 'https://spb.hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=%D0%90%D0%B3%D1%80%D0%BE%D0%BF%D1%80%D0%BE%D0%BC%D1%8B%D1%88%D0%BB%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9&page=0'


def hh_parse(base_url, headers):
    jobs = []
    urls = []
    pagination = []
    urls.append(base_url)
    session = requests.Session()
    request = session.get(base_url, headers=headers)

    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        try:
            pagination = soup.find_all('a', attrs={'data-qa': 'pager-page'})
            count = int(pagination[-1].text)
            for i in range(count):
                url = f'https://spb.hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=%D0%90%D0%B3%D1%80%D0%BE%D0%BF%D1%80%D0%BE%D0%BC%D1%8B%D1%88%D0%BB%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9&page={i}'
                if url not in urls:
                    urls.append(url)

        except:
            pass

    for url in urls:
        request = session.get(url, headers=headers)
        soup = bs(request.content, 'lxml')


        divs = soup.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
        for div in divs:
            try:
                title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})['href']
                href_vac = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                # try:
                #     contact_datas = soup.find_all('div', {'class': 'vacancy-contacts vacancy-contacts_opened'})
                #     name = contact_datas.find('p', attrs={'data-qa': 'vacancy-contacts__fio'}).text
                #     tel = contact_datas.find('p', attrs={'data-qa': 'vacancy-contacts__phone'}).text
                #     print(name, tel)
                # except:
                #     pass
                jobs.append({
                    'title': title,
                    'href': f'https://spb.hh.ru{href}',
                    'href_vac': href_vac
                })

            except:
                pass



        print(len(jobs))
    else:
        print('Error or Done ' + str(request.status_code))
    return jobs


def hh_page_parse(jobs, headers):
    page_url = jobs.__getitem__(href_vac)
    session = requests.Session()
    r_page = session.get(page_url, headers=headers)
    if r_page.status_code == 200:
        soup = bs(r_page.content, 'lxml')





def file_writer(jobs):
    with open('parsed_jobs.csv', 'w',  encoding='utf-8') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('Название компании', 'URL компании', 'Название вакансии'))
        for job in jobs:
            a_pen.writerow((job['title'], job['href'], job['href_vac']))

# get data from each page

jobs = hh_parse(base_url, headers)
page_data = hh_page_parse(jobs, headers)
file_writer(jobs)
