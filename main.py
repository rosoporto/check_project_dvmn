import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv


logger = logging.getLogger(__file__)


def main():
    load_dotenv()
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s',
        level=logging.INFO
    )
    
    devman_token = os.environ.get('DEVMAN_TOKEN')
    tg_token_bot = os.environ.get('TG_TOKEN_BOT')
    tg_chat_id = os.environ.get('TG_CHAT_ID')
    bot = telegram.Bot(token=tg_token_bot)
    url = 'https://dvmn.org/api/long_polling/'

    headers = {'Authorization': f'Token {devman_token}'}
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
            
                last_time = review.get('last_attempt_timestamp', last_time)
                
                bot.send_message(chat_id=tg_chat_id,
                                text=(f'У вас проверили работу "{lesson_title}"\n\n'
                                    f'{status}\n{lesson_url}'))
            else:
                last_time = review.get('timestamp_to_request', last_time)
                    
        except requests.exceptions.ReadTimeout:        
            continue
        except requests.exceptions.ConnectionError:        
            time.sleep(600)


if __name__ == '__main__':
    main()
