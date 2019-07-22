from typing import Optional

from telebot import types

from accounts.models import User
from core.models import Employee
from core.telegram.decorators import infuse_user
from core.telegram.keyboards import get_offline_keyboard_markup
from lunchegram import bot


__all__ = ['set_offline', 'offline_callback_query']


@bot.message_handler(commands=['offline'])
@infuse_user()
def set_offline(user: Optional[User], message):
    if user:
        bot.send_message(
            message.chat.id,
            "Choose groups in which you want to go offline:",
            reply_markup=get_offline_keyboard_markup(user))


@bot.callback_query_handler(func=lambda c: c.data.startswith('offline'))
@infuse_user()
def offline_callback_query(user: Optional[User], query: types.CallbackQuery):
    data = query.data
    company_id = data.split(':')[1]
    if user:
        try:
            employee = Employee.objects.filter(user=user, company_id=company_id, state=Employee.State.online).get()
        except Employee.DoesNotExist:
            pass
        else:
            employee.state = Employee.State.offline
            employee.save()
            bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=get_offline_keyboard_markup(user))
    # Answer callback even if user isn't authenticated
    bot.answer_callback_query(
        query.id,
        show_alert=False)
