from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from common.constants import *
from user.send_id.common import (
    get_id_info,
    extract_important_info,
    check_local_storage,
    check_remote_storage,
)
from common.common import edit_message
from common.stringifies import *
import models
from start import start_command

ID = 0


async def add_ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await update.callback_query.answer(
            text=(
                "أرسل الآيدي.\n"
                "في حال إرسالك إحالة مسجلة لديك مسبقاً، أو مستخدمة من قبل شخص آخر فسيقوم البوت بتجاهل الآيدي وحسب."
            ),
            show_alert=True,
        )
        return ID


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        wait_msg = await context.bot.send_message(
            chat_id=update.effective_user.id, text="الرجاء الانتظار..."
        )
        trader_id = update.message.text

        ref = models.Referral.get(referral_trader_id=trader_id)
        if ref:
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

        await models.Referral.add(
            user_id=update.effective_user.id, referral_trader_id=trader_id
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

        await update.message.reply_text(
            text=("تم ✅\n" "الرجاء الضغط على تحديث ♻️"),
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="تحديث ♻️",
                    callback_data="refresh to delete",
                )
            ),
        )

        await wait_msg.delete()
        await update.message.delete()

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
    fallbacks=[start_command],
)
