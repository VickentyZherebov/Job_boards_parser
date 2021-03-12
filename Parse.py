from bs4 import BeautifulSoup
import csv
# import requests
#
# url = 'https://career.habr.com/vacancies/'
#
# headers = {
#     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
#                   'Chrome/88.0.4324.192 Safari/537.36',
#     'accept': '*/*'}
#
host = 'https://career.habr.com'
#
# req = requests.get(url, headers=headers)
# src = req.text
# # print(src)
#
# with open('index.html', 'w') as file:
#     file.write(src)

with open('vacancies.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Название вакансии",
                     'Название компании',
                     'Ссылка на компанию',
                     'Ссылка на вакансию',
                     'Дата открытия вакансии',
                     'Ссылка на логотип',
                     "Вилка"])

with open('index.html') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')
vacancy_card = soup.find_all(class_='vacancy-card')
for item in vacancy_card:
    title = item.find('a', class_='vacancy-card__title-link').text
    company_title = item.find('a', class_='link-comp link-comp--appearance-dark').text
    company_link = host + item.find('a', class_='link-comp link-comp--appearance-dark').get('href')
    title_link = host + item.find('a', class_='vacancy-card__title-link').get('href')
    date = item.find('div', class_='vacancy-card__date').find('time', class_='basic-date').text
    icon_link = item.find('a', class_='vacancy-card__icon-link').find('img', 'vacancy-card__icon').get('src')
    salary = item.find('div', class_='basic-salary').text
    # skills = []
    skills = item.find('div', class_='vacancy-card__skills').find_all('span', 'preserve-line')
    for skill in skills:
        skill = skill.find('a', class_='link-comp link-comp--appearance-dark').text
        skills.append(skill)
    # vacancy_skills = []
    # for skill in skills:
    #     vacancy_skill = skill.find('href')
    #     vacancy_skills.append(vacancy_skill)
    print(title)
    print(company_title)
    print(company_link)
    print(title_link)
    print(date)
    print(icon_link)
    print(salary)
    # print(skills)
    # print(vacancy_skills)
    print('______________')
    with open('vacancies.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([title, company_title, company_link, title_link, date, icon_link, salary])
