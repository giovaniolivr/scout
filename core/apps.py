import warnings
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Clear all sessions every time the server starts so developers
        # always begin from a logged-out state. DB access in ready() is
        # intentional here; suppress Django's advisory warning.
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', RuntimeWarning)
                from django.contrib.sessions.models import Session
                Session.objects.all().delete()
        except Exception:
            pass
