from django.apps import AppConfig
from django.conf import settings


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    def ready(self):
        if settings.TESTING:
            return

        from . import signals
        from .models import Order

        signals.order_created.connect(
            receiver=signals.send_mail_receiver,
            sender=Order,
            dispatch_uid="email_sender",
        )
