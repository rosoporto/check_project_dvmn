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
    
    devman_token = os.environ.get('DEVMAN_TOKEN')
    tg_token_bot = os.environ.get('TG_TOKEN_BOT')
    tg_chat_id = os.environ.get('TG_CHAT_ID')    
    url = 'https://dvmn.org/api/long_polling/'
    
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(message)s',
        level=logging.INFO
    )    
    tg_handler = TgLogsHandler(tg_token_bot, tg_chat_id)
    logger.addHandler(tg_handler)

    headers = {'Authorization': f'Token {devman_token}'}
    last_time = ''
    
    logger.info('Bot started')
    while True:
        try:
            params = {'timestamp': last_time}
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            review = response.json()
            if review['status'] == 'found':
                answer = review['new_attempts'][0]
                if answer['is_negative']:
                    status = 'В работе есть ошибки'
                else:
                    status = 'Работа проверена. Ошибок нет'
                lesson_title = answer['lesson_title']
                lesson_url = answer['lesson_url']             
            
                last_time = review.get('last_attempt_timestamp', last_time)
                
                tg_handler.bot.send_message(chat_id=tg_chat_id,
                                text=(f'У вас проверили работу "{lesson_title}"\n\n'
                                    f'{status}\n{lesson_url}'))
            else:
                last_time = review.get('timestamp_to_request', last_time)
                    
        except requests.exceptions.ReadTimeout:
            logger.error('Time Out')
            continue
        except requests.exceptions.ConnectionError:
            logger.error('Lost connection')
            time.sleep(600)


if __name__ == '__main__':
    main()
