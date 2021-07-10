import logging, boto3, requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from os import getenv
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv()
sns = boto3.client('sns',
                region_name='us-east-1', 
                aws_access_key_id=getenv('KEY_ID'),
                aws_secret_access_key='ACCESS_KEY')

value = float(requests.get('https://economia.awesomeapi.com.br/last/USD-BRL').json()['USDBRL']['high'])


def hi(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('/msg [SMS á ser enviado sem colchetes]\n/echo [Text to reply]')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text.split('/echo')[1])

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def msg(update, context):
    name = f'{update.message.from_user.first_name} {update.message.from_user.last_name}'
    sns.publish(TopicArn=getenv('ARN_TOPIC'), 
        Message= f"{name} from Telegram:{update.message.text.split('/msg')[1]}",
        Subject="Mensagem no Telegram")
    
    update.message.reply_text('SMS enviado com sucesso')

def cot(update, context):
    update.message.reply_text(f'O dolar neste momento está à R${value}')

def conv(update, context):
    conv = float(update.message.text.split()[1])*value
    update.message.reply_text(f'${update.message.text.split()[1]} equivalem à R${conv}')


def main():
    """Start the bot."""
    updater = Updater(getenv('TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("hi", hi))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("echo", echo))
    dp.add_handler(CommandHandler("msg", msg))
    dp.add_handler(CommandHandler("cot", cot))
    dp.add_handler(CommandHandler("conv", conv))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()