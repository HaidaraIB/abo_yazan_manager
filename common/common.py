from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes
from telegram.constants import ChatType
import os
import uuid
import models
from dotenv import load_dotenv

load_dotenv()

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def check_hidden_keyboard(context: ContextTypes.DEFAULT_TYPE):
    if (
        not context.user_data.get("request_keyboard_hidden", None)
        or not context.user_data["request_keyboard_hidden"]
    ):
        context.user_data["request_keyboard_hidden"] = False

        reply_markup = ReplyKeyboardMarkup(request_buttons, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()
    return reply_markup


def build_user_keyboard():
    keyboard = []
    return InlineKeyboardMarkup(keyboard)


def build_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إعدادات الآدمن⚙️🎛",
                callback_data="admin settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="حظر/فك حظر 🔓🔒",
                callback_data="ban unban",
            )
        ],
        [
            InlineKeyboardButton(
                text="إخفاء/إظهار كيبورد معرفة الآيديات🪄",
                callback_data="hide ids keyboard",
            )
        ],
        [
            InlineKeyboardButton(
                text="رسالة جماعية👥",
                callback_data="broadcast",
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back_button(data: str):
    return [InlineKeyboardButton(text="الرجوع🔙", callback_data=data)]


def uuid_generator():
    return uuid.uuid4().hex


request_buttons = [
    [
        KeyboardButton(
            text="معرفة id مستخدم🆔",
            request_users=KeyboardButtonRequestUsers(request_id=0, user_is_bot=False),
        ),
        KeyboardButton(
            text="معرفة id قناة📢",
            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=True),
        ),
    ],
    [
        KeyboardButton(
            text="معرفة id مجموعة👥",
            request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=False),
        ),
        KeyboardButton(
            text="معرفة id بوت🤖",
            request_users=KeyboardButtonRequestUsers(request_id=3, user_is_bot=True),
        ),
    ],
]


def create_folders():
    os.makedirs("data", exist_ok=True)


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")


def calc_available_balance(user_id: int):
    my_account = models.Account.get(user_id=user_id)
    my_account_info = models.AccountInfo.get(trader_id=my_account.trader_id)

    refs = models.Referral.get(user_id=user_id)
    refs_info = models.AccountInfo.get(
        trader_ids=list(map(lambda x: x.referral_trader_id, refs))
    )

    team_balance = (
        sum(list(map(lambda x: x.vol_share, refs_info))) - my_account_info.vol_share
    )
    level_reward = 0  # TODO how to calc?
    all_time_balance = my_account_info.vol_share + team_balance + level_reward
    available_balance = all_time_balance - my_account.withdrawals

    return {
        "team_balance": team_balance,
        "level_reward": level_reward,
        "all_time_balance": all_time_balance,
        "available_balance": available_balance,
        "my_account_balance": my_account_info.vol_share,
        "withdrawals": my_account.withdrawals,
    }


async def edit_message(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    text: str,
    msg_id: int,
    reply_markup: InlineKeyboardMarkup,
):
    try:
        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=msg_id,
            text=text,
            reply_markup=reply_markup,
        )
    except:
        pass
