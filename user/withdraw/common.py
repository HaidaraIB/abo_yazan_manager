def stringify_withdraw_order(amount: str, address: str):
    return (
        "<b>طلب سحب 📤</b>\n\n"
        f"المبلغ: <code>{amount}</code>\n"
        f"المحفظة: <code>{address}</code>"
    )
