import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = os.environ.get('TOKEN', '')

sender_email = os.environ.get('SENDER_EMAIL', '')
password = os.environ.get('EMAIL_PASSWORD', '')

PORT = int(os.environ.get('PORT', 5000))

CHOOSE_SERVICE, ADDRESS, PHONE, COMPANY = range(4)


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Order Services']]
    update.message.reply_text(
        'Привіт!\nЯ — бот команди Bite The Taste. З моєю допомогою зможеш всього за два кліка зробити замовлення на '
        'дегустацію!',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOOSE_SERVICE


def choose_service(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Замовити Дегустацію':
        update.message.reply_text('Введіть вашу адресу:')
        return ADDRESS
    else:
        update.message.reply_text('Будь-ласка натисніть Замовити Дегустацію.')
        return CHOOSE_SERVICE


def receive_address(update: Update, context: CallbackContext) -> int:
    context.user_data['address'] = update.message.text
    update.message.reply_text('Введіть ваш номер телефону у форматі +380*********:')
    return PHONE


def receive_phone(update: Update, context: CallbackContext) -> int:
    phone_number = update.message.text

    match = re.fullmatch(r'\+380\d{9}', phone_number)

    if match:
        context.user_data['phone'] = phone_number
        update.message.reply_text('Введіть назву компанії:')
        return COMPANY
    else:
        update.message.reply_text('Будь ласка, введіть вірний номер телефону у форматі +380*********')
        return PHONE


def receive_company(update: Update, context: CallbackContext) -> int:
    context.user_data['company'] = update.message.text
    send_email(context.user_data)
    update.message.reply_text('Дякую! Ми вам зателефонуємо.')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Замовлення скасоване. Щоб заново розпочати натисніть /start.')
    return ConversationHandler.END


def send_email(user_data):
    subject = 'Нове замовлення дегустації'
    body = f"Адреса: {user_data['address']}\nНомер телефону: {user_data['phone']}\nКомпанія: {user_data['company']}"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = sender_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(message['From'], password)
        server.sendmail(sender_email, sender_email, message.as_string())


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_SERVICE: [MessageHandler(Filters.text & ~Filters.command, choose_service)],
            ADDRESS: [MessageHandler(Filters.text & ~Filters.command, receive_address)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, receive_phone)],
            COMPANY: [MessageHandler(Filters.text & ~Filters.command, receive_company)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.setWebhook(f'https://bite-the-taste-3e67e88ca643.herokuapp.com/{TOKEN}')

    updater.idle()


if __name__ == '__main__':
    main()
