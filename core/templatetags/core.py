from django import template
from django.urls import reverse

from core.models import Company

register = template.Library()


@register.simple_tag(takes_context=True)
def invite_url(context, company: Company):
    request = context['request']
    return request.build_absolute_uri(reverse('company_invite', args=(company.invite_token,)))
