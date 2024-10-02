from telegram import Update, Chat
from telegram.ext import ContextTypes, MessageHandler, filters
from custom_filters import User
from send_id.common import (
    extract_important_info,
    get_id_info,
    check_local_storage,
    check_remote_storage,
)
from common.stringifies import stringify_account_info
from common.constants import *

import models


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
        trader_id = update.message.text

        wait_message = await update.message.reply_text("الرجاء الانتظار...")
        text = await get_id_info(trader_id=trader_id)
        if not text:
            await wait_message.edit_text(
                text=ACCOUNT_NOT_FOUND_TEXT,
            )
            return

        is_closed = "ACCOUNT CLOSED" in text
        data = extract_important_info(text, is_closed=is_closed)

        await check_local_storage(is_closed=is_closed, data=data, trader_id=trader_id)

        check_remote_storage(trader_id=trader_id, is_closed=is_closed, data=data)

        await update.message.reply_text(
            text=stringify_account_info(
                info=models.AccountInfo.get(trader_id=trader_id)
            )
        )


send_id_handler = MessageHandler(
    filters=filters.Regex("^\d+$"),
    callback=get_id,
)
