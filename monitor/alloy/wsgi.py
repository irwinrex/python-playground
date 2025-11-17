"""
WSGI config for alloy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alloy.settings')

import alloy.telemetry.logs_traces

from opentelemetry.instrumentation.django import DjangoInstrumentor
DjangoInstrumentor().instrument()

from opentelemetry.instrumentation.requests import RequestsInstrumentor
RequestsInstrumentor().instrument()

from opentelemetry.instrumentation.logging import LoggingInstrumentor
LoggingInstrumentor().instrument()

application = get_wsgi_application()
