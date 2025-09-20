from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, max_retries=3)
def send_email_captcha_task(self, subject, message, recipient_email):
    return send_mail(
        subject=subject,
        message=message,
        from_email=None,             # 用 settings.DEFAULT_FROM_EMAIL
        recipient_list=[recipient_email],
        fail_silently=False,
    )