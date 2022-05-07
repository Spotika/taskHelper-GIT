from parso import parse
from telebot import TeleBot
from telebot import types
# from telegram import ParseMode
import methods
from constants import *
import parseExel
import datetime
import dataBase
# import methods
import os


secretKey = '' # Insert SK
TOKEN = 'Test' # Insert Token
Bot = TeleBot(TOKEN)


USERS = dataBase.get_users()


waitingSecretKey = []

date = datetime.date.today()
timeTable = dataBase.get_timeTable(date)




'''
Bot methods:
'''

# Starting bot
@Bot.message_handler(commands = ['start'])
def start(message, UID = None):
    global USERS

    # delete last message
    try:
        Bot.delete_message(message.chat.id, message.id - 1)
        Bot.delete_message(message.chat.id, message.id)
    except:
        pass


    if UID == None:
        userId = str(message.from_user.id)
    else:
        userId = str(UID)
    username = message.from_user.first_name

    # Registration
    if userId in USERS.keys():
        pass
    else:
        Bot.send_message(message.chat.id, f'Привет, {username}')
        USERS[userId] = [username, 'user']


    # Reset to default layout
    markup = types.InlineKeyboardMarkup()
    timeTableViewButton = types.InlineKeyboardButton('Просмотреть задачи', callback_data = 'timeTableView')
    



    # show stayed personal duties (for casual)
    timeTableDutiesStayed = types.InlineKeyboardButton('Оставшиеся задачи', callback_data = 'timeTabledutiesStayed')

    # Statisticks about casuals users (for root)
    timeTableStatistics = types.InlineKeyboardButton('Статистика дня', callback_data = 'timeTableStatistics')

    # reassign duties of users
    timeTableReassignButton = types.InlineKeyboardButton('Переназначить задачи', callback_data = 'timeTableReassign')

    # show timeTable for every datetime
    timeTableViewByDayButton = types.InlineKeyboardButton('Полная статистика', callback_data = 'timeTableViewByDay')



    # add to markup
    markup.add(timeTableViewButton)
    if USERS[userId][1] != 'root':
        markup.add(timeTableDutiesStayed)
    else:
        markup.add(timeTableStatistics)
    # markup.add(timeTableDutiesStayed)
    # markup.add(timeTableStatistics)
    markup.add(timeTableReassignButton)
    markup.add(timeTableViewByDayButton)
    


    Bot.send_message(message.chat.id, f'С чего начать?', reply_markup = markup)


# Message interception
@Bot.message_handler(content_types = ['text'])
def handle_text(message):
    global USERS

    if message.text.split()[0] == 'SK:':

        if message.text.split()[1] == secretKey:
            Bot.send_message(message.chat.id, 'Права выданы успешно')
            USERS[str(message.from_user.id)][1] = 'root'
        else:
            Bot.send_message(message.chat.id, 'Ошибка в ключе')


# view and redact Time Table
@Bot.callback_query_handler(lambda call: call.data == "timeTableView")
def callback_handler_timeTableView(call):
    global date
    global timeTable
    global USERS

    try:
        # delete last message
        Bot.delete_message(call.message.chat.id, call.message.id)
    except:
        pass
    

    # getting and update time table
    today = datetime.date.today()
    if today != date:
        date = today
        timeTable = dataBase.get_timeTable(date)

    
    # create message of time table
    message = ''
    done = '✅'
    notDone = '❌'
    index = 1
    for duti in timeTable:
        message += f'{str(index)}. '

        if duti[0] == 'True':
            message += done + ' '
        else:
            message += notDone + ' '
        performing = 'Никто'
        if duti[2] != 'None':
            performing = USERS[duti[2]][0]
        message += duti[1].replace('_', ' ') + ' - <i><b>' + performing + '</b></i>'
        message += '\n'
        index += 1
    


    # markup for redacting
    markup = types.InlineKeyboardMarkup(row_width = 5)

    # buttons for redact time table
    acceptDutiesButtonList = []
    for i in range(1, len(timeTable) + 1):
        sign = '+'
        if timeTable[i - 1][0] == 'True':
            sign = '-'

        acceptDutiesButtonList.append(types.InlineKeyboardButton(f'{sign}{i}', callback_data = f'REDACT_{i}'))
    markup.row(*acceptDutiesButtonList)


    exitButton = types.InlineKeyboardButton('<- Назад', callback_data = 'exit_1') # come back to start layout
    markup.add(exitButton)

    # sending
    Bot.send_message(call.message.chat.id, message, parse_mode = 'HTML', reply_markup = markup)

    # Alert
    Bot.answer_callback_query(callback_query_id  = call.id, show_alert = False, text = "Показаны задачи")


# this function redirect user to start
@Bot.callback_query_handler(lambda call: call.data.split('_')[0] == 'exit')
def callback_handler_exit(call):


    for messageId in range(call.message.id, call.message.id + int(call.data.split('_')[1]) + 1):
        try:
            # delete latest messages
            Bot.delete_message(call.message.chat.id, messageId)
        except:
            pass

    # redirect to start
    start(call.message, UID = call.from_user.id)


# interception queryes for redacting time table
@Bot.callback_query_handler(lambda call: call.data.split('_')[0] == 'REDACT')
def callback_handler_redactTimeTable(call):
    # delete last message
    Bot.delete_message(call.message.chat.id, call.message.id)


    index = int(call.data.split('_')[1]) - 1

    # redact
    if timeTable[index][0] == 'True':
        timeTable[index][0] = 'False'
    else:
        timeTable[index][0] = 'True'


    # redirect to view time table
    callback_handler_timeTableView(call)



# show stayed duti personale
@Bot.callback_query_handler(lambda call: call.data == 'timeTabledutiesStayed')
def callback_handler_dutiesStayed(call):
    global USERS

    # delete last message
    Bot.delete_message(call.message.chat.id, call.message.id)

    # check for personal duties
    message = ''
    index = 1
    for duti in timeTable:
        if duti[0] == 'False':
            if str(call.from_user.id) == duti[2]:
                message += f'{index}. {duti[1].replace("_", " ")}\n'
                index += 1
    

    markup = types.InlineKeyboardMarkup()

    exitButton = types.InlineKeyboardButton('<- Назад', callback_data = 'exit_1')
    markup.add(exitButton)

    if message == '':
        index = 1
        for duti in timeTable:
            if duti[0] == 'False':
                if  'None' == duti[2]:
                    message += f'{index}. {duti[1].replace("_", " ")}\n'
                    index += 1
        if message == '':
            message = 'Задач нет. Радуйся!'
        else:
            message = 'Таких задач нет, но есть те, за которые никто не взялся: \n' + message
    
    Bot.send_message(call.message.chat.id, message, reply_markup = markup)


# reassign users duties
@Bot.callback_query_handler(lambda call: call.data == 'timeTableReassign')
def callback_handler_timeTableReassign(call):
    global USER
    global timeTable

    # delete last message
    Bot.delete_message(call.message.chat.id, call.message.id)


    markup = types.InlineKeyboardMarkup()

    # while button is pressed the duties list will be deleted
    exitButton = types.InlineKeyboardButton('<- Завершить перераспределение', callback_data = f'exit_{len(timeTable) + 1}')

    markup.add(exitButton)
    Bot.send_message(call.message.chat.id, 'Переназначение...', reply_markup = markup)

    
    # list of duties
    index = 1
    for duti in timeTable:
        message = ''
        performing = 'Никто'
        if duti[2] != 'None':
            performing = USERS[duti[2]][0]
        message = f'{index}. {duti[1].replace("_", " ")} - <i><b>{performing}</b></i>\n'

        markup = types.InlineKeyboardMarkup()

        performers = []
        for userId in USERS.keys():
            if USERS[userId][1] != 'root':
                performers.append(types.InlineKeyboardButton(f'{USERS[userId][0]}', callback_data = f'REASSIGN_{userId}_{index - 1}'))
            

        markup.row(*performers)
        # choose performer
        Bot.send_message(call.message.chat.id, message, parse_mode = 'HTML', reply_markup = markup)

        index += 1


# reassign duti by user ud and pressing inline button
@Bot.callback_query_handler(lambda call: call.data.split('_')[0] == 'REASSIGN')
def callback_handler_Reassign(call):
    global USERS
    global timeTable


    # reassign duti by user id
    index = int(call.data.split('_')[2])
    userId = call.data.split('_')[1]
    timeTable[index][2] = str(userId)

    # redacting message 
    try:
        Bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.id, 
        text = f'{index + 1}. {timeTable[index][1].replace("_", " ")} - <i><b>{USERS[userId][0]}</b></i>', parse_mode = 'HTML', reply_markup = call.message.reply_markup)
    except:
        pass


@Bot.callback_query_handler(lambda call: call.data == 'timeTableStatistics')
def callback_handler_timeTableStatistics(call):
    global USERS
    global timeTable


    # delete last message
    Bot.delete_message(call.message.chat.id, call.message.id)


    message = ''

    for userId in USERS.keys():
        user = USERS[userId]
        flag = False
        if user[1] != 'root':
            message += f'<i><b>{user[0]}</b></i>:\n'
            index = 1

            for duti in timeTable:  
                if duti[2] == userId and duti[0] == 'False':
                    message += f'{index}. {duti[1].replace("_", " ")}\n'
                    index += 1
                    flag = True
            if not flag:
                message += f'<b>Все задачи выполнены!</b>'
        message += '\n'    

    markup = types.InlineKeyboardMarkup()
    exitButton = types.InlineKeyboardButton('<- Назад', callback_data = 'exit_1')
    markup.add(exitButton)


    Bot.send_message(call.message.chat.id, message, parse_mode = 'HTML', reply_markup = markup )


# show timeTable by day (if exists) or list duties by day 
@Bot.callback_query_handler(lambda call: call.data.split('_')[0] == 'timeTableViewByDay')
def callback_handler_timeTableViewByDay(call, requestData = None):
    global date
    global USERS

    # delete last message
    Bot.delete_message(call.message.chat.id, call.message.id)



    # get date from callback data or take today
    currentDate = requestData
    if currentDate == None:
        if len(call.data.split('_')) == 1:
            currentDate = date
        else:
            currentDate = datetime.datetime(*map(int, call.data.split('_')[1].split('-')))
    else:
        currentDate = datetime.datetime(*map(int, currentDate.split('-')))


    # create message
    message = f'<b>{str(currentDate).split()[0]}</b>\n'


    if str(currentDate).split()[0] + '.txt' in os.listdir(TIMETABLESFILEPATH):
        # usual time table
        if str(currentDate).split()[0] == str(date).split()[0]:
            timeTable_ = timeTable
        else:
            timeTable_ = dataBase.get_timeTable(str(currentDate).split()[0])
        index = 1
        done = '✅'
        notDone = '❌'
        for duti in timeTable_:
            message += f"{index}. "
            if duti[0] == 'True':
                message += f'{done} '
            else:
                message += f'{notDone} '
            
            message += f"{duti[1].replace('_', ' ')} - "

            if duti[2] == 'None':
                message += '<b><i>Никто</i></b>\n'
            else:
                message += f'<b><i>{USERS[duti[2]][0]}</i></b>\n'
            index += 1
    else:
        # det duties without time table
        duties = parseExel.get_duties(currentDate)

        index = 1
        for duti in duties:
            message += f"{index}. {duti.replace('_', ' ')}\n"
            index += 1




    # markup

    # buttons changing month
    markup = types.InlineKeyboardMarkup(row_width = 7)
    arrowLeftButton = types.InlineKeyboardButton('<-', callback_data = f'changeMonth_prev_{str(currentDate).split()[0]}')
    arrowRightButton = types.InlineKeyboardButton('->', callback_data = f'changeMonth_next_{str(currentDate).split()[0]}')
    monthInfoButton = types.InlineKeyboardButton(str(MONTH[int(str(currentDate).split()[0].split('-')[1])]) + f' {str(currentDate).split()[0].split("-")[0]}', callback_data = 'None')
    markup.row(arrowLeftButton, monthInfoButton, arrowRightButton)


    # buttons, changing days
    numOfDays = methods.num_of_days(int((str(currentDate).split()[0]).split('-')[1]))
    dayButtonsList = []

    for i in range(numOfDays):
        dayButtonsList.append(types.InlineKeyboardButton(f'{i + 1}', callback_data = f'changeDay_{"-".join(str(currentDate).split("-")[:-1])}-{i+1}'))
    markup.row(*dayButtonsList)

 
    exitButton = types.InlineKeyboardButton('<- Назад', callback_data = 'exit_1')
    markup.add(exitButton)



    Bot.send_message(call.message.chat.id, message, parse_mode = 'HTML', reply_markup = markup)


# changing day for callback_handler_timeTableViewByDay
@Bot.callback_query_handler(lambda call: call.data.split('_')[0] == 'changeDay')
def callback_handler_changeDay(call):

    # # delete last message
    # Bot.delete_message(call.message.chat.id, call.message.id)

    dayToChange = call.data.split('_')[1]
    callback_handler_timeTableViewByDay(call, dayToChange)



@Bot.callback_query_handler(lambda call: call.data.split('_')[0] == 'changeMonth')
def callback_handler_changeMonth(call):
    
    command = call.data.split('_')[1]
    dateToChange = list(map(int, call.data.split('_')[2].split('-')))

    if command == 'prev':
        dateToChange[2] = 1
        if dateToChange[1] == 1:
            dateToChange[1] = 12
            dateToChange[0] -= 1
        else:
            dateToChange[1] -= 1
    elif command == 'next':
        dateToChange[2] = 1
        if dateToChange[1] == 12:
            dateToChange[1] = 1
            dateToChange[0] += 1
        else:
            dateToChange[1] += 1

    callback_handler_timeTableViewByDay(call, '-'.join(list(map(str, dateToChange))))


'''
Starting bot polling
'''
try:
    Bot.polling(none_stop = True, interval = 0)
finally:
    # saving data about users
    dataBase.set_users(USERS)
    # saving data about time table
    dataBase.set_timeTable(timeTable, date)