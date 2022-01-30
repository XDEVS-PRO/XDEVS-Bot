from functools import wraps

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from core import db


def redirect_to_user_chat(markup: ReplyKeyboardMarkup):
    """
    Clean the bot commands from the group chat and send the message to a user.

    Args:
        markup: ReplyKeyboardMarkup

    Returns:
        None
        or
        Calls decorated function if in the user's chat.
    """

    def decorator(func):
        @wraps(func)
        def send_message_to_user(update: Update, context: CallbackContext, *args, **kwargs):
            user_telegram_id = update.effective_user.id
            if context.dispatcher.user_data.get(user_telegram_id, None) == {}:
                context.dispatcher.user_data[user_telegram_id] = db.get_user(update.effective_user.username).to_dict()
            if update.effective_chat.id != user_telegram_id:
                update.message.delete()
                context.bot.send_message(chat_id=user_telegram_id,
                                         text='Let\'s continue here. Press any button to begin.',
                                         reply_markup=markup)
            else:
                return func(update, context, *args, **kwargs)

        return send_message_to_user
    return decorator
