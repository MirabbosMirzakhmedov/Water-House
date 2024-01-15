from app import bot
import time

while True:
    try:
        print('Bot started')
        bot.infinity_polling(
            timeout=20,
            skip_pending=False,
            long_polling_timeout=20,
            logger_level=40,
            allowed_updates=['message', 'edited_channel_post', 'callback_query'],
            restart_on_change=False,
            path_to_watch=None
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)