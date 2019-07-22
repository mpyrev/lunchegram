from telebot import types

from accounts.models import User
from core.models import Employee


def get_offline_keyboard_markup(user: User):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    employees = Employee.objects.filter(user=user, state=Employee.State.online).select_related('company')
    for employee in employees:
        company = employee.company
        buttons.append(types.InlineKeyboardButton(company.name, callback_data=f'offline:{company.pk}'))
    markup.add(*buttons)
    return markup


def get_online_keyboard_markup(user: User):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    employees = Employee.objects.filter(user=user, state=Employee.State.offline).select_related('company')
    for employee in employees:
        company = employee.company
        buttons.append(types.InlineKeyboardButton(company.name, callback_data=f'online:{company.pk}'))
    markup.add(*buttons)
    return markup
