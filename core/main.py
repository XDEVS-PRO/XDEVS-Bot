import logging
from datetime import datetime

from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ConversationHandler, MessageHandler, Filters, CallbackContext, Updater, CallbackQueryHandler, \
    Dispatcher, CommandHandler

import settings
from core import db
from core.decorators import redirect_to_user_chat

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NL = '\n'
main_reply_keyboard = [['My info', 'XDEVS'],
                       ['Next review Goals'],
                       ['Onboarding', 'Birthdate'],
                       ]
markup = ReplyKeyboardMarkup(main_reply_keyboard, one_time_keyboard=True)

# State definitions for top level conversation
CHOOSING, SET_BIRTHDATE, ASK_FOR_BIRTHDATE = map(chr, range(3))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

ok_button = [
    [
        InlineKeyboardButton(text='OK', callback_data=str(END)),
    ],
]

bot = Bot(settings.TELEGRAM_TOKEN)


@redirect_to_user_chat(markup)
def user_info(update: Update, context: CallbackContext) -> str:
    telegram_id = update.effective_user.id
    user = context.dispatcher.user_data[telegram_id]
    text = f'Position: {user.get("position")}'
    update.message.reply_text(text=text, reply_markup=markup)
    return CHOOSING


@redirect_to_user_chat(markup)
def xdevs_info(update: Update, context: CallbackContext) -> str:
    main_info = 'https://docs.google.com/document/d/1XZaodC7klZeHtrahIkDKf1XijotP' \
                '4zCU/edit?usp=sharing&ouid=101431570397641864644&rtpof=true&sd=true'
    goals = 'https://docs.google.com/document/d/13To7-AgL73lIBXxOAxcv9Ou5qvPRUz5EFvuJotjB7Dk/edit?usp=sharing'
    ps = 'Make sure you are using XDEVS account.'
    text = f'XDEVS: {NL}' \
           f'{main_info} {NL}{NL}' \
           f'Goals {datetime.now().year}: {NL}' \
           f'{goals} {NL}' \
           f'{ps}'
    keyboard = InlineKeyboardMarkup(ok_button)
    update.message.reply_text(text=text, reply_markup=keyboard)
    return CHOOSING


@redirect_to_user_chat(markup)
def user_review_goals(update: Update, context: CallbackContext) -> str:
    telegram_id = update.effective_user.id
    user: dict = context.dispatcher.user_data[telegram_id]
    next_review: dict = user.get('next_review')
    if next_review:
        date = next_review.get("date").strftime('%d.%m.%Y')
        text = f'Next review is: {date} {NL}' \
               f'Your goals: {NL}' \
               f'{next_review.get("url")}'
    else:
        text = 'Your goals are unclear 🔮. Please come back later'
    update.message.reply_text(text=text, reply_markup=markup)
    return CHOOSING


@redirect_to_user_chat(markup)
def user_onboarding(update: Update, context: CallbackContext) -> str:
    conventions_link = 'https://docs.google.com/document/d/1YlfK160CwhKUcYRlxZiYYZ-RBSz9FN7N/edit?usp=sharing&ouid=101431570397641864644&rtpof=true&sd=true'
    tasks_flow_link = 'https://docs.google.com/document/d/1V2Uv-_CsdjkRBGqgkvu5yGaGKfU9TcPV1lNXqfLQ9hA/edit?usp=sharing'
    bonuses_link = 'https://docs.google.com/document/d/1fYmN_Yxh8_g1B0_p6ar3aq4kBUR1OXd2-X7ssJ3lMI0/edit?usp=sharing'
    ps = 'Make sure you are using XDEVS account.'
    text = f'Conventions: {NL}' \
           f'{conventions_link} {NL}{NL}' \
           f'Tasks flow: {NL}' \
           f'{tasks_flow_link} {NL}{NL}' \
           f'Bonuses: {NL}' \
           f'{bonuses_link} {NL}' \
           f'{ps}'
    keyboard = InlineKeyboardMarkup(ok_button)
    update.message.reply_text(text=text, reply_markup=keyboard)
    return CHOOSING


@redirect_to_user_chat(markup)
def user_birthdate(update: Update, context: CallbackContext):
    text = 'You can set your birthdate in `mm.dd.yyyy` format:'
    action_button_txt = 'Set date'
    telegram_id = update.effective_user.id
    user: dict = context.dispatcher.user_data[telegram_id]
    user_bday: datetime = user.get('birthdate')
    if user_bday:
        text = f'Your birthdate is on {user_bday.strftime("%d.%m.%Y")}'
        action_button_txt = 'Edit date'
    buttons = [
        [
            InlineKeyboardButton(text=action_button_txt, callback_data=str(ASK_FOR_BIRTHDATE)),
            InlineKeyboardButton(text='Back', callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=text, reply_markup=keyboard)
    return SET_BIRTHDATE


@redirect_to_user_chat(markup)
def ask_for_birthdate(update: Update, context: CallbackContext) -> str:
    """Prompt user to input data for selected feature."""
    text = 'Okay, tell me. Example: 21.10.1995'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING


@redirect_to_user_chat(markup)
def save_birthdate(update: Update, context: CallbackContext) -> str:
    """Save input for feature and return to feature selection."""
    if update.message:
        message = update.message
    else:
        message = update.edited_message
    b_date = message.text

    try:
        b_date = datetime.strptime(b_date, "%d.%m.%Y")
    except ValueError:
        message.reply_text(text='Wrong date format ❌. Please try again')
        return TYPING
    db.patch_user(update.effective_user.username, {'birthdate': b_date})
    telegram_id = update.effective_user.id
    context.dispatcher.user_data[telegram_id]['birthdate'] = b_date
    message.reply_text(text='Done ✅', reply_markup=markup)

    return END


@redirect_to_user_chat(markup)
def other_msgs_handler(update: Update, context: CallbackContext) -> str:
    """Handle messages that don't have regex handler."""
    telegram_id = update.effective_user.id
    chat_id = telegram_id
    bot.send_message(chat_id=chat_id, text='404', reply_markup=markup)

    return CHOOSING


def start(update: Update, context: CallbackContext) -> str:
    username = update.effective_user.username
    reply_text = "Ready to start >>>"
    user_doc = db.get_user(username)
    user = user_doc.to_dict()
    if not user_doc.exists:
        reply_text = "Access denied. Please contact the administrator."
        update.message.reply_text(reply_text)
        return END
    if not user.get('telegram_id'):
        data = {
            'telegram_id': update.effective_user.id,
        }
        db.update_user(username, data)
        user = {**user, **data}

    telegram_id = user.get('telegram_id')
    if update.message.chat.id != telegram_id:
        update.message.delete()
        context.bot.send_message(chat_id=telegram_id, text='Let\'s continue here. Click on any button to start.',
                                 reply_markup=markup)
    else:
        update.message.reply_text(reply_text, reply_markup=markup)
    return CHOOSING


def end(update: Update, context: CallbackContext) -> str:
    reply_text = ">>>"
    update.callback_query.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING


def get_conv_handler() -> ConversationHandler:
    default_regex_commands = 'My info|XDEVS|Next review Goals|Onboarding|Birthdate'

    birthdate_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(ask_for_birthdate, pattern=f'^{ASK_FOR_BIRTHDATE}$'),
            MessageHandler(Filters.text & ~Filters.command, save_birthdate),
        ],
        states={
            TYPING: [MessageHandler(Filters.text & ~Filters.command, save_birthdate)],
        },
        fallbacks=[
            CallbackQueryHandler(end, pattern=f'^{END}$'),
        ],
        map_to_parent={
            # Return to second level menu
            END: CHOOSING,
        },
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.regex(f'^{default_regex_commands}$'), start)
        ],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^My info$'), user_info),
                       MessageHandler(Filters.regex('^XDEVS$'), xdevs_info),
                       MessageHandler(Filters.regex('^Next review Goals$'), user_review_goals),
                       MessageHandler(Filters.regex('^Onboarding$'), user_onboarding),
                       MessageHandler(Filters.regex('^Birthdate$'), user_birthdate),
                       # MessageHandler(Filters.regex(f'^(?!.*({default_regex_commands}))'),
                       #                other_msgs_handler),
                       ],
            SET_BIRTHDATE: [birthdate_handler]
        },

        fallbacks=[CallbackQueryHandler(end, pattern=f'^{END}$')],
        name='XDEVS_bot',
        persistent=True
    )
    return conv_handler


def main():
    """
    Use this function for local development.
    Returns:

    """

    updater = Updater(settings.TELEGRAM_TOKEN, use_context=True, persistence=settings.firebase_persistence)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    globals()['context.dispatcher'] = dp

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY

    dp.add_handler(get_conv_handler())

    updater.start_polling()
    updater.idle()


def webhook(request):
    """Webhook for the telegram bot. This Cloud Function only executes within a certain
    time period after the triggering event.
    Args:
        request: A flask.Request object. <https://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        Response text.
    """
    dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True, persistence=settings.firebase_persistence)
    dispatcher.add_handler(get_conv_handler())
    globals()['context.dispatcher'] = dispatcher

    logger.info("In webhook handler")

    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)

        dispatcher.process_update(update)

        return "ok"
    else:
        # Only POST accepted
        logger.warning("Only POST method accepted")
        return "error"


if __name__ == '__main__':
    if settings.DEBUG:
        main()
