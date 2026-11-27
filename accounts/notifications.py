"""Create in-site notifications (and optionally email them)."""
import uuid

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape, linebreaks

from .models import Notification

SITE_URL = 'https://mkhmd.uk'


def _absolute(link):
    if not link:
        return SITE_URL + '/'
    return link if link.startswith('http') else SITE_URL + link


def _send_email(user, title, message, link):
    url = _absolute(link)
    text = f"{title}\n\n{message}\n\nOpen: {url}\n"
    html = f"""<!DOCTYPE html><html><body style="margin:0;background:#f4f4f7;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;">
<table role="presentation" width="100%" style="padding:32px 0;"><tr><td align="center">
<table role="presentation" width="560" style="max-width:100%;background:#fff;border-radius:14px;overflow:hidden;">
<tr><td style="background:linear-gradient(135deg,#7c3aed,#5b21b6);padding:28px 32px;color:#fff;">
<div style="font-family:monospace;font-size:14px;opacity:.85;">&lt;abdurohman/&gt;</div>
<h1 style="margin:8px 0 0;font-size:22px;">{escape(title)}</h1></td></tr>
<tr><td style="padding:28px 32px;color:#1f2937;font-size:15px;line-height:1.6;">{linebreaks(escape(message))}
<p style="margin:28px 0 0;"><a href="{escape(url)}" style="background:#7c3aed;color:#fff;text-decoration:none;padding:12px 22px;border-radius:8px;font-weight:600;display:inline-block;">Open mkhmd.uk</a></p>
</td></tr>
<tr><td style="padding:16px 32px;background:#fafafa;color:#9ca3af;font-size:12px;">You received this because you have an account on mkhmd.uk.</td></tr>
</table></td></tr></table></body></html>"""
    mail = EmailMultiAlternatives(title, text, settings.DEFAULT_FROM_EMAIL, [user.email])
    mail.attach_alternative(html, 'text/html')
    mail.send(fail_silently=False)


def notify(users, title, message='', link='', level='info', sent_by=None, email=False):
    """
    Send a notification to each user in `users`.
    Returns (number_created, number_emailed, batch_id).
    """
    batch = uuid.uuid4()
    users = list(users)
    items = [
        Notification(user=u, title=title, message=message, link=link, level=level,
                     batch=batch, sent_by=sent_by)
        for u in users
    ]
    Notification.objects.bulk_create(items)

    emailed = 0
    if email:
        emailed_ids = []
        for user in users:
            if not user.email:
                continue
            try:
                _send_email(user, title, message, link)
                emailed += 1
                emailed_ids.append(user.id)
            except Exception as exc:  # keep going if one address fails
                print(f"Notification email to {user.email} failed: {exc}")
        if emailed_ids:
            Notification.objects.filter(batch=batch, user_id__in=emailed_ids).update(emailed=True)
    return len(items), emailed, batch
