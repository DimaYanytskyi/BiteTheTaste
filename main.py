import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = "6563939869:AAEzPgAX0_xAnJxKBg_1GKY1yT3CASPpCrY"

PORT = int(os.environ.get('PORT', 5000))

CHOOSE_SERVICE, ADDRESS, PHONE, COMPANY = range(4)


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Order Services']]
    update.message.reply_text(
        'Hello! Press "Order Services" to order our services.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOOSE_SERVICE


def choose_service(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Order Services':
        update.message.reply_text('Please enter your address:')
        return ADDRESS
    else:
        update.message.reply_text('Please press "Order Services" to proceed.')
        return CHOOSE_SERVICE


def receive_address(update: Update, context: CallbackContext) -> int:
    context.user_data['address'] = update.message.text
    update.message.reply_text('Please enter your phone number:')
    return PHONE


def receive_phone(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    update.message.reply_text('Please enter your company name:')
    return COMPANY


def receive_company(update: Update, context: CallbackContext) -> int:
    context.user_data['company'] = update.message.text
    send_email(context.user_data)
    update.message.reply_text('Thank you! Your order has been placed.')
    return ConversationHandler.END


def send_email(user_data):
    subject = 'New Order Received'
    body = f"Address: {user_data['address']}\nPhone: {user_data['phone']}\nCompany: {user_data['company']}"
    message = f'Subject: {subject}\n\n{body}'


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Order cancelled. To restart the process, press /start.')
    return ConversationHandler.END


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
