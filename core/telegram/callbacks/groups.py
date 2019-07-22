from typing import Optional

from accounts.models import User
from core.models import Employee
from core.telegram.decorators import infuse_user
from lunchegram import bot


__all__ = ['send_companies']


@bot.message_handler(commands=['groups'])
@infuse_user()
def send_companies(user: Optional[User], message):
    msg = "Looks like you do not participate in any lunch groups."
    if user:
        employees = Employee.objects.filter(user=user).select_related('company')
        if employees:
            msg = "You're part of these lunch groups:\n"
            msg += '\n'.join(f'• {e.company} [{e.get_state_display()}]' for e in employees)
    bot.send_message(
        message.chat.id,
        msg,
    )
