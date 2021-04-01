import telebot
import random
import time
import sqlite3
import psycopg2
import dj_database_url
from mwt import MWT

access_token = "432656055:AAH3_jLNQFpqNr8dZFXSYoAcZLEVF5jFvuM"
bot = telebot.TeleBot(access_token)
DATABASELINK = "postgres://adtvurxwqmfpfp:517b76d5ca5886c72947580769d88878444beb7ca54a99b52806ba3f5a457ae3@ec2-79-125-118-221.eu-west-1.compute.amazonaws.com:5432/df02ed0lrqf3n3"
db_info = dj_database_url.config(default=DATABASELINK)


@MWT(timeout=60 * 60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


@bot.message_handler(commands=['start'])
def start_message(message):
    resp = 'Йоу, собаки! Крч, я появился от нефиг делать, буду там постепенно расширяться.\nФункционал можете посмотреть по команде <b>help</b>\nБудут идеи, что добавить - милости прошу в ЛС к создателю\n@WhiskeyMotel'
    bot.send_message(message.chat.id, resp, parse_mode='HTML')
    chat_id = str(message.chat.id)[1:]
    conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'), password=db_info.get('PASSWORD'),
                            host=db_info.get('HOST'), port=db_info.get('PORT'))
    c = conn.cursor()
    kom = "CREATE TABLE IF NOT EXISTS ch_{} (id SERIAL PRIMARY KEY, user_id BIGINT, nickname VARCHAR NOT NULL, pidor_counter INTEGER, flag_time BIGINT)".format(
        chat_id)
    c.execute(kom)
    conn.commit()
    c.close()
    conn.close()


@bot.message_handler(commands=['register'])
def reg_user(message):
    chat_id = str(message.chat.id)[1:]
    conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'), password=db_info.get('PASSWORD'),
                            host=db_info.get('HOST'), port=db_info.get('PORT'))
    c = conn.cursor()
    try:
        kom = "SELECT user_id FROM ch_{}".format(chat_id)
        c.execute(kom)
        count = int(0)
        data = c.fetchall()
        print(data)
        for i in range(len(data)):
            print(data[i])
            data[i] = str(data[i])[1:-2]
            data[i] = int(data[i])
            print(data[i])
            print(message.from_user.id)
            if data[i] == message.from_user.id:
                count = 1
        if count >= 1:
            resp = 'Ты уже зарегистрирован!'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
            c.close()
            conn.close()
        else:
            usern = '{} {}'.format(message.from_user.first_name, message.from_user.last_name)
            print(usern)
            if usern[-4:] == 'None':
                usern = usern[:-5]
            print(usern)
            if usern == 'None':
                usern = '{}'.format(message.from_user.username)
            kom = "INSERT INTO ch_{} (user_id, nickname, pidor_counter, flag_time) VALUES ('{}','{}',0, 0)".format(
                chat_id, message.from_user.id, usern)
            c.execute(kom)
            conn.commit()
            resp = 'Окей, ты зареган. Команды <b>who</b> и <b>pidor</b> теперь учитывают тебя'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
            c.close()
            conn.close()
    except sqlite3.ProgrammingError:
        resp = 'База данных недоступна. Повторите запрос позднее'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
        c.close()
        conn.close()


@bot.message_handler(commands=['help'])
def help_message(message):
    resp = '<b>help</b> - помощь по командам\n<b>choose</b> или <b>вариант 1</b> или <b>вариант 2</b>... - выбирает один из заданных вариантов ответа. Все варианты отделять словом "или"\n'
    resp += '<b>who</b> <b>формулировка</b> - выбирает зарегестрированного пользователя из конфы по заданной формулировке\n<b>pidor</b> - ну, вы и так знаете, только можно вызвать всегда и нет статистики (потом прикручу)'
    resp += '\n<b>roll</b> - по просьбе Суицидника. По умолчанию генерирует рандомное число от 1 до 100, но можно задать свой предел через пробел'
    resp += '\n<b>start</b> - начало работы бота. Без нее не работают функции рандома.'
    resp += '\n<b>register</b> - регистрация в БД бота для данной беседы. Пока не зарегистрируетесь, рандом вас выбирать не будет.'
    resp += '\n<b>загугли</b> - запрос в Гугле'
    resp += '\n<b>flip</b> - подбросить монетку!'
    resp += '\n<b>pidorstat</b> - статистика пидоров за все время работы бота'
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['choose'])
def choose(message):
    resp = ''
    buf = message.text.split(' или ')
    if len(buf) < 3:
        resp += 'Ээээ, брат, падажжи. Ты варики указать забыл (минимум 2)'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
    else:
        form = rand_form_choose(random.randint(1, 4))
        resp += '{}<b>{}</b>'.format(form, buf[random.randint(1, len(buf) - 1)])
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['who'])
def who(message):
    try:
        _, question = message.text.split(maxsplit=1)
        chat_id = str(message.chat.id)[1:]
        conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'),
                                password=db_info.get('PASSWORD'), host=db_info.get('HOST'), port=db_info.get('PORT'))
        c = conn.cursor()
        try:
            kom = "SELECT nickname FROM ch_{}".format(chat_id)
            c.execute(kom)
            max = c.fetchall()
            if len(max) < 2:
                resp = 'Не, так не пойдет. Минимум 2 человека надо чтоб зарегистрировалось, иначе неинтересно'
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
                c.close()
                conn.close()
            else:
                i = random.randint(0, len(max) - 1)
                print(i)
                name = str(max[i])[2:-3]
                resp = '<b>{}</b>'.format(name)
                resp += ' {}'.format(question)
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
                c.close()
                conn.close()
        except psycopg2.ProgrammingError:
            resp = 'База данных недоступна. Повторите запрос позднее'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
            conn.close()
    except ValueError:
        resp = 'Эээ, брат, падажжи, а где сам вопрос?'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['pidor'])
def pidor(message):
    flag = 0
    chat_id = str(message.chat.id)[1:]
    conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'),
                            password=db_info.get('PASSWORD'), host=db_info.get('HOST'), port=db_info.get('PORT'))
    c = conn.cursor()
    try:
        kom = "SELECT user_id, nickname, flag_time FROM ch_{}".format(chat_id)
        c.execute(kom)
        max = c.fetchall()
        for human in max:
            if time.time() - human[2] > 86400:
                req = "UPDATE ch_{} SET flag_time = 0 WHERE user_id = '{}'".format(chat_id, human[0])
                c.execute(req)
                conn.commit
                break
        if len(max) < 2:
            resp = 'Не, так не пойдет. Минимум 2 человека надо чтоб зарегистрировалось, иначе неинтересно'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
            c.close()
            conn.close()
        else:
            for human in max:
                if time.time() - human[2] < 86400:
                    resp = 'Пидором сегодняшнего дня объялен <b>{}</b>!'.format(human[1])
                    bot.send_message(message.chat.id, resp, parse_mode='HTML')
                    flag = 1
                    break
            if flag == 0:
                i = random.randint(0, len(max) - 1)
                pidorname = str(max[i][1])
                req = "UPDATE ch_{} SET pidor_counter = pidor_counter+1 WHERE user_id = '{}'".format(chat_id, max[i][0])
                c.execute(req)
                conn.commit()
                time_now = int(time.time())
                req = "UPDATE ch_{} SET flag_time = {} WHERE user_id = '{}'".format(chat_id, time_now, max[i][0])
                c.execute(req)
                conn.commit()
                resp = 'ВНИМАНИЕ!'
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
                time.sleep(1)
                resp = 'ИЩЕМ ТЕКУЩЕГО ПИДОРА...'
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
                time.sleep(1)
                resp = '<b>{}</b>'.format(pidorname)
                resp += ', ты текущий пидарас :)'
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
                c.close()
                conn.close()

    except psycopg2.ProgrammingError:
        resp = 'База данных недоступна. Повторите запрос позднее'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
        c.close()
        conn.close()


@bot.message_handler(commands=['roll'])
def rand_number_mes(message):
    try:
        _, start, end = message.text.split()
        start = int(start)
        end = int(end)
        resp = 'Из мешка вытаскивается шар с номером <b>{}</b>'.format(random.randint(start, end))
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
    except ValueError:
        resp = 'Из мешка вытаскивается шар с номером <b>{}</b>'.format(random.randint(1, 100))
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['flip'])
def flip_mes(message):
    resp = 'Подбрасываем монетку вверх...'
    bot.send_message(message.chat.id, resp, parse_mode='HTML')
    time.sleep(1)
    side = int(random.randint(1, 2))
    if side == 1:
        resp = 'Выпадает <b>орёл!</b>'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
    elif side == 2:
        resp = 'Выпадает <b>решка!</b>'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['google'])
def google_mes(message):
    try:
        _, link = message.text.split(maxsplit=1)
        resp = 'https://www.google.com/search?q='
        resp += '{}'.format(link.replace(' ', '+'))
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
    except ValueError:
        resp = 'Падажжи, шо гуглить?'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['pidorstat'])
def pidorstat(message):
    chat_id = str(message.chat.id)[1:]
    conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'),
                            password=db_info.get('PASSWORD'), host=db_info.get('HOST'), port=db_info.get('PORT'))
    c = conn.cursor()
    try:
        kom = "SELECT nickname, pidor_counter FROM ch_{}".format(chat_id)
        c.execute(kom)
        max = c.fetchall()
        print(max)
        max.sort(key=lambda tup: tup[1], reverse=True)
        print(max)
        resp = '<b>Статистика пидоров за всё время:</b>\n'
        for human in max:
            resp += '\n⌬{} - {}'.format(human[0], human[1])
        bot.send_message(message.chat.id, resp, parse_mode='HTML')

    except psycopg2.ProgrammingError:
        resp = 'База данных недоступна. Повторите запрос позднее'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
        c.close()
        conn.close()
    pass


@bot.message_handler(commands=['resetbase'])
def resetbase(message):
    if message.from_user.id in get_admin_ids(bot, message.chat.id):
        chat_id = str(message.chat.id)[1:]
        conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'),
                                password=db_info.get('PASSWORD'), host=db_info.get('HOST'), port=db_info.get('PORT'))
        c = conn.cursor()
        try:
            kom = "TRUNCATE ch_{}".format(chat_id)
            c.execute(kom)
            conn.commit()
            resp = 'Внимание! База данных была полностью очищена\nТребуется провести повторную регистрацию'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
            c.close()
            conn.close()
        except psycopg2.ProgrammingError:
            resp = 'База данных недоступна. Повторите запрос позднее'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
            c.close()
            conn.close()
    else:
        resp = 'Данная команда доступна только администраторам'
        bot.reply_to(message, resp, parse_mode='HTML')


@bot.message_handler(commands=['updatebase'])
def updatebase(message):
    chat_id = str(message.chat.id)[1:]
    conn = psycopg2.connect(database=db_info.get('NAME'), user=db_info.get('USER'),
                            password=db_info.get('PASSWORD'), host=db_info.get('HOST'), port=db_info.get('PORT'))
    c = conn.cursor()
    try:
        kom = "SELECT user_id, nickname FROM ch_{}".format(chat_id)
        c.execute(kom)
        max = c.fetchall()
        print(1)
        for human in max:
            try:
                bof = bot.get_chat_member(message.chat.id, human[0])
                print(bof)
                usern = '{} {}'.format(bof.user.first_name, bof.user.last_name)
                if usern[-4:] == 'None':
                    usern = usern[:-5]
                if usern == 'None':
                    usern = '{}'.format(bof.user.username)
                req = "UPDATE ch_{} SET nickname = '{}' WHERE user_id = '{}'".format(chat_id, usern, human[0])
                c.execute(req)
                conn.commit()
                print(1)
            except telebot.apihelper.ApiException:
                pass
        resp = 'Внимание! База данных была актуализирована администратором'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
        c.close()
        conn.close()
    except psycopg2.ProgrammingError:
        resp = 'База данных недоступна. Повторите запрос позднее'
        bot.send_message(message.chat.id, resp, parse_mode='HTML')
        c.close()
        conn.close()


def rand_form_choose(kek):
    if kek == 1:
        return 'Я помолился Аллаху и спросил, могу ли я за свои вечные страдания\nполучить от него выбор всей жизни.\nАллах велик, и он помог мне, выбрав '
    elif kek == 2:
        return 'Есть тут у меня знакомый один, рука у него счастливая. Я попросил его выбрать\nИз предложенного, ему больше понравился вариант '
    elif kek == 3:
        return 'Чтобы выбрать из предложенного, я дождался подходящей фазы Луны, отсосал у <b>dorel</b>-a, отдал все деньги РПЦ, и только после этого солнце на рассвете указало мне, что лучшим вариантом будет '
    elif kek == 4:
        return 'Недолго думая, без помощи кого-либо, я выбрал '


if __name__ == '__main__':
    bot.polling(none_stop=True)
