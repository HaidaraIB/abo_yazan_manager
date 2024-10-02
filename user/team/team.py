from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from user.team.common import build_team_keyboard
from common.back_to_home_page import back_to_user_home_page_button

import models


async def team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        account = models.Account.get(user_id=update.effective_user.id)
        if not account:
            await update.callback_query.answer(
                text="ليس لديك حساب بعد، قم بإضافة حساب بالضغط على زر حسابي 👤",
                show_alert=True,
            )
            return

        refs = list(
            map(
                lambda x: str(x.referral_trader_id),
                models.Referral.get(user_id=update.effective_user.id),
            )
        )
        keyboard = build_team_keyboard()
        keyboard.append(back_to_user_home_page_button[0])
        await update.callback_query.edit_message_text(
            text="الفريق:\n\n" + "\n".join(refs),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


team_handler = CallbackQueryHandler(team, "^team$")
