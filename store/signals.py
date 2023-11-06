from django.dispatch import Signal
from django.core.mail import send_mail
from django.conf import settings

order_created = Signal()


def send_mail_receiver(sender, order, **kwargs):
    email = order.user.email
    subject = f"Sifarisiniz #{order.id}"
    txt = "\n".join([str(order_item.product) for order_item in order.items.all()])
    txt += f"\nPrice: {order.price}"
    txt += f"\n{order.phone}\n{order.address}"
    return send_mail(subject, txt, settings.EMAIL_HOST_USER, [email])
