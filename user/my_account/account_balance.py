from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from user.my_account.common import build_manage_account_keyboard
from common.back_to_home_page import back_to_user_home_page_button
import models


def calc_available_balance(user_id: int):
    my_account = models.Account.get(user_id=user_id)
    my_account_info = models.AccountInfo.get(trader_id=my_account.trader_id)

    refs = models.Referral.get(user_id=user_id)
    refs_info = models.AccountInfo.get(
        trader_ids=list(map(lambda x: x.referral_trader_id, refs))
    )

    team_balance = (
        sum(list(map(lambda x: x.balance, refs_info))) - my_account_info.balance
    )
    level_reward = 0  # TODO how to calc?
    all_time_balance = my_account_info.balance + team_balance + level_reward
    available_balance = all_time_balance - my_account.withdrawals

    return {
        "team_balance": team_balance,
        "level_reward": level_reward,
        "all_time_balance": all_time_balance,
        "available_balance": available_balance,
        "my_account_balance": my_account_info.balance,
        "withdrawals": my_account.withdrawals,
    }


def stringify_balance_info(user_id: int):
    balances = calc_available_balance(user_id=user_id)
    return (
        "<b>الرصيد (الربح)</b>"
        f"من حسابك: {balances['my_account_balance']}$\n"
        f"من الفريق: {balances['team_balance']}$\n"
        f"هدايا المستوى: {balances['level_reward']}$\n"
        "-------------------------------------------------------------\n"
        f"المجموع في كل الوقت: {balances['all_time_balance']}$\n"
        f"السحوبات: {balances['withdrawals']}$\n"
        f"الرصيد المتاح: {balances['available_balance']}$\n"
    )


async def account_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        keyboard = build_manage_account_keyboard()
        keyboard.append(back_to_user_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=stringify_balance_info(user_id=update.effective_user.id),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


account_balance_handler = CallbackQueryHandler(account_balance, "^account balance$")
