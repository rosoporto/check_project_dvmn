import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv


logger = logging.getLogger(__file__)


class TgLogsHandler(logging.Handler):

    def __init__(self, token, chat_id):
        super().__init__()
        self.bot = telegram.Bot(token=token)
        self.admin_chat_id = chat_id

    def emit(self, record):
        self.bot.send_message(
                         chat_id=self.admin_chat_id,
                         text=self.format(record)
		)


def main():
    load_dotenv()
    
    tg_token_bot = os.environ.get('TG_TOKEN_BOT')
    tg_chat_id = os.environ.get('TG_CHAT_ID')
    
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(message)s',
        level=logging.INFO
    )    
    tg_handler = TgLogsHandler(tg_token_bot, tg_chat_id)
    logger.addHandler(tg_handler)
  
    logger.info('Bot started')
    
    try:
        1/0
    except ZeroDivisionError:
        logger.exception('Deliberate divide by zero traceback')
        

if __name__ == '__main__':
    main()
