from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.back_to_home_page import (
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
)
from common.constants import *
from common.common import build_back_button
from user.send_id.common import (
    stringify_account_info,
    get_id_info,
    extract_important_info,
    check_remote_storage,
    check_local_storage,
)
from user.my_account.common import build_manage_account_keyboard
from start import start_command

import models


async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        account = models.Account.get(user_id=update.effective_user.id)
        if not account:
            text = "ليس لديك حساب بعد، قم بإنشاء حساب بالضغط على الزر أدناه."
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="إضافة حساب",
                        callback_data="add account",
                    ),
                ],
                back_to_user_home_page_button[0],
            ]
        else:
            info = models.AccountInfo.get(trader_id=account.trader_id)
            text = stringify_account_info(info=info)
            keyboard = build_manage_account_keyboard()
            keyboard.append(back_to_user_home_page_button[0])

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


ID = 0


async def manage_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        context.user_data["manage_account_action"] = update.callback_query.data
        back_buttons = [
            build_back_button("back_to_manage_account"),
            back_to_user_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="أرسل الآيدي", reply_markup=InlineKeyboardMarkup(back_buttons)
        )
        return ID


back_to_manage_account = my_account


async def get_my_account_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        back_buttons = [
            build_back_button("back_to_manage_account"),
            back_to_user_home_page_button[0],
        ]
        trader_id = update.message.text
        account = models.Account.get(trader_id=trader_id)
        if account:
            if account.user_id != update.effective_user.id:
                await update.message.reply_text(
                    text="هذا الحساب عائد لمستخدم آخر، تحقق من الآيدي المرسل وأعد المحاولة",
                    reply_markup=InlineKeyboardMarkup(back_buttons),
                )
            else:
                await update.message.reply_text(
                    text="يرجى إرسال آيدي مختلف عن آيدي حسابك الحالي ",
                    reply_markup=InlineKeyboardMarkup(back_buttons),
                )
            return
        wait_message = await update.message.reply_text("الرجاء الانتظار...")
        text = await get_id_info(trader_id=trader_id)
        if not text:
            await wait_message.edit_text(
                text=ACCOUNT_NOT_FOUND_TEXT,
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return

        is_closed = "ACCOUNT CLOSED" in text
        data = extract_important_info(text, is_closed=is_closed)

        await check_local_storage(is_closed=is_closed, data=data, trader_id=trader_id)

        check_remote_storage(trader_id=trader_id, is_closed=is_closed, data=data)

        action: str = context.user_data["manage_account_action"]
        if action.startswith("add"):
            await models.Account.attach_to_user(
                user_id=update.effective_user.id,
                trader_id=trader_id,
            )
            text = "تمت إضافة الحساب بنجاح ✅"
        elif action.startswith("update"):
            await models.Account.reattach_to_user(
                user_id=update.effective_user.id,
                trader_id=trader_id,
            )
            text = "تم تعديل حسابك بنجاح ✅"

        await models.Referral.add(
            user_id=update.effective_user.id, referral_trader_id=trader_id
        )

        await wait_message.edit_text(text=text)

        await update.message.reply_text(
            text=(
                "معلومات حسابك:\n"
                + stringify_account_info(
                    info=models.AccountInfo.get(trader_id=trader_id)
                )
                + "اضغط /start للمتابعة."
            )
        )
        return ConversationHandler.END


my_account_handler = CallbackQueryHandler(my_account, "^my account$")

manage_account_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            manage_account,
            "^((add)|(update)) account$",
        )
    ],
    states={
        ID: [
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=get_my_account_id,
            )
        ]
    },
    fallbacks=[
        back_to_user_home_page_handler,
        start_command,
        CallbackQueryHandler(back_to_manage_account, "^back_to_manage_account$"),
    ],
)
