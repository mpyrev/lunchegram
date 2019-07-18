from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import render


class LoginView(DjangoLoginView):
    pass


def login(request):
    return render(request, 'accounts/login.html')
