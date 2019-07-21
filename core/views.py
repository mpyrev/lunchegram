import telebot
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, CreateView, DetailView
from telebot import types

from accounts.models import User
from core.forms import CompanyForm
from core.models import Company, Employee
from lunchegram import bot


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('dashboard'))
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'owned_companies': self.request.user.owned_companies.all(),
            'companies': self.request.user.companies.all(),
        })
        return super().get_context_data(**kwargs)


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        if self.object.privacy_mode == Company.Privacy.link:
            self.object.invite_token = self.object.generate_invite_token()
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('dashboard')


class InviteLoginView(DetailView):
    queryset = Company.objects.privacy_link()
    slug_field = 'invite_token'
    slug_url_kwarg = 'invite_token'
    template_name = 'core/invite_login.html'

    def dispatch(self, request, *args, **kwargs):
        company = self.get_object()
        if request.user.is_authenticated:
            return redirect(reverse('company_invite_confirm', args=(company.invite_token,)))
        request.session['next'] = reverse('company_invite', args=(company.invite_token,))
        return super().dispatch(request, *args, **kwargs)


class InviteConfirmView(LoginRequiredMixin, DetailView):
    queryset = Company.objects.privacy_link()
    slug_field = 'invite_token'
    slug_url_kwarg = 'invite_token'
    template_name = 'core/invite_confirm.html'

    def post(self, request, *args, **kwargs):
        self.employee = Employee.objects.get_or_create(
            company=self.get_object(),
            user=request.user,
        )[0]
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('company_invite_success', args=(self.employee.pk,))


class InviteSuccessView(LoginRequiredMixin, DetailView):
    queryset = Employee.objects.all()
    template_name = 'core/invite_success.html'


##### Telegram webhooks


@never_cache
@require_POST
@csrf_exempt
def webhook(request):
    if request.headers.get('content-type') == 'application/json':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse()
    else:
        return HttpResponse(status=400)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Hi! I'm random lunch bot.")


# List user's lunch groups
@bot.message_handler(commands=['groups'])
def send_companies(message):
    uid = message.from_user.id
    user = User.objects.get_from_telegram_uid(uid)
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


def get_offline_keyboard_markup(user: User):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    employees = Employee.objects.filter(user=user, state=Employee.State.online).select_related('company')
    for employee in employees:
        company = employee.company
        buttons.append(types.InlineKeyboardButton(company.name, callback_data=f'offline:{company.pk}'))
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=['offline'])
def set_offline(message):
    uid = message.from_user.id
    user = User.objects.get_from_telegram_uid(uid)
    if user:
        bot.send_message(
            message.chat.id,
            "Choose groups in which you want to go offline:",
            reply_markup=get_offline_keyboard_markup(user))


@bot.callback_query_handler(func=lambda c: c.data.startswith('offline'))
def private_query(query: types.CallbackQuery):
    data = query.data
    company_id = data.split(':')[1]
    uid = query.from_user.id
    user = User.objects.get_from_telegram_uid(uid)
    if user:
        try:
            employee = Employee.objects.filter(user=user, company_id=company_id, state=Employee.State.online).get()
        except Employee.DoesNotExist:
            pass
        else:
            employee.state = Employee.State.offline
            employee.save()
            bot.answer_callback_query(
                query.id,
                text='Hello! This callback.',
                show_alert=False)
            bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=get_offline_keyboard_markup(user))


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, "Sorry, I don't know this command.")
