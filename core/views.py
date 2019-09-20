import telebot
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, CreateView, DetailView
from django.utils.translation import gettext as _

from core.forms import CompanyForm
from core.models import Company, Employee
# from core.tables import LunchScheduleTable
from core.tasks import send_telegram_message
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


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


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
        company = self.get_object()
        self.employee = Employee.objects.get_or_create(
            company=company,
            user=request.user,
        )[0]
        if request.user.has_telegram and request.user.telegram_account:
            send_telegram_message.delay(
                request.user.telegram_account.uid,
                _('Hi! You''ve successfully joined lunch group «{}». '
                  'You may manage your participation with /offline and /online commands.').format(company.name))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('company_invite_success', args=(self.employee.pk,))


class InviteSuccessView(LoginRequiredMixin, DetailView):
    queryset = Employee.objects.all()
    template_name = 'core/invite_success.html'


# class CompanyMixin:
#     company_pk_url_kwarg = 'company_id'
#
#     def get_company_queryset(self):
#         return Company.objects.filter(owner=self.request.user)
#
#     def get_company(self, queryset=None):
#         if queryset is None:
#             queryset = self.get_company_queryset()
#         try:
#             return queryset.get(pk=self.kwargs[self.company_pk_url_kwarg])
#         except Company.DoesNotExist:
#             raise Http404
#
#     def dispatch(self, request, *args, **kwargs):
#         self.company = self.get_company()
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         kwargs['company'] = self.company
#         return super().get_context_data(**kwargs)
#
#
# class LunchScheduleCreateView(LoginRequiredMixin, CompanyMixin, CreateView):
#     model = LunchSchedule
#     form_class = LunchScheduleForm
#
#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.company = self.company
#         self.object.save()
#         return redirect(self.get_success_url())
#
#     def get_success_url(self):
#         return reverse('company_detail', args=(self.company.pk,))


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
