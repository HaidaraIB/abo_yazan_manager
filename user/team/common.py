from telegram import InlineKeyboardButton
import models


def stringify_team_stats(user_id: int):
    refs = models.Referral.get(user_id=user_id)
    refs_info = models.AccountInfo.get(
        trader_ids=list(map(lambda x: x.referral_trader_id, refs))
    )
    return (
        "الفريق:\n"
        "-------------------------------------------------------------\n"
        f"عدد أعضاء فريقك: {len(refs)}\n"
        f"مجموع الأرصدة {sum(list(map(lambda x:x.balance, refs_info))):.2f}$\n"
        f"عدد مرات الإيداع {sum(list(map(lambda x:x.deposits_count, refs_info)))}\n"
        f"مجموع الإيداعات {sum(list(map(lambda x:x.deposits_sum, refs_info))):.2f}$\n"
        f"عدد مرات السحب {sum(list(map(lambda x:x.withdrawal_sum, refs_info)))}\n"
        f"مجموع السحوبات {sum(list(map(lambda x:x.withdrawal_count, refs_info))):.2f}$\n"
        f"حجم التداول الكلي {sum(list(map(lambda x:x.vol_share, refs_info))):.2f}$\n"
        "-------------------------------------------------------------\n"
        f"الربح: {sum(list(map(lambda x:x.turnover_clear, refs_info))):.2f}$\n"
    )


def build_team_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة إحالة ➕",
                callback_data="add ref",
            ),
            InlineKeyboardButton(
                text="إحصائيات الفريق 📊",
                callback_data="team stats",
            ),
        ]
    ]
    return keyboard
