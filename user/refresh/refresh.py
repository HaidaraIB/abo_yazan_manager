from telegram import Update, Chat
from telegram.ext import ContextTypes, CallbackQueryHandler
from custom_filters import User
from user.send_id.common import (
    extract_important_info,
    stringify_account_info,
    get_id_info,
    check_local_storage,
    check_remote_storage,
)

import models


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and User().filter(update):
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

        await update.callback_query.edit_message_text("الرجاء الانتظار...")

        for i in [*refs, account.trader_id]:
            text = await get_id_info(trader_id=i)
            
            if not text:
                continue

            is_closed = "ACCOUNT CLOSED" in text
            data = extract_important_info(text, is_closed=is_closed)

            await check_local_storage(is_closed=is_closed, data=data, trader_id=i)

            check_remote_storage(trader_id=i, is_closed=is_closed, data=data)

        await update.callback_query.answer(
            text="تم التحديث ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_text(
            text=(
                "معلومات حسابك:\n"
                + stringify_account_info(
                    info=models.AccountInfo.get(trader_id=account.trader_id)
                )
                + "اضغط /start للمتابعة."
            )
        )


refresh_handler = CallbackQueryHandler(refresh, "^refresh$")
