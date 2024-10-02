from PyroClientSingleton import PyroClientSingleton
import models

import asyncio
from datetime import datetime


def extract_important_info(text: str, is_closed: bool):
    important_line_names_to_numbers_mapper = {
        "trader_id": 0,
        "country": 1,
        "registery_date": 2,
        "balance": 6,
        "deposits_count": 7,
        "deposits_sum": 8,
        "withdrawal_count": 11,
        "withdrawal_sum": 12,
        "turnover_clear": 16,
        "vol_share": 19,
    }
    if is_closed:
        important_line_names_to_numbers_mapper = {
            "trader_id": 0,
            "country": 1,
            "registery_date": 2,
            "balance": 7,
            "deposits_count": 8,
            "deposits_sum": 9,
            "withdrawal_count": 12,
            "withdrawal_sum": 13,
            "turnover_clear": 17,
            "vol_share": 20,
        }
    all_lines = text.split("\n")
    important_lines: dict[str, float | int | str] = {}

    for line_name, line_number in important_line_names_to_numbers_mapper.items():
        try:
            important_lines[line_name] = all_lines[line_number].split("#")[1].strip()
        except IndexError:
            try:
                important_lines[line_name] = (
                    all_lines[line_number].split("$")[1].strip()
                )
            except IndexError:
                try:
                    important_lines[line_name] = (
                        all_lines[line_number].split(":")[1].strip()
                    )
                except:
                    pass

    date_string = important_lines["registery_date"][:-1]
    date_format = "%d.%m.%Y"  # This format specifies day, month, year
    date_object = datetime.strptime(date_string, date_format).date()
    important_lines["registery_date"] = date_object

    def clean_and_calculate(key, multiplier):
        try:
            value = float(important_lines[key].replace(",", ""))
            if multiplier:
                value *= multiplier
            important_lines[key] = f"{value:.2f}"
        except ValueError:
            important_lines[key] = 0

    keys = ["turnover_clear", "vol_share", "balance", "deposits_sum", "withdrawal_sum"]
    multipliers_dict = {
        "turnover_clear": 0.4,
        "vol_share": 0.4,
        "balance": 0,
        "deposits_sum": 0,
        "withdrawal_sum": 0,
    }
    for key in keys:
        clean_and_calculate(
            key,
            multiplier=multipliers_dict[key],
        )

    return important_lines


def stringify_for_data_channel(info: models.AccountInfo):
    return info.__str__()


async def get_id_info(trader_id: str):
    cpyro = PyroClientSingleton()
    sent = await cpyro.send_message(
        chat_id="@QuotexPartnerBot",
        text=trader_id,
    )
    await asyncio.sleep(2)
    rcvd = await cpyro.get_messages(
        chat_id="@QuotexPartnerBot",
        message_ids=sent.id + 1,
    )
    if (not rcvd.text) or ("not found" in rcvd.text) or ("Trader #" not in rcvd.text):
        return False

    return rcvd.text


async def check_local_storage(is_closed: bool, data: dict, trader_id: str):
    stored_account = models.AccountInfo.get(trader_id=trader_id)
    if stored_account:
        if is_closed and not stored_account.closed:
            await models.AccountInfo.close(trader_id=trader_id)
        await models.AccountInfo.update_info(data=data, is_closed=is_closed)
    else:
        await models.AccountInfo.add(data=data, is_closed=is_closed)


def check_remote_storage(trader_id: str, is_closed: bool, data: dict):
    remote_data = models.RemoteDB.get_from_remote_db(trader_id=trader_id)
    if remote_data:
        models.RemoteDB.update_into_remote_db(
            data=list(data.values()), is_closed=int(is_closed)
        )
    else:
        models.RemoteDB.insert_into_remote_db(
            data=list(data.values()), is_closed=int(is_closed)
        )
