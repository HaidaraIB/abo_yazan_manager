import models
from common.common import calc_available_balance


def stringify_balance_info(user_id: int):
    balances = calc_available_balance(user_id=user_id)
    return (
        "<b>الرصيد (الربح)</b>\n"
        f"من حسابك: <b>{balances['my_account_balance']:.2f}$</b>\n"
        f"من الفريق: <b>{balances['team_balance']:.2f}$</b>\n"
        f"هدايا المستوى: <b>{balances['level_reward']:.2f}$</b>\n"
        "-------------------------------------------------------------\n"
        f"المجموع في كل الوقت: <b>{balances['all_time_balance']:.2f}$</b>\n"
        f"السحوبات: <b>{balances['withdrawals']:.2f}$</b>\n"
        f"الرصيد المتاح: <code>{balances['available_balance']:.2f}</code>$\n"
    )


def stringify_team_stats(user_id: int):
    refs = models.Referral.get(user_id=user_id)
    refs_info = models.AccountInfo.get(
        trader_ids=list(map(lambda x: x.referral_trader_id, refs))
    )

    return (
        "الفريق:\n"
        + "\n".join(list(map(lambda x: f"<code>{x.referral_trader_id}</code>", refs)))
        + "\n-------------------------------------------------------------\n"
        f"عدد أعضاء فريقك: <b>{len(refs)}</b>\n"
        f"مجموع الأرصدة <b>{sum(list(map(lambda x:x.balance, refs_info))):.2f}$</b>\n"
        f"عدد مرات الإيداع <b>{sum(list(map(lambda x:x.deposits_count, refs_info)))}</b>\n"
        f"مجموع الإيداعات <b>{sum(list(map(lambda x:x.deposits_sum, refs_info))):.2f}$</b>\n"
        f"عدد مرات السحب <b>{sum(list(map(lambda x:x.withdrawal_sum, refs_info)))}</b>\n"
        f"مجموع السحوبات <b>{sum(list(map(lambda x:x.withdrawal_count, refs_info))):.2f}$</b>\n"
        f"حجم التداول الكلي <b>{sum(list(map(lambda x:x.vol_share, refs_info))):.2f}$</b>\n"
        "-------------------------------------------------------------\n"
        f"الربح: <b>{sum(list(map(lambda x:x.turnover_clear, refs_info))):.2f}$</b>\n\n"
    )


def stringify_account_info(info: models.AccountInfo):
    return (
        f"حسابك في كيوتيكس <code>{info.trader_id}</code>\n"
        "-------------------------------------------------------------\n"
        f"المستوى: <b>{info.level}</b>\n"
        "نسبه الربح: <b>{}%</b>\n"
        "-----------------------------------------------------------------\n"
        f"رصيدك: <b>{info.balance}$</b>\n"
        f"عدد مرات الايداع: <b>{info.deposits_count}</b>\n"
        f"مجموع الايداعات: <b>{info.deposits_sum}$</b>\n"
        f"عدد مرات السحب: <b>{info.withdrawal_count}</b>\n"
        f"مجموع السحوبات: <b>{info.withdrawal_sum}$</b>\n"
        f"حجم التداول الحقيقي: <b>{info.vol_share}$</b>\n"
        "-----------------------------------------------------------------\n"
        f"الربح: <b>{info.turnover_clear}$</b>\n"
    )


def stringify_withdraw_order(amount: str, address: str):
    return (
        "<b>طلب سحب 📤</b>\n\n"
        f"المبلغ: <code>{amount}</code>\n"
        f"المحفظة: <code>{address}</code>\n\n"
    )
