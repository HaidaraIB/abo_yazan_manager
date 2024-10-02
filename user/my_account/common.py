from telegram import InlineKeyboardButton


def build_manage_account_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="تعديل الحساب",
                callback_data="update account",
            ),
            InlineKeyboardButton(
                text="الرصيد",
                callback_data="account balance",
            ),
        ],
    ]
    return keyboard
