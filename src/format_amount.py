def format_amount(amount: int, decimals: int):
    amount_str = str(amount)
    if len(amount_str) < decimals + 1:
        amount_str = amount_str.zfill(decimals + 1)
    integers_str = amount_str[:-decimals] if decimals > 0 else amount_str
    decimals_str = amount_str[-decimals:] if decimals > 0 else ''
    output = integers_str
    if decimals > 0 and int(decimals_str) > 0:
        output += f".{decimals_str.rstrip('0')}"
    return output