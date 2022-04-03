# https: // companies.dev.by /
import logging
import datetime
import pprint
from collections import namedtuple
import requests
import csv
from bs4 import BeautifulSoup as bs
from multiprocessing import Pool

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger('hh')

HEADERS = (
    'Компания',
    'Ссылка на компанию',
    'Ссылка на сотрудника',
    'Имя сотрудника',
    'Должность',
)
result = []


class DevByParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'accept': '*/*', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                                               ' AppleWebKit/537.36 (KHTML, like Gecko) '
                                                               'Chrome/78.0.3904.108 Safari/537.36',
                                                               'Accept-Language': 'ru'
                                }

    def get_page(self, url, page: int = None):
        params = {}
        if page and page > 1:
            params['p'] = page
            url = url
        elif page and page == 1:
            url = url
        else:
            url = url

        r = self.session.get(url, params=params)
        return r.text

    def get_blocks(self):
        text = self.get_page(page=2, url='https://companies.dev.by/')
        soup = bs(text, 'lxml')
        container = soup.find('tbody')
        for item in container:
            block = self.parse_block(item=item)
        self.save_results()

    def parse_block(self, item):
        # Выбрать блок со ссылкой
        url_block = item.find('td')
        if type(url_block) != int:
            href = url_block.find('a').get('href')
            company_name = url_block.find('a').get_text()
            company_page_url = 'https://companies.dev.by' + href
            # идем на страницу компании, на странице компании собираем инфо
            text = self.get_page(page=1, url=company_page_url)
            soup = bs(text, 'lxml')
            try:
                container = soup.find('div', attrs={'widget-companies-agents'}).find('ul').find_all('li')
                for item in container:
                    print(item)
                    person_url = item.find('a').get('href')
                    person_info = item.get_text('\n')
                    person_info = list(filter(None, map(lambda i: i.strip(), person_info.split('\n'))))
                    if len(person_info) == 2:
                        person_name, person_position = person_info
                        result.append({
                            'company_name': company_name,
                            'company_page_url': company_page_url,
                            'person_url': person_url,
                            'person_name': person_name,
                            'person_position': person_position
                        })
                # self.save_results()
                # block = self.parse_company_block(item=item, company_name=company_name, company_page_url=company_page_url)
            except:
                pass
            # self.save_results()

    # def parse_company_block(self, item, company_name, company_page_url):
    #     person_url = item.find('a').get('href')
    #     person_info = item.get_text('\n')
    #     person_info = list(filter(None, map(lambda i: i.strip(), person_info.split('\n'))))
    #     if len(person_info) == 2:
    #         person_name, person_position = person_info
    #         result.append({
    #             'company_name': company_name,
    #             'company_page_url': company_page_url,
    #             'person_url': person_url,
    #             'person_name': person_name,
    #             'person_position': person_position
    #         })
    #         self.save_results()
            # logger.debug('%s, %s, %s', person_name, person_position, person_url)
            # logger.info(f'Получили {len(self.result)} элементов')
            # logger.debug('-' * 100)
            # self.save_results()

        # text = self.get_page(page=0, url=person_url)
        # pprint.pprint(text)
        # soup = bs(text, 'lxml')
        # try:
        #     container = soup.find('div', attrs={'island island_rounded'})
        #     try:
        #         e_mail = container.find('div', class_='island-text')
        #         e_mail = e_mail[-1].get('href')
        #         print(e_mail)
        #     except:
        #         pass
        #     try:
        #         telephon = container.find('div', class_= 'island-text').find
        #     except:
        #         pass
        # except:
        #     pass

    def save_results(self):
        path = 'C:/Users/Admin/PycharmProjects/hh/dev_by.csv'
        with open(path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(('Компания', 'Ссылка на компанию', 'Ссылка на сотрудника', 'Имя сотрудника', 'Должность',))
            for item in result:
                print(item)
                writer.writerow((item['company_name'], item['company_page_url'], item['person_url'],
                                 item['person_name'], item['person_position']))


def main():
    p = DevByParser()
    p.get_blocks()


if __name__ == '__main__':
    main()