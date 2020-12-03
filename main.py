import json
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from requ import *

config = json.load(open('config.json', encoding='utf-8'))
replicates = config['replicates']
token = config['token']

vk_session = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk_session)


#keyboard = VkKeyboard(one_time=True)
#keyboard.add_button('Привет', color=VkKeyboardColor.NEGATIVE)

time_keyboard = VkKeyboard(one_time=True)
time_keyboard.add_button(config['time'][0], color=VkKeyboardColor.PRIMARY)
time_keyboard.add_button(config['time'][1], color=VkKeyboardColor.PRIMARY)

default_keyboard = VkKeyboard(one_time=True)
default_keyboard.add_button(replicates['change_date_and_time'], color=VkKeyboardColor.PRIMARY)

def send_message(user_id, message, keyboard = None):
    vk_session.get_api().messages.send(
        keyboard = keyboard.get_keyboard() if keyboard != None else None,
        user_id = user_id,
        message = message,
        random_id = get_random_id()
    )


def get_keyboard_date():
    keyboard = VkKeyboard(one_time=True)

    days = get_date(delta=config['days_next'])

    for x in days:

        keyboard.add_button(days[x], color=VkKeyboardColor.PRIMARY)

        if x % 3 == 0: keyboard.add_line()

    return keyboard

if __name__ == '__main__':
    for event in longpoll.listen():
        #Проверка на новое сообщение
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            today = datetime.datetime.today().date()
            str_today = f'{today.day}.{today.month}.{today.year}'
            user_id = event.user_id
            user_info = vk_session.method('users.get', {'user_ids' : user_id,'fields' : 'domain'})[0]
            text = event.text


            #Если пользователь пишет впервые - предложить выбрать дату
            if not Users.select().where(Users.user_id == user_id).exists():
                #Добавление в бд

                user = Users.create(user_id = user_id, state = 'select_date')

                #Отправка сообещения
                send_message(user_id ,f'{replicates["first_message"]}\n{replicates["select_date"]}', get_keyboard_date())

            #Если нет - взять юзера из дб
            else:
                user = Users.get(Users.user_id == user_id)

                #Проверки на стейт
                if user.state == 'select_date':
                    #Если юзер жмет не по кнопочкам
                    if text not in get_date(delta=config['days_next'], dict=True):
                        send_message(user_id, replicates['input_error'], get_keyboard_date())
                        continue

                    user.date = text
                    user.state = 'select_time'
                    user.save()

                    send_message(user_id, replicates['select_time'], time_keyboard)


                elif user.state == 'select_time':
                    # Если юзер жмет не по кнопочкам
                    if text not in config['time']:
                        send_message(user_id, replicates['input_error'], time_keyboard)
                        continue

                    user.time = text
                    user.state = 'null'
                    user.save()

                    answer = replicates['final'].replace('{DATE}', f'{user.date} в {user.time}').replace('{ADDRESS}', config['address'])

                    send_message(user_id, answer, default_keyboard)

                    user_domain = f'vk.com/{user_info["domain"]}'

                    admin_msg = f'{user_info["first_name"]} {user_info["last_name"]}({user_domain}) создал(а) встречу на {user.date} в {user.time}'
                    send_message(config['admin_id'], admin_msg)

                elif user.state == 'null':
                    if text == replicates['change_date_and_time']:
                        user.state = 'select_date'
                        user.save()

                        send_message(user_id, f'{replicates["first_message"]}\n{replicates["select_date"]}', get_keyboard_date())

                    else:
                        send_message(user_id, replicates['error_command'], default_keyboard)