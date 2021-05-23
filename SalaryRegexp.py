import re


def find_lower_salary_value(salary):
    low_salary = ''
    if re.search('от', salary):  # проверяем в зепке наличие слова "от "
        first_split = re.split('от ', salary)  # чистим строку от слова "от "
        if re.search('до', first_split[1]):  # проверяем в цене наличие слова "До ", если есть, то:
            second_split = re.split(' до ', first_split[1])  # отрезаем слово "До "
            if re.search('₽', second_split[1]):  # Если находим символ рубля, то:
                low_salary = second_split[0].replace(' ', '')  # убиваем пробелы
            else:
                if re.search('\\$', second_split[1]):  # Если находим символ доллара, то:
                    low_salary = second_split[0].replace(' ', '')  # убиваем пробелы
                else:
                    if re.search('€', second_split[1]):  # Если находим символ евро, то:
                        low_salary = second_split[0].replace(' ', '')  # убиваем пробелы
                    else:
                        print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
                        print('_____________________________________________')
        else:
            if re.search('₽', first_split[1]):
                low_salary = re.split(' ₽', first_split[1])[0].replace(' ', '')
            else:
                if re.search('\\$', first_split[1]):
                    low_salary = re.split(' \\$', first_split[1])[0].replace(' ', '')
                else:
                    if re.search('€', first_split[1]):
                        low_salary = re.split(' €', first_split[1])[0].replace(' ', '')
                    else:
                        print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
    else:
        if re.search('До ', salary):
            first_split = re.split('До ', salary)
            if re.search('₽', first_split[1]):
                low_salary = 'не указано'
            else:
                if re.search('\\$', first_split[1]):
                    low_salary = 'не указано'
                else:
                    if re.search('€', first_split[1]):
                        low_salary = 'не указано'
        else:
            low_salary = 'нет указано'

    return low_salary


def find_high_salary_value(salary):
    high_salary = ''
    if re.search('от', salary):  # проверяем в зепке наличие слова "от "
        first_split = re.split('от ', salary)  # чистим строку от слова "от "
        if re.search('до', first_split[1]):  # проверяем в цене наличие слова "До ", если есть, то:
            second_split = re.split(' до ', first_split[1])  # отрезаем слово "До "
            if re.search('₽', second_split[1]):  # Если находим символ рубля, то:
                high_salary = re.split(' ₽', second_split[1])[0].replace(' ', '')
            else:
                if re.search('\\$', second_split[1]):  # Если находим символ рубля, то:
                    high_salary = re.split(' \\$', second_split[1])[0].replace(' ', '')
                else:
                    if re.search('€', second_split[1]):  # Если находим символ евро, то:
                        high_salary = re.split(' €', second_split[1])[0].replace(' ', '')
                    else:
                        print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
                        print('_____________________________________________')
        else:
            if re.search('₽', first_split[1]):
                high_salary = 'не указано'
            else:
                if re.search('\\$', first_split[1]):
                    high_salary = 'не указано'
                else:
                    if re.search('€', first_split[1]):
                        high_salary = 'не указано'
                    else:
                        print('Какой-то баг - не прошел проверку на рубли, евро и баксы')
    else:
        if re.search('До ', salary):
            first_split = re.split('До ', salary)
            if re.search('₽', first_split[1]):
                high_salary = re.split(' ₽', first_split[1])[0].replace(' ', '')
            else:
                if re.search('\\$', first_split[1]):
                    high_salary = re.split(' \\$', first_split[1])[0].replace(' ', '')
                else:
                    if re.search('€', first_split[1]):
                        high_salary = re.split(' €', first_split[1])[0].replace(' ', '')
        else:
            high_salary = 'не указано'

    return high_salary


def find_salary_currency(salary):
    if re.search('₽', salary):
        currency = 'rub'
    else:
        if re.search('\\$', salary):
            currency = 'usd'
        else:
            if re.search('€', salary):
                currency = 'eur'
            else:
                currency = 'не указано'
    return currency
