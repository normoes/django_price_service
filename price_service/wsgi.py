"""
WSGI config for price_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "price_service.settings")


# Using the 'StaticFileHandler' in production is not recommended.
# Recommendation:
#  Let 'gunicorn' handle the application by using the commented line.
#  Use 'nginx' to serve static contents.
#  Use the 'StaticFileHandler' only when developping locally.

if settings.DEBUG:
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
