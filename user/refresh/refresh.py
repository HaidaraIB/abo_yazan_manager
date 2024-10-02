from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from common.stringifies import *
import models
from common.common import edit_message
from user.send_id.common import (
    check_local_storage,
    check_remote_storage,
    extract_important_info,
    get_id_info,
)


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        wait_msg = await context.bot.send_message(
            chat_id=update.effective_user.id, text="الرجاء الانتظار..."
        )
        refs = models.Referral.get(user_id=update.effective_user.id)
        for ref in refs:
            text = await get_id_info(trader_id=ref.referral_trader_id)
            if not text:
                continue
            is_closed = "ACCOUNT CLOSED" in text
            data = extract_important_info(text, is_closed=is_closed)

            await check_local_storage(
                is_closed=is_closed, data=data, trader_id=ref.referral_trader_id
            )

            check_remote_storage(
                trader_id=ref.referral_trader_id, is_closed=is_closed, data=data
            )

        account = models.Account.get(user_id=update.effective_user.id)
        await edit_message(
            context=context,
            user_id=update.effective_user.id,
            text=stringify_balance_info(user_id=update.effective_user.id),
            msg_id=context.user_data["balance_info_msg_id"],
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="سحب 📤",
                    callback_data="withdraw",
                )
            ),
        )

        await edit_message(
            context=context,
            user_id=update.effective_user.id,
            text=stringify_team_stats(user_id=update.effective_user.id),
            msg_id=context.user_data["team_stats_msg_id"],
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="إضافة إحالة ➕",
                    callback_data="add ref",
                ),
            ),
        )

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
        await update.callback_query.answer(text="تم التحديث ✅", show_alert=True)

        await wait_msg.delete()
        if "to delete" in update.callback_query.data:
            await update.callback_query.delete_message()


refresh_handler = CallbackQueryHandler(refresh, "^refresh")
