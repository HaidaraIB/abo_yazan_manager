from telegram import Update
from telegram.ext import CallbackQueryHandler, InvalidCallbackData
import start
from common.common import invalid_callback_data, create_folders
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)
from common.error_handler import error_handler


from user.user_calls import *
from user.my_account import *
from user.team import *
from user.refresh import *
from user.withdraw import *

from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *

from models import create_tables

from MyApp import MyApp

from PyroClientSingleton import PyroClientSingleton


def main():
    create_folders()
    create_tables()

    app = MyApp.build_app()

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )

    # USER

    # MY ACCOUNT
    app.add_handler(manage_account_handler)

    # WITHDRAW
    app.add_handler(withdraw_handler)
    app.add_handler(mark_as_done_handler)

    # TEAM
    app.add_handler(add_ref_handler)

    # REFRESH
    app.add_handler(refresh_handler)

    # ADMIN

    # BROADCASE
    app.add_handler(broadcast_message_handler)

    # BAN
    app.add_handler(ban_unban_user_handler)

    # ADMIN SETTINGS
    app.add_handler(admin_settings_handler)
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)

    # ADMIN CALLS
    app.add_handler(start.admin_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)

    # START
    app.add_handler(start.start_command)

    # BACK TO HOME PAGE
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_error_handler(error_handler)

    PyroClientSingleton().start()

    app.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

    PyroClientSingleton().stop()
