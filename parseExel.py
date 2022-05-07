import os
import math
# from this import d
import time
import pandas
import datetime
from constants import *


def get_duties(date, filePath = 'excel/schedule.xlsx'):
    xl = pandas.ExcelFile(filePath)
    xl = xl.parse('Sheet1')


    # today date & weekday
    today = date
    weekday = WEEKDAYS[today.weekday() + 1]
    weekday_N = (today.timetuple()[2] // 7 + 1)

    dayColl = f'{weekday}.{weekday_N}'


    # getting coll of duties
    coll = list(xl[dayColl])
    DUTIES_ = list(xl['Обязанности'])
    duties = [DUTIES_[i] for i in range(len(coll)) if coll[i] == 'x']

    return duties


# print(get_duties(datetime.date(2022, 5, 18)))
