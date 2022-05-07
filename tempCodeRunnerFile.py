
        dayButtonsList.append(types.InlineKeyboardButton(f'{i + 1}', callback_data = f'changeDay_{"-".join(str(currentDate).split("-")[:-1])}-{i+1}'))
    markup.row(*dayButtonsList)

 
    exitButton = types.InlineKeyboardButton('<- Назад', callback_data = 'exit_1')