"""
WSGI config for exchange project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchange.settings")
from django.conf import settings
    
print(settings.DEBUG, os.environ.get('RUN_MAIN'),  os.environ.get('WERKZEUG_RUN_MAIN'))
if settings.DEBUG:
# #     if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
    import debugpy
    try:
        debugpy.listen(("0.0.0.0", 3003))
        print('Attached!')
    except:
        print('Not attached, jejeje!')
        
application = get_wsgi_application()
