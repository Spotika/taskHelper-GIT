from constants import *
import parseExel
import datetime
import os


def get_users():

    users = {}
    with open(USERSFILEPATH, 'r') as f:
        for i in f.read().split('\n')[:-1]:
            data = i.split()
            users[data[0]] = data[1:]

    
    return users


def set_users(users):

    with open(USERSFILEPATH, 'w') as f:
        for i in users.keys():
            f.write(' '.join((i, *users[i])) + '\n')


def get_timeTable(date):

    timeTable = []
    if str(date) + '.txt' not in os.listdir(TIMETABLESFILEPATH):
        duties = parseExel.get_duties(date)

        with open(TIMETABLESFILEPATH + str(date) + '.txt', 'w') as timeTableFile:
            for duti in duties:
                timeTableFile.write(f'False {duti} None \n')
    
    
    with open(TIMETABLESFILEPATH + str(date) + '.txt', 'r') as timeTableFile:
        for row in timeTableFile.readlines():
            timeTable.append(row.split())

    return timeTable


def set_timeTable(timeTable, date):
    with open(TIMETABLESFILEPATH + str(date) + '.txt', 'w') as timeTableFile:
        for duti in timeTable:
            timeTableFile.write(' '.join(duti) + '\n')
