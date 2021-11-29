import sqlite3
from xlsxwriter.workbook import Workbook
workbook = Workbook('MentalGrowth.xlsx')
worksheet = workbook.add_worksheet()

conn = sqlite3.connect('companies.db')
c = conn.cursor()
c.execute("select * from companies where company_name == 'MentalGrowth'")
rows = c.fetchall()

m = 0
for row in rows:
    m += 1
    print(f"{m}. {row}")

# my_select = c.execute("select * from abc ")
for i, row in enumerate(rows):
    for j, value in enumerate(row):
        worksheet.write(i, j, value)
workbook.close()
