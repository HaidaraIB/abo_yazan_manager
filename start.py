from telegram import (
    Update,
    Chat,
    BotCommandScopeChat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CommandHandler, ContextTypes, Application, ConversationHandler
import os
import models
from custom_filters import Admin
from common.decorators import check_if_user_banned_dec, add_new_user_dec
from common.common import build_admin_keyboard, check_hidden_keyboard

from common.stringifies import *


async def inits(app: Application):
    await models.Admin.add_new_admin(admin_id=int(os.getenv("OWNER_ID")))


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st_cmd = ("start", "start command")
    commands = [st_cmd]
    if Admin().filter(update):
        commands.append(("admin", "admin command"))
    await context.bot.set_my_commands(
        commands=commands, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )


@add_new_user_dec
@check_if_user_banned_dec
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await set_commands(update, context)
        account = models.Account.get(user_id=update.effective_user.id)
        if account:

            await update.message.reply_text(text=ACCOUNT_LEVELS_TEXT)

            balance_info_msg = await update.message.reply_text(
                text=stringify_balance_info(user_id=update.effective_user.id),
                reply_markup=InlineKeyboardMarkup.from_row(
                    [
                        InlineKeyboardButton(
                            text="سحب 📤",
                            callback_data="withdraw",
                        )
                    ]
                ),
            )
            context.user_data["balance_info_msg_id"] = balance_info_msg.id

            await update.message.reply_text(
                text="قم بدعوة الاصدقاء الى منصة كيوتيكس عن طريق مشاركه رابط الإحاله الخاص بك للحصول على على نسبه ربح من حجم التداول الكلي للأعضاء",
                reply_markup=InlineKeyboardMarkup.from_row(
                    [
                        InlineKeyboardButton(
                            text="رابط المشاركة",
                            url="https://broker-qx.pro/?lid=1011365",
                        ),
                        InlineKeyboardButton(
                            text="بونص 50%",
                            url="https://broker-qx.pro/?lid=1011365",
                        ),
                    ]
                ),
            )

            team_stats_msg = await update.message.reply_text(
                text=stringify_team_stats(user_id=update.effective_user.id),
                reply_markup=InlineKeyboardMarkup.from_row(
                    [
                        InlineKeyboardButton(
                            text="إضافة إحالة ➕",
                            callback_data="add ref",
                        ),
                    ]
                ),
            )
            context.user_data["team_stats_msg_id"] = team_stats_msg.id

            my_account_msg = await update.message.reply_text(
                text=stringify_account_info(
                    info=models.AccountInfo.get(trader_id=account.trader_id)
                ),
                reply_markup=InlineKeyboardMarkup.from_row(
                    [
                        InlineKeyboardButton(
                            text="تعديل الحساب 🆕",
                            callback_data="update account",
                        ),
                        InlineKeyboardButton(
                            text="تحديث ♻️",
                            callback_data="refresh",
                        ),
                    ]
                ),
            )
            context.user_data["my_account_msg_id"] = my_account_msg.id
            return

        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="إضافة حساب",
                    callback_data="add account",
                )
            ),
        )
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await set_commands(update, context)
        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=check_hidden_keyboard(context),
        )

        await update.message.reply_text(
            text="تعمل الآن كآدمن 🕹",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
