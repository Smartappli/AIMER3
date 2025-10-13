from __future__ import annotations

import asyncio
import logging
from urllib.parse import urljoin

from django.core.mail import EmailMessage
from django.urls import reverse
from django.conf import settings

logger = logging.getLogger(__name__)

async def send_email(subject: str, email: str, message: str) -> None:
    try:
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        msg = EmailMessage(subject, message, email_from, recipient_list)

        def _send_blocking():
            # .send() retourne le nombre de messages envoyés
            return msg.send(fail_silently=False)

        sent = await asyncio.to_thread(_send_blocking)
        if sent != 1:
            logger.warning("Email not sent (count=%s) to %s for subject '%s'", sent, email, subject)

    except Exception as e:
        logger.exception("Failed to send email to %s for subject '%s': %s", email, subject, e)


def get_absolute_url(path: str) -> str:
    """Build an absolute URL from BASE_URL and a relative path."""
    base = getattr(settings, "BASE_URL", "").rstrip("/") + "/"
    return urljoin(base, path.lstrip("/"))

async def send_verification_email(email: str, token: str) -> None:
    subject = "Verify your email"
    verification_url = get_absolute_url(reverse('verify-email', kwargs={'token': token}))
    message = f"Hi,\n\nPlease verify your email using this link: {verification_url}"
    await send_email(subject, email, message)

async def send_password_reset_email(email: str, token: str) -> None:
    subject = "Reset your password"
    reset_url = get_absolute_url(reverse('reset-password', kwargs={'token': token}))
    message = f"Hi,\n\nPlease reset your password using this link: {reset_url}"
    await send_email(subject, email, message)
