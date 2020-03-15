from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .tokens import account_activation_token
from django.conf import settings
from .models import User


# sending email
@shared_task(name="Send Activation Mail")
def mysendmail(site, user):
    userobj = User.objects.get(user_id=user)

    user = userobj.email
    current_site = site
    subject = 'Activate Your Lyne Account'
    message = render_to_string('emails/account_activation_email.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(userobj.pk)),
        'token': account_activation_token.make_token(userobj),
    })

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [userobj.email],
        fail_silently=False,
    )
    return None
