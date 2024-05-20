from django.dispatch import Signal
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _

order_created = Signal()


def send_mail_receiver(sender, order, **kwargs):
    email = order.user.email
    subject = _("Order #%(order_id)d") % {"order_id": order.id}
    txt = "\n".join([str(order_item.product) for order_item in order.items.all()])
    txt += _("\Price: %(order_price)d") % {"order_price": order.price}
    txt += f"\n{order.phone}\n{order.address}"
    return send_mail(subject, txt, settings.EMAIL_HOST_USER, [email])
