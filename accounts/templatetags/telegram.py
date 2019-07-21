from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('accounts/_telegram_widget.html')
def telegram_widget():
    return {
        'domain': settings.TELEGRAM_WIDGET_DOMAIN,
    }
