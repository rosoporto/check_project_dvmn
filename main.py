import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv


logger = logging.getLogger(__file__)


def main():
    load_dotenv()
    
    api_devman = os.environ.get('API_DEVMAN')
    api_telegram_bot = os.environ.get('API_TELEGRAM_BOT')
    chat_id = os.environ.get('CHAT_ID')
    bot = telegram.Bot(token=api_telegram_bot)
    url = 'https://dvmn.org/api/long_polling/'
    time_sleep = 300

    headers = {'Authorization': f'Token {api_devman}'}
    last_time = ''

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
                
            last_time = review.get('timestamp_to_request', last_time)
            last_time = review.get('last_attempt_timestamp', last_time)
            
            bot.send_message(chat_id=chat_id,
                             text=(f'У вас проверили работу "{lesson_title}"\n\n'
                                   f'{status}\n{lesson_url}')
                             )
                    
        except requests.exceptions.ReadTimeout:        
            logger.error('Timeout occurred!')
            time.sleep(time_sleep)
            logger.info('Trying to reconnect...')
        except requests.exceptions.ConnectionError:        
            logger.error('Connection Error!')
            time.sleep(time_sleep)
            logger.info('Trying to reconnect...')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
        level=logging.INFO
    )
    main()
