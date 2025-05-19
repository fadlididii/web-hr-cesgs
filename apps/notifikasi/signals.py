from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
from django.core.mail import send_mail
from django.conf import settings

@receiver(notify)
def send_email_notification(sender, recipient, verb, description, **kwargs):
    # Handle both single recipient and QuerySet of recipients
    recipients = recipient if hasattr(recipient, '__iter__') else [recipient]
    
    for user in recipients:
        if hasattr(user, 'email') and user.email:
            subject = f"Notifikasi Pengajuan - {verb}"
            send_mail(
                subject,
                description,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )