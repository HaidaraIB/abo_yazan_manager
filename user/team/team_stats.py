from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from user.team.common import stringify_team_stats, build_team_keyboard
from common.back_to_home_page import back_to_user_home_page_button


async def team_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await update.callback_query.answer()
        keyboard = build_team_keyboard()
        keyboard.append(back_to_user_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=stringify_team_stats(user_id=update.effective_user.id),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

team_stats_handler = CallbackQueryHandler(team_stats, "^team stats$")