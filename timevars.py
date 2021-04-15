import datetime


def dmyhms():
    dmy: str = datetime.datetime.today().strftime("%d_%m_%Y")
    hms: str = datetime.datetime.today().strftime("%H_%M_%S")
    return dmy, hms
