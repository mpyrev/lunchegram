from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path(f'webhook/{settings.WEBHOOK_URL_SECRET}/', views.webhook, name='webhook'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('companies/add/', views.CompanyCreateView.as_view(), name='company_add'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    # path('companies/<int:company_id>/schedule/add/', views.LunchScheduleCreateView.as_view(), name='lunchschedule_add'),
    path('i/<slug:invite_token>/', views.InviteLoginView.as_view(), name='company_invite'),
    path('c/<slug:invite_token>/', views.InviteConfirmView.as_view(), name='company_invite_confirm'),
    path('s/<uuid:pk>/', views.InviteSuccessView.as_view(), name='company_invite_success'),
    path('', views.IndexView.as_view(), name='index'),
]
