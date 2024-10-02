from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.common import edit_message
from common.stringifies import *
from common.constants import *
from user.send_id.common import (
    get_id_info,
    extract_important_info,
    check_remote_storage,
    check_local_storage,
)
import start
import models


ID = 0


async def manage_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        data = update.callback_query.data
        if data.startswith("add"):
            await update.callback_query.delete_message()
        context.user_data["manage_account_action"] = data
        await update.callback_query.answer(
            text=(
                "أرسل الآيدي.\n"
                "في حال إرسالك آيدي حسابك الحالي أو آيدي حساب عائد لشخص آخر فسيقوم البوت بتجاهل الآيدي وحسب."
            ),
            show_alert=True,
        )
        return ID


async def get_my_account_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        wait_msg = await context.bot.send_message(
            chat_id=update.effective_user.id, text="الرجاء الانتظار..."
        )

        trader_id = update.message.text

        account = models.Account.get(trader_id=trader_id)
        if account:
            await wait_msg.delete()
            await update.message.delete()
            return ConversationHandler.END

        text = await get_id_info(trader_id=trader_id)
        if not text:
            await wait_msg.delete()
            await update.message.delete()
            return ConversationHandler.END

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
            await update.message.reply_text(
                text="تمت إضافة الحساب بنجاح ✅، اضغط /start للمتابعة."
            )

        elif action.startswith("update"):
            await models.Account.reattach_to_user(
                user_id=update.effective_user.id,
                trader_id=trader_id,
            )
            await update.message.reply_text(
                text=("تم ✅\n" "الرجاء الضغط على تحديث ♻️"),
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="تحديث ♻️",
                        callback_data="refresh to delete",
                    )
                ),
            )

        await models.Referral.add(
            user_id=update.effective_user.id, referral_trader_id=trader_id
        )

        account = models.Account.get(trader_id=trader_id)

        await edit_message(
            context=context,
            user_id=update.effective_user.id,
            text=stringify_account_info(
                info=models.AccountInfo.get(trader_id=account.trader_id)
            ),
            msg_id=context.user_data["my_account_msg_id"],
            reply_markup=InlineKeyboardMarkup.from_row(
                [
                    InlineKeyboardButton(
                        text="تعديل الحساب",
                        callback_data="update account",
                    ),
                    InlineKeyboardButton(
                        text="تحديث ♻️",
                        callback_data="refresh",
                    ),
                ]
            ),
        )

        await wait_msg.delete()
        await update.message.delete()

        return ConversationHandler.END


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
    fallbacks=[start.start_command],
)
