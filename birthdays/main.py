import logging
from datetime import datetime
from typing import List, Union

from google.cloud.firestore_v1 import DocumentSnapshot
from telegram import Bot

import settings
from settings import firestore_client as client

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(settings.TELEGRAM_TOKEN)


def has_birthdate() -> Union[List[DocumentSnapshot], list]:
    """
    Checks if any user has a birthdate today.
    Returns:
         list

    """
    today = datetime.today()
    users_born_today = []

    for user_doc in client.collection('users').get():
        user_birthday = user_doc.to_dict().get('birthdate')
        if user_birthday and user_birthday.day == today.day and user_birthday.month == today.month:
            users_born_today.append(user_doc)
    return users_born_today


def main():
    """
    Use this function for local development.
    Returns:

    """
    for user in has_birthdate():
        text = f"У @{user.id} сегодня День Рождения 🥳"
        bot.send_message(chat_id=settings.GROUP_CHAT_ID, text=text)


def pubsub(event, context):
    """Webhook for the telegram bot. This Cloud Function only executes within a certain
    time period after the triggering event.
    Args:
        request: A flask.Request object. <https://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        Response text.
    """

    for user in has_birthdate():
        text = f"У @{user.id} сегодня День Рождения 🥳"
        bot.send_message(chat_id=settings.GROUP_CHAT_ID, text=text)


if __name__ == '__main__':
    if settings.DEBUG:
        main()
