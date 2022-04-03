import sqlite3
from sqlite3 import Connection

connection = sqlite3.connect(r'//SavedData/SQLite3DataBase/HabrData.db')
cursor = connection.cursor()


def create_db() -> Connection:
    cursor.execute("""CREATE TABLE IF NOT EXISTS kotlin_vacancies(                 
        low_salary INTEGER,       
        high_salary INTEGER,             
        currency TEXT,           
        date_of_publication TEXT,
        logo_link TEXT,                   
        company_link TEXT,                   
        company_name TEXT,                   
        vacancy_link TEXT PRIMARY KEY,                  
        vacancy_name TEXT,
        FOREIGN KEY (company_link) REFERENCES companies (company_link))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS ios_companies(
        size TEXT,
        location TEXT,
        vacancies_count TEXT,
        open_vacancies_link TEXT,
        skills TEXT,
        about TEXT,
        rating TEXT,
        company_link TEXT PRIMARY KEY,
        company_name TEXT,
        logo_link TEXT)""")
    connection.commit()
    return connection
