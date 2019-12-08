import json
import dflow.entity_maker as de
from app import settings
from bot import CurrencyInfoBot
from dflow import get_sessions_client


def main():
    dialogflow_config = {
        'project_id': settings.DIALOGFLOW_PROJECT_ID,
        'lang_code': settings.DIALOGFLOW_LANGUAGE_CODE,
        'client': get_sessions_client()
    }
    bot = CurrencyInfoBot(
        token=settings.TELEGRAM_BOT_TOKEN,
        df_config=dialogflow_config
    )
    bot.start()


if __name__ == '__main__':
    main()
    # de.configure_crypto_currency_entity()
