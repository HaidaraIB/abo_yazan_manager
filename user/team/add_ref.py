from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from common.back_to_home_page import (
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
)
from common.constants import *

from user.send_id.common import (
    get_id_info,
    extract_important_info,
    check_local_storage,
    check_remote_storage,
    stringify_account_info,
)
import models
from start import start_command

ID = 0


async def add_ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        account = models.Account.get(user_id=update.effective_user.id)
        if not account:
            await update.callback_query.answer(
                text="ليس لديك حساب بعد، قم بإضافة حساب بالضغط على زر حسابي 👤",
                show_alert=True,
            )
            return
        await update.callback_query.edit_message_text(
            text="أرسل الآيدي",
            reply_markup=InlineKeyboardMarkup(back_to_user_home_page_button),
        )
        return ID


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        trader_id = update.message.text

        ref = models.Referral.get(referral_trader_id=trader_id)
        if ref:
            if ref.user_id == update.effective_user.id:
                await update.message.reply_text(
                    text="هذا الآيدي في قائمة إحالاتك بالفعل"
                )
            else:
                await update.message.reply_text(
                    text="تم تسجيل هذا الآيدي عن طريق الإحالة من قبل"
                )
            return

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

        await models.Referral.add(
            user_id=update.effective_user.id, referral_trader_id=trader_id
        )

        await update.message.reply_text(text="تمت إضافة الإحالة بنجاح ✅")

        await update.message.reply_text(
            text=(
                "معلومات الإحالة:\n"
                + stringify_account_info(
                    info=models.AccountInfo.get(trader_id=trader_id)
                )
                + "اضغط /start للمتابعة."
            )
        )
        return ConversationHandler.END


add_ref_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_ref,
            "^add ref$",
        )
    ],
    states={
        ID: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=get_id,
            )
        ]
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
    ],
)
