import logging
from add_question import *
from player_interface import *
from telegram.ext import Updater
TIME = 30
# Ядро.
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
TOKEN = "829719381:AAH7KMl8OeBvMq5ZLOWebK99lHAi4PrS-O4"

updater = Updater(TOKEN)
dp = updater.dispatcher
j = updater.job_queue
add_admin_commands(dp)
add_player_commands(dp)
updater.start_polling()
updater.idle()
