from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime

import csv, logging, configparser, re

print("BOT STARTED")
config = configparser.ConfigParser()
config.read('config_bot.ini')
token = config['telegram.bot']['token']

plate_arr = []
admin_arr = []

FORMAT = '%(asctime)-15s  %(levelname)-8s %(message)s'
logging.basicConfig(filename='sovhoz_bot.log', format=FORMAT, level=logging.INFO)
logging.info('BOT STARTED...')

with open("spisok.csv", newline='') as csv_file:
    plate_csv = csv.DictReader(csv_file)
    for i in plate_csv:
        plate_arr.append(i['PLATE'].lower())
print('List was created From file.csv')
logging.info('List was created From file.csv')

with open("admin_list.csv", newline='') as csv_file:
    admin_csv = csv.DictReader(csv_file)
    for i in admin_csv:
        admin_arr.append(i['ADMIN'].lower())
print('Admin list was created From admin_list.csv')
logging.info('Admin list was read')

class Bot:
    def __init__(self, token):
        self.token = token
        self.updater = Updater(token, use_context=True)

    def join(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler('start', self.start))
        dp.add_handler(MessageHandler(Filters.text, self.message_handler))
        self.updater.start_polling()
        self.updater.idle()

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=config['DEFAULT']['greetingstr'])

    def message_handler(self, update, context):
        msg_text = update.message.text.lower()
        print('{}; user:= {}; name:= {} {}; text:= {}'.format(datetime.now(), update.message.from_user.username, update.message.from_user.first_name, update.message.from_user.last_name, update.message.text))

        log(update)
        #----private chat block
        if(update.effective_chat.type == 'private'):
            if(msg_text == '/help' or msg_text == '/help@sovhozparking_bot'):
                context.bot.send_message(chat_id=update.effective_chat.id, text=config['DEFAULT']['helpmestr'])
                log_answer(config['DEFAULT']['helpmestr'])
            elif(msg_text.find("/check") != -1):
                if(msg_text.find("/check@sovhozparking_bot") != -1 and len(msg_text) > 30):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=check_plate(prepare_str(msg_text)))
                    log_answer(check_plate(prepare_str(msg_text)))
                elif(msg_text == '/check' or msg_text == '/check@sovhozparking_bot'):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=config['DEFAULT']['emptycheck'])
                    log_answer(config['DEFAULT']['emptycheck'])
                elif(msg_text.find("/check@sovhozparking_bot") == -1 and msg_text.find("/check") != -1 and len(msg_text) >= 12):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=check_plate(prepare_str(msg_text)))
                    log_answer(check_plate(prepare_str(msg_text)))
            elif(msg_text == "/admin" and update.message.from_user.id == int(config['telegram.bot']['owner_id'])):
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=config['telegram.bot']['admin_greeting'])
            elif(msg_text == '/admin_list' and update.message.from_user.id == int(config['telegram.bot']['owner_id'])):
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=get_admin_list())
            elif(msg_text.find("/set_admin") != -1 and update.message.from_user.id == int(config['telegram.bot']['owner_id'])):
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=set_admin(prepare_str(msg_text)))
            elif (msg_text.find("/del_admin") != -1 and update.message.from_user.id == int(config['telegram.bot']['owner_id'])):
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=del_admin(prepare_str(msg_text)))
            elif(msg_text.find("/add_num ") != -1):
                if(str(update.message.from_user.id) in admin_arr):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=add_to_base(prepare_str(msg_text)))
                    logging.info('Успешно добавлен в базу: {}'.format(prepare_str(msg_text)))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=config['telegram.bot']['admin_err'])
                    log_answer(config['telegram.bot']['admin_err'])
            elif(msg_text.find("/delete_num ") != -1):
                if(str(update.message.from_user.id) in admin_arr):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=del_from_base(prepare_str(msg_text)))
                    logging.info('Успешно удален из базы: {}'.format(prepare_str(msg_text)))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=config['telegram.bot']['admin_err'])
                    log_answer(config['telegram.bot']['admin_err'])
            elif(reg_search(cut_chars(msg_text))):
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=check_plate(cut_chars(msg_text)))
                log_answer(check_plate(cut_chars(msg_text)))

        #----group chat block
        else:
            if(msg_text == '/help' or msg_text == '/help@sovhozparking_bot'):
                context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=config['DEFAULT']['helpmestr'])
                log_answer(config['DEFAULT']['helpmestr'])
            elif(msg_text.find("/check") != -1):
                if (msg_text.find("/check@sovhozparking_bot") != -1 and len(msg_text) > 30):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=check_plate(prepare_str(msg_text)))
                    log_answer(check_plate(prepare_str(msg_text)))
                elif (msg_text.find("/check@sovhozparking_bot") == -1 and msg_text.find("/check") != -1 and len(msg_text) >= 12):
                    context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.message.message_id, text=check_plate(prepare_str(msg_text)))
                    log_answer(check_plate(prepare_str(msg_text)))


def check_plate(string):
    if string in plate_arr:
        text_msg = config['DEFAULT']['foundstr']
    else:
        text_msg = config['DEFAULT']['notfoundstr']
    return text_msg

def prepare_str(string):
    string_out = string.replace('@sovhozparking_bot', '')
    string_out = string_out.replace('/check', '')
    string_out = string_out.replace('/set_admin', '')
    string_out = string_out.replace('/del_admin', '')
    string_out = string_out.replace('/add_num', '')
    string_out = string_out.replace('/delete_num', '')
    string_out = cut_chars(string_out)
    return string_out

def cut_chars(str):
    string_out = str.replace(' ', '')
    string_out = string_out.replace('"', '')
    string_out = string_out.replace("'", '')
    string_out = string_out.replace('(', '')
    string_out = string_out.replace(')', '')
    string_out = string_out.replace('_', '')
    string_out = string_out.replace('-', '')
    string_out = string_out.replace('.', '')
    string_out = string_out.replace(',', '')
    return string_out

def log(update):
    logging.info(
        'INPUT MESSAGE FROM chat_id:= {} - chat_type:= {} - chat_title:= {}'.format(update.effective_chat.id, update.effective_chat.type, update.effective_chat.title))
    logging.info(
        'INPUT MSG FROM user_id:= {} - USERNAME:= {} - NAME:= {} {} - TEXT:= {}'.format(update.message.from_user.id, update.message.from_user.username, update.message.from_user.first_name, update.message.from_user.last_name, update.message.text))

def log_answer(str):
    logging.info('BOT ANSWER:= {}'.format(str))

def reg_search(line):
    parser = re.search(r'\w\d{3}\w{2}', line)
    return(True if parser else False)

def get_admin_list():
    string = ''
    for admin in admin_arr:
        string += admin + ' ; '
    if(len(string) == 0):
        return 'Список пуст'
    else: return string

def set_admin(str):
    admin_arr.append(str)
    with open("admin_list.csv", 'w', newline='') as csv_file:
        header = ['ADMIN']
        admin_csv = csv.writer(csv_file, delimiter=',')
        admin_csv.writerow(header)
        for admin in admin_arr:
            admin_csv.writerow([admin,])
    print('Admin list was updated')
    logging.info('Admin list was updated')
    return 'Успешно добавлено'

def del_admin(str):
    try:
        admin_arr.remove(str)
        with open("admin_list.csv", 'w', newline='') as csv_file:
            header = ['ADMIN']
            admin_csv = csv.writer(csv_file, delimiter=',')
            admin_csv.writerow(header)
            for admin in admin_arr:
                admin_csv.writerow([admin,])
        return 'Успешно'
    except ValueError:
        return 'Ошибка: админа нет в списке'

def add_to_base(str):
    if(str not in plate_arr):
        plate_arr.append(str)
        print("List of Plates was updated")
        with open("spisok.csv", "w", newline='') as csv_file:
            header = ['PLATE']
            plate_csv = csv.writer(csv_file, delimiter=',')
            plate_csv.writerow(header)
            for plate in plate_arr:
                plate_csv.writerow([plate,])
        return 'Номер успешно добавлен в базу'
    else:
        return 'Этот номер уже внесен'

def del_from_base(str):
    try:
        plate_arr.remove(str)
        print("List of Plates was updated (DELETE COMMAND)")
        with open("spisok.csv", "w", newline='') as csv_file:
            header = ['PLATE']
            plate_csv = csv.writer(csv_file, delimiter=',')
            plate_csv.writerow(header)
            for plate in plate_arr:
                plate_csv.writerow([plate,])
        return 'Номер успешно удален'
    except ValueError:
        print('Ошибка: номера нет в списке: {}'.format(str))
        return 'Ошибка: номера нет в списке'

bot = Bot(token)
bot.join()