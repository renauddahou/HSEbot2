import logging
import json
import requests
from flask import Flask, request
from telegram import Update,Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Dispatcher
from utils import get_reply, fetch_news, topics_keyboard

# enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# telegram bot token
TOKEN = "1636690419:AAGpb52230vXZO-gt7eijcNy2aFcDhYal4w"

app=Flask(__name__)

@app.route('/')
def index():
    return "Hello!"

@app.route(f'/{TOKEN}', methods=['GET', 'POST'])
def webhook():
    update=Update.de_json(request.get_json(),bot)
    dp.process_update(update)
    return "ok"



def start(update: Update, context: CallbackContext):
    """callback function for /start handler"""
    author = update.message.from_user.first_name
    reply = "Hi! {}".format(author)
    update.message.reply_text(reply)


def _help(bot, update):
    """callback function for /help handler"""
    help_txt = "Hey! This is a help text."
    bot.send_message(chat_id=update.message.chat_id, text=help_txt)
    
def news(update: Update, context: CallbackContext):
    text="Choose a category"
    update.message.reply_text(text,
                     reply_markup=ReplyKeyboardMarkup(keyboard=topics_keyboard, one_time_keyboard=True))
    
def summary(update, context):
    response = requests.get('https://api.covid19api.com/summary')
    if(response.status_code==200): #Everything went okay, we have the data
        data = response.json()
        #print(i for i in data['Global'])
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=data['Global'].items())
    else: #something went wrong
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error, something went wrong.")


def reply_text(update: Update, context: CallbackContext):
    """callback function for text message handler"""
    intent, reply = get_reply(update.message.text, update.message.chat_id)
    if intent == "get_news":
        articles = fetch_news(reply)
        for article in articles:
            update.message.reply_text(article['link'])
    else:
        update.message.reply_text(reply)
    


def echo_sticker(update: Update, context: CallbackContext):
    """callback function for sticker message handler"""
    bot.send_sticker(chat_id=update.message.chat_id,
                     sticker=update.message.sticker.file_id)


def error(bot, update):
    """callback function for error handler"""
    logger.error("Update '%s' caused error '%s'", update, update.error)

bot=Bot(TOKEN)
try:
    bot.set_webhook("https://telegram-newsbot.herokuapp.com/"+ TOKEN)
    
except Exception as e:
    print(e)
    
dp = Dispatcher(bot,None)

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", _help))
dp.add_handler(CommandHandler("news", news))
dp.add_handler(CommandHandler("summary", summary))
dp.add_handler(MessageHandler(Filters.text, reply_text))
dp.add_handler(MessageHandler(Filters.sticker, echo_sticker))
dp.add_error_handler(error)


if __name__ == "__main__":
    
    app.run(port=8443)
    
    
    
    
    
    
