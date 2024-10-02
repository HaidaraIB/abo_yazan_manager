from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from common.back_to_home_page import (
    back_to_user_home_page_button,
    back_to_user_home_page_handler,
)
from custom_filters import Admin
from common.common import build_back_button, build_user_keyboard
from common.constants import *
from user.withdraw.common import stringify_withdraw_order
from user.my_account.account_balance import calc_available_balance

import models
import os

from start import start_command

WALLET_ADDRESS, AMOUNT, CONFIRM_WITHDRAW = range(3)


async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        account = models.Account.get(user_id=update.effective_user.id)
        if not account:
            await update.callback_query.answer(
                text="ليس لديك حساب بعد، قم بإضافة حساب بالضغط على زر حسابي 👤",
                show_alert=True,
            )
            return

        await update.callback_query.edit_message_text(
            text=("أرسل عنوان محفظة USDT\n\n" "<b>ملاحظة: الشبكة المستخدمة TRC20</b>"),
            reply_markup=InlineKeyboardMarkup(back_to_user_home_page_button),
        )
        return WALLET_ADDRESS


async def get_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        back_buttons = [
            build_back_button("back_to_get_wallet_address"),
            back_to_user_home_page_button[0],
        ]
        if update.message:
            context.user_data["withdraw_wallet_address"] = update.message.text
            await update.message.reply_text(
                text="أرسل المبلغ",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل المبلغ",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return AMOUNT


back_to_get_wallet_address = withdraw


async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        back_buttons = [
            build_back_button("back_to_get_amount"),
            back_to_user_home_page_button[0],
        ]
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
            *back_buttons,
        ]
        if update.message:
            balances = calc_available_balance(user_id=update.effective_user.id)
            amount = float(update.message.text)

            if balances["available_balance"] - amount < 0:
                await update.message.reply_text(
                    text=f"ليس لديك رصيد كافٍ، الرصيد المتاح: <b>{balances['available_balance']}$</b>",
                    reply_markup=InlineKeyboardMarkup(back_buttons),
                )
                return

            context.user_data["withdraw_amount"] = amount
            await update.message.reply_text(
                text=stringify_withdraw_order(
                    amount=context.user_data["withdraw_amount"],
                    address=context.user_data["withdraw_wallet_address"],
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text=stringify_withdraw_order(
                    amount=context.user_data["withdraw_amount"],
                    address=context.user_data["withdraw_wallet_address"],
                ),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return CONFIRM_WITHDRAW


back_to_get_amount = get_wallet_address


async def confirm_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        if update.callback_query.data.startswith("approve"):
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
            await update.callback_query.edit_message_text(
                text="شكراً لك، تم إرسال طلبك للمراجعة",
                reply_markup=build_user_keyboard(),
            )
        else:
            await update.callback_query.answer(
                text="تم الإلغاء ❌",
                show_alert=True,
            )
            await update.callback_query.edit_message_text(
                text=HOME_PAGE_TEXT,
                reply_markup=build_user_keyboard(),
            )
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
        WALLET_ADDRESS: [
            MessageHandler(
                filters=filters.Regex(r"^T[A-Za-z1-9]{33}$"),
                callback=get_wallet_address,
            )
        ],
        AMOUNT: [
            MessageHandler(
                filters=filters.Regex(
                    "^\d+\.?\d*$",
                ),
                callback=get_amount,
            )
        ],
        CONFIRM_WITHDRAW: [
            CallbackQueryHandler(
                confirm_withdraw,
                "^((approve)|(cancel))_withdraw$",
            )
        ],
    },
    fallbacks=[
        start_command,
        back_to_user_home_page_handler,
        CallbackQueryHandler(
            back_to_get_wallet_address, "^back_to_get_wallet_address$"
        ),
        CallbackQueryHandler(back_to_get_amount, "^back_to_get_amount$"),
    ],
)


mark_as_done_handler = CallbackQueryHandler(mark_as_done, "^mark as done$")
