from typing import Optional

from telebot import types

from accounts.models import User
from core.models import Employee
from core.telegram.decorators import infuse_user
from core.telegram.keyboards import get_online_keyboard_markup
from lunchegram import bot


__all__ = ['set_online', 'online_callback_query']


@bot.message_handler(commands=['online'])
@infuse_user()
def set_online(user: Optional[User], message):
    if user:
        bot.send_message(
            message.chat.id,
            "Choose groups in which you want to go online:",
            reply_markup=get_online_keyboard_markup(user))


@bot.callback_query_handler(func=lambda c: c.data.startswith('online'))
@infuse_user()
def online_callback_query(user: Optional[User], query: types.CallbackQuery):
    data = query.data
    company_id = data.split(':')[1]
    if user:
        try:
            employee = Employee.objects.filter(user=user, company_id=company_id, state=Employee.State.offline).get()
        except Employee.DoesNotExist:
            pass
        else:
            employee.state = Employee.State.online
            employee.save()
            bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=get_online_keyboard_markup(user))
    # Answer callback even if user isn't authenticated
    bot.answer_callback_query(
        query.id,
        show_alert=False)
