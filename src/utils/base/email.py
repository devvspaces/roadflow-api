from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.conf import settings


def render_email_message(request: HttpRequest, template: str, context: dict = None):
    """Render email message using template and context

    :param request: http request
    :type request: HttpRequest
    :param template: email template path
    :type template: str
    :param context: context to be \
passed to template. Defaults to None.
    :type context: dict, optional
    :return: message to be sent
    :rtype: str
    """

    site = get_current_site(request)

    default_data = {
        "request": request,
        "domain": site.domain,
        'from': settings.DEFAULT_FROM_EMAIL,
        "APP_NAME": settings.APP_NAME,
    }

    context.update(default_data)

    message = render_to_string(template, context)
    return message
