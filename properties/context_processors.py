from django.conf import settings


def business_info(request):
    return {
        "FATHER_PHONE": settings.FATHER_PHONE,
        "FATHER_WHATSAPP": settings.FATHER_WHATSAPP,
        "FATHER_NAME": settings.FATHER_NAME,
        "FATHER_NAME_HI": settings.FATHER_NAME_HI,
        "FATHER_OWNER": settings.FATHER_OWNER,
        "whatsapp_link": f"https://wa.me/91{settings.FATHER_WHATSAPP}",
        "call_link": f"tel:+91{settings.FATHER_PHONE}",
    }
