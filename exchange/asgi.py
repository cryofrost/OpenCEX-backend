"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""
import os

import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchange.settings")
from django.conf import settings

django.setup()
if settings.DEBUG:
    import debugpy
    try:
        debugpy.listen(("0.0.0.0", 3004))
        print('Debugger listening on port 3004')
        debugpy.wait_for_client()
    except:
        print('Ignoring consequent attempt to invoke debugger')
application = get_default_application()
