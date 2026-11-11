import logging
import random
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def generate_otp():
    return f"{random.randint(100000, 999999)}"


def _otp_cache_key(phone: str) -> str:
    return f"otp:{phone}"


def _rate_key(phone: str) -> str:
    return f"otp_rate:{phone}"


def can_send_otp(phone: str) -> bool:
    return cache.get(_rate_key(phone)) is None


def store_otp(phone: str, otp: str) -> None:
    cache.set(_otp_cache_key(phone), otp, timeout=settings.OTP_EXPIRY_SECONDS)
    cache.set(_rate_key(phone), True, timeout=settings.OTP_RATE_LIMIT_SECONDS)


def verify_otp(phone: str, otp: str) -> bool:
    stored = cache.get(_otp_cache_key(phone))
    if stored and stored == otp:
        cache.delete(_otp_cache_key(phone))
        return True
    return False


def _safe_console(text: str) -> None:
    """Print to console without crashing on Windows cp1252 encoding."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


def send_sms(phone: str, message: str) -> bool:
    """Send SMS via Fast2SMS. Falls back to console when DEBUG_SMS or no API key."""
    if settings.DEBUG_SMS or not settings.FAST2SMS_API_KEY:
        _safe_console(
            f"\n===== SMS (console) to {phone} =====\n{message}\n==============================\n"
        )
        logger.info("SMS console to %s: %s", phone, message)
        return True

    try:
        response = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={
                "authorization": settings.FAST2SMS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "route": "q",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": phone,
            },
            timeout=15,
        )
        data = response.json() if response.content else {}
        ok = bool(data.get("return"))
        if ok:
            logger.info("Fast2SMS sent to %s", phone)
            return True
        logger.error("Fast2SMS rejected: %s", data)
        _safe_console(f"\n===== Fast2SMS rejected =====\n{data}\nMessage for {phone}: {message}\n")
        return False
    except Exception as exc:
        logger.exception("Fast2SMS failed: %s", exc)
        _safe_console(
            f"\n===== SMS FALLBACK (console) to {phone} =====\n{message}\n==============================\n"
        )
        return False


def send_otp(phone: str, otp: str) -> bool:
    """Legacy SMS OTP (unused for login). Prefer prepare_whatsapp_otp."""
    message = f"Your OTP for Baba Khatu Shyam Real Estate is {otp}. Valid for 10 minutes. Do not share."
    store_otp(phone, otp)
    return send_sms(phone, message)


def whatsapp_otp_url(phone: str, otp: str, name: str = "") -> str:
    """Build free wa.me link (user → broker). Does not store OTP."""
    broker = (settings.FATHER_WHATSAPP or settings.FATHER_PHONE or "").strip()
    lines = [f"OTP {otp}"]
    if name:
        lines.append(f"Name: {name}")
    lines.append(f"Mobile: {phone}")
    lines.append("Please verify my number for Baba Khatu Shyam Real Estate.")
    text = "\n".join(lines)
    return f"https://wa.me/91{broker}?text={quote(text)}"


def prepare_whatsapp_otp(phone: str, otp: str, name: str = "") -> str:
    """
    Free OTP: store rate-limit marker and return wa.me link.
    User sends the prefilled message to the broker WhatsApp (incoming = free).
    """
    store_otp(phone, otp)
    return whatsapp_otp_url(phone, otp, name=name)


def interest_whatsapp_url(interest) -> str:
    """Free WhatsApp chat link to broker number — one property only per message."""
    phone = settings.FATHER_WHATSAPP or settings.FATHER_PHONE
    customer = interest.customer
    prop = interest.property
    # Keep message short and single-property (do not append / duplicate)
    text = (
        f"Interest in: {prop.title}\n"
        f"Location: {prop.location_display}\n"
        f"Name: {customer.name}\n"
        f"Mobile: {customer.phone}\n"
        f"Please call me."
    )
    return f"https://wa.me/91{phone}?text={quote(text)}"


def notify_father(interest) -> None:
    customer = interest.customer
    prop = interest.property
    message = (
        f"Interest: {customer.name} ({customer.phone}) wants "
        f"{prop.title} ({prop.location_display}). Call them."
    )

    # Also try SMS to WhatsApp number (needs Fast2SMS wallet)
    alert_phone = settings.FATHER_WHATSAPP or settings.FATHER_PHONE
    send_sms(alert_phone, message)

    if settings.FATHER_EMAIL and settings.EMAIL_HOST_USER:
        try:
            send_mail(
                subject=f"New property interest: {prop.title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.FATHER_EMAIL],
                fail_silently=True,
            )
        except Exception as exc:
            logger.exception("Email notify failed: %s", exc)
