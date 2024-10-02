from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from custom_filters import Admin
from common.constants import *
from common.common import calc_available_balance, edit_message
from common.stringifies import *
import models
import os
from start import start_command

WALLET_ADDRESS, AMOUNT, CONFIRM_WITHDRAW = range(3)


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        balances = calc_available_balance(user_id=update.effective_user.id)
        withdraw_msg = await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "أرسل المبلغ.\n"
                f"الرصيد المتاح: <code>{balances['available_balance']:.2f}</code>$"
            ),
        )
        context.user_data["withdraw_msg_id"] = withdraw_msg.id
        return AMOUNT


async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:

        text = "أرسل عنوان محفظة USDT\n\n" "<b>ملاحظة: الشبكة المستخدمة TRC20</b>"
        balances = calc_available_balance(user_id=update.effective_user.id)
        amount = float(update.message.text)

        if balances["available_balance"] - amount < 0:
            await update.message.reply_text(
                text=f"ليس لديك رصيد كافٍ، الرصيد المتاح: <code>{balances['available_balance']:.2f}</code>$",
            )
            return
        elif amount == 0:
            await update.message.reply_text(
                text=f"الرجاء إرسال قيمة موجبة تماماً أكبر من الصفر، الرصيد المتاح: <code>{balances['available_balance']:.2f}</code>$",
            )
            return

        context.user_data["withdraw_amount"] = amount

        get_amount_msg = await update.message.reply_text(
            text=text,
        )
        context.user_data["get_amount_msg_id"] = get_amount_msg.id

        await context.bot.delete_message(
            chat_id=update.effective_user.id,
            message_id=context.user_data["withdraw_msg_id"],
        )
        await update.message.delete()

        return WALLET_ADDRESS


async def get_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="تأكيد ✅",
                    callback_data="approve_withdraw",
                ),
                InlineKeyboardButton(
                    text="إلغاء ❌",
                    callback_data="cancel_withdraw",
                ),
            ],
        ]
        context.user_data["withdraw_wallet_address"] = update.message.text
        get_wallet_address_msg = await update.message.reply_text(
            text=stringify_withdraw_order(
                amount=context.user_data["withdraw_amount"],
                address=context.user_data["withdraw_wallet_address"],
            )
            + "هل أنت متأكد؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        context.user_data["get_wallet_address_msg_id"] = get_wallet_address_msg.id

        await context.bot.delete_message(
            chat_id=update.effective_user.id,
            message_id=context.user_data["get_amount_msg_id"],
        )
        await update.message.delete()

        return CONFIRM_WITHDRAW


async def confirm_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if update.callback_query.data.startswith("approve"):

            await models.Account.withdraw(
                user_id=update.effective_user.id,
                amount=context.user_data["withdraw_amount"],
            )

            await context.bot.send_message(
                chat_id=int(os.getenv("WITHDRAWALS_CHANNEL")),
                text=stringify_withdraw_order(
                    amount=context.user_data["withdraw_amount"],
                    address=context.user_data["withdraw_wallet_address"],
                ),
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="التعليم كطلب منجز ✔️", callback_data="mark as done"
                    )
                ),
            )

            await update.callback_query.answer(
                text="شكراً لك، تم إرسال طلبك للمراجعة",
                show_alert=True,
            )

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

            await update.message.reply_text(
                text=("تم ✅\n" "الرجاء الضغط على تحديث ♻️"),
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        text="تحديث ♻️",
                        callback_data="refresh to delete",
                    )
                ),
            )

        else:
            await update.callback_query.answer(
                text="تم الإلغاء ❌",
                show_alert=True,
            )
        await update.callback_query.delete_message()
        return ConversationHandler.END


async def mark_as_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.CHANNEL and Admin().filter(update):
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="منجز ✅",
                    callback_data="✅✅✅✅✅✅✅✅✅",
                )
            )
        )


withdraw_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            withdraw,
            "^withdraw$",
        )
    ],
    states={
        AMOUNT: [
            MessageHandler(
                filters=filters.Regex(
                    "^\d+\.?\d*$",
                ),
                callback=get_amount,
            )
        ],
        WALLET_ADDRESS: [
            MessageHandler(
                filters=filters.Regex(r"^T[A-Za-z1-9]{33}$"),
                callback=get_wallet_address,
            )
        ],
        CONFIRM_WITHDRAW: [
            CallbackQueryHandler(
                confirm_withdraw,
                "^((approve)|(cancel))_withdraw$",
            )
        ],
    },
    fallbacks=[start_command],
)


mark_as_done_handler = CallbackQueryHandler(mark_as_done, "^mark as done$")
