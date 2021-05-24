import datetime


class VDateTime:
    def __init__(self, date: str, time: str):
        self.date = date
        self.time = time


def get_now() -> VDateTime:
    today = datetime.datetime.today()
    day_month_year: str = today.strftime("%d_%m_%Y")
    hour_minute_second: str = today.strftime("%H_%M_%S")
    return VDateTime(day_month_year, hour_minute_second)
