import datetime


def find_time():
    day_month_year: str = datetime.datetime.today().strftime("%d_%m_%Y")
    hour_minute_second: str = datetime.datetime.today().strftime("%H_%M_%S")
    return day_month_year, hour_minute_second
