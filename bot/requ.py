from models import *
import datetime

def get_date(delta = 5, ignore_weekends = True, dict = False):
    x = 0
    days = {}
    dict_days = []
    day = datetime.date.today()

    while x != delta:
        day = day + datetime.timedelta(days=1)

        if day.isoweekday() > 5 and ignore_weekends == True:
            continue

        else:
            x += 1
            s = f'{day.day}.{day.month}.{day.year}'
            days.update({x : s})
            dict_days.append(s)


    return days if not dict else dict_days


