"""Parse Marathi / Hinglish WhatsApp-style property messages into Property fields."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from .models import Property

# Multiply-like separators used in plot sizes: 50×90, 50x90, 50*90
_DIM_SEP = r"[xX×✕\*]"

_AREA_PATTERNS: list[tuple[str, str]] = [
    (r"नागप[ूु]र|nagpur", Property.Area.NAGPUR),
    (r"अकोला|akola", Property.Area.AKOLA),
    (r"यवतमाळ|yavatmal", Property.Area.YAVATMAL),
    (r"वर्धा|wardha", Property.Area.WARDHA),
    (r"चंद्रप[ूु]र|chandrapur", Property.Area.CHANDRAPUR),
    (r"भंडारा|bhandara", Property.Area.BHANDARA),
    (r"गोंदिया|gondia", Property.Area.GONDIA),
    (r"वाशिम|washim", Property.Area.WASHIM),
    (r"गडचिरोली|gadchiroli", Property.Area.GADCHIROLI),
    (r"बडनेरा|badnera", Property.Area.BADNERA),
    (r"दर्याप[ूु]र|daryapur", Property.Area.DARYAPUR),
    (r"अचलप[ूु]र|achalpur", Property.Area.ACHALPUR),
    (r"मोर्शी|morshi", Property.Area.MORSHI),
    (r"वरुड|warud", Property.Area.WARUD),
    (r"चांद[ूु]र\s*बाजार|chandur\s*bazar", Property.Area.CHANDUR_BAZAR),
    (r"चांद[ूु]र\s*(?:रेल्वे|rly|railway)|chandur\s*(?:rly|railway)", Property.Area.CHANDUR_RLY),
    (r"अंजनगाव|anjangaon", Property.Area.ANJANGAON),
    (r"धामणगाव|dhamangaon", Property.Area.DHAMANGAON),
    (r"तिवसा|tiwsa", Property.Area.TIWSA),
    (r"नांदगाव|nandgaon", Property.Area.NANDGAON_KHANDESH),
    (r"भातकुली|bhatkuli", Property.Area.BHATKULI),
    (r"अमरावती|amravati", Property.Area.AMRAVATI_CITY),
]

_TYPE_PATTERNS: list[tuple[str, str]] = [
    (r"फ्लॅट|फ्लॅट्|flat|अपार्टमेंट|apartment", Property.PropertyType.FLAT),
    (r"शॉप|दुकान|shop|गोडाऊन|godown|warehouse", Property.PropertyType.SHOP),
    (r"शेत|farm|कृषि|agricultural\s*land|शेती", Property.PropertyType.FARM),
    (r"घर|बंगला|house|bungalow|रो हाउस|row\s*house", Property.PropertyType.HOUSE),
    (r"प्लॉट|plot|जमीन|जमिनी|भूमि|नाका\s*प्लॉट", Property.PropertyType.PLOT),
]

_TYPE_LABELS_MR = {
    Property.PropertyType.PLOT: "प्लॉट",
    Property.PropertyType.FLAT: "फ्लॅट",
    Property.PropertyType.HOUSE: "घर",
    Property.PropertyType.SHOP: "शॉप",
    Property.PropertyType.FARM: "शेत",
    Property.PropertyType.OTHER: "मालमत्ता",
}

_AREA_LABELS = dict(Property.Area.choices)


def _to_int(num: str) -> int | None:
    try:
        return int(re.sub(r"[,\s]", "", num))
    except ValueError:
        return None


def _to_decimal(num: str) -> Decimal | None:
    try:
        return Decimal(re.sub(r"[,\s]", "", num))
    except (InvalidOperation, ValueError):
        return None


def _detect_property_type(text: str) -> str:
    lower = text.lower()
    for pattern, ptype in _TYPE_PATTERNS:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            return ptype
    return Property.PropertyType.PLOT


def _is_commercial(text: str) -> bool:
    return bool(
        re.search(
            r"कॉमर्सियल|कमर्शियल|व्यावसायिक|commercial|बिझनेस|business",
            text,
            flags=re.IGNORECASE,
        )
    )


def _detect_area(text: str) -> str:
    for pattern, area in _AREA_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return area
    return Property.Area.AMRAVATI_CITY


def _detect_deal_status(text: str) -> str:
    if re.search(r"विकले|विकला|sold\b|deal\s*done|बंद\s*झाल", text, flags=re.IGNORECASE):
        return Property.DealStatus.SOLD
    if re.search(
        r"negotiation|वाटाघाट|अंडर\s*नेगो|under\s*nego|बुकिंग|booking",
        text,
        flags=re.IGNORECASE,
    ):
        return Property.DealStatus.UNDER_NEGOTIATION
    return Property.DealStatus.AVAILABLE


def _extract_sq_ft(text: str) -> int | None:
    # 50×90=4500 or 50x90 = 4500
    m = re.search(
        rf"(\d[\d,]*)\s*{_DIM_SEP}\s*(\d[\d,]*)\s*=\s*(\d[\d,]*)",
        text,
    )
    if m:
        product = _to_int(m.group(3))
        if product and product > 50:
            return product
        a, b = _to_int(m.group(1)), _to_int(m.group(2))
        if a and b and a * b > 50:
            return a * b

    # Explicit sq ft / स्क्वेअर फुट
    m = re.search(
        r"(\d[\d,]*)\s*(?:स्क्वेअर\s*फुट|स्क्वे\.?\s*फु\.?|चौ\.?\s*फु\.?|"
        r"sq\.?\s*ft\.?|sqft|sft)",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        val = _to_int(m.group(1))
        if val and val > 50:
            return val

    # Dimension only: 50×90 → multiply
    m = re.search(rf"(\d[\d,]*)\s*{_DIM_SEP}\s*(\d[\d,]*)", text)
    if m:
        a, b = _to_int(m.group(1)), _to_int(m.group(2))
        if a and b and 100 < a * b < 500_000:
            return a * b

    # Lone large number near "प्लॉट" (fallback)
    m = re.search(r"(\d[\d,]{2,})\s*(?:फुट|ft)", text, flags=re.IGNORECASE)
    if m:
        val = _to_int(m.group(1))
        if val and val > 50:
            return val

    return None


def _extract_acres(text: str) -> Decimal | None:
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:एकर|एकड़|acres?)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    value = _to_decimal(match.group(1))
    if value and value > 0:
        return value.quantize(Decimal("0.01"))
    return None


def _extract_bhk(text: str) -> int | None:
    match = re.search(
        r"(\d+)\s*(?:bhk|b\.?\s*h\.?\s*k|बी\.?\s*एच\.?\s*के|बीएचके)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    value = int(match.group(1))
    if 1 <= value <= 10:
        return value
    return None


def _extract_price_per_sq_ft(text: str) -> Decimal | None:
    m = re.search(
        r"(?:₹|rs\.?|रु\.?)?\s*(\d[\d,]*(?:\.\d+)?)\s*"
        r"(?:प्रति\s*(?:स्क्वेअर\s*)?फुट|/?\s*sq\.?\s*ft\.?|/\s*sft|rate)",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        return _to_decimal(m.group(1))
    return None


def _extract_total_price(text: str) -> Decimal | None:
    # 45 लाख / 1.5 कोटी
    m = re.search(
        r"(?:₹|rs\.?|रु\.?)?\s*(\d+(?:\.\d+)?)\s*(लाख|lakh|lac|कोटी|करोड|crore)",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        num = _to_decimal(m.group(1))
        if num is None:
            return None
        unit = m.group(2).lower()
        if unit in ("लाख", "lakh", "lac"):
            return num * Decimal("100000")
        return num * Decimal("10000000")

    m = re.search(
        r"(?:एकूण|total|किंमत|price|रक्कम)\s*[:\-]?\s*(?:₹|rs\.?|रु\.?)?\s*(\d[\d,]*(?:\.\d+)?)",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        val = _to_decimal(m.group(1))
        if val and val >= 10_000:
            return val
    return None


def _extract_location_detail(text: str, area_code: str) -> str:
    """Best-effort landmark / road snippet from the message body."""
    cleaned = text
    # Drop contact block
    cleaned = re.split(r"संपर्क|contact|फोन|phone|whatsapp|व्हाट्स", cleaned, flags=re.IGNORECASE)[0]
    # Prefer text after ":-" or ":" near sale keywords
    m = re.search(
        r"(?:विकणे\s*आहे|विक्री|for\s*sale|available)[:\-\s]*(.+)",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    chunk = m.group(1) if m else cleaned

    # Cut at sq-ft / dimension / facing / contact leftovers
    chunk = re.split(
        rf"\d[\d,]*\s*{_DIM_SEP}|\d[\d,]*\s*(?:स्क्वेअर|sq\.?\s*ft)|"
        r"पूर्व|पश्चिम|उत्तर|दक्षिण|मुखी|facing|संपर्क",
        chunk,
        flags=re.IGNORECASE,
    )[0]

    chunk = re.sub(r"[\r\n]+", " ", chunk)
    chunk = re.sub(r"\s{2,}", " ", chunk).strip(" .-–—:")

    # Remove city name if already captured as area
    area_name = _AREA_LABELS.get(area_code, "")
    if area_name:
        chunk = re.sub(re.escape(area_name), "", chunk, flags=re.IGNORECASE).strip(" ,.-")
    chunk = re.sub(r"अमरावती|amravati", "", chunk, flags=re.IGNORECASE).strip(" ,.-")

    # Drop commercial/type prefixes left over
    chunk = re.sub(
        r"^(?:कॉमर्सियल|कमर्शियल|व्यावसायिक|commercial|प्लॉट|plot|"
        r"फ्लॅट|flat|घर|house|शॉप|shop)\s*[\(\)A-Za-z\u0900-\u097F]*\s*",
        "",
        chunk,
        flags=re.IGNORECASE,
    ).strip(" ,.-")

    return chunk[:255]


def _extract_facing(text: str) -> str:
    parts = []
    mapping = [
        (r"पूर्व|east", "पूर्व"),
        (r"पश्चिम|west", "पश्चिम"),
        (r"उत्तर|north", "उत्तर"),
        (r"दक्षिण|south", "दक्षिण"),
    ]
    for pattern, label in mapping:
        if re.search(pattern, text, flags=re.IGNORECASE):
            parts.append(label)
    if not parts:
        return ""
    return "/".join(parts) + " मुखी"


def _build_title(
    *,
    property_type: str,
    commercial: bool,
    location_detail: str,
    area_code: str,
    sq_ft: int | None,
    acres: Decimal | None = None,
    bhk: int | None = None,
) -> str:
    type_label = _TYPE_LABELS_MR.get(property_type, "मालमत्ता")
    prefix = f"व्यावसायिक {type_label}" if commercial else type_label
    area_name = _AREA_LABELS.get(area_code, "विदर्भ")
    # Short place for title — full text stays in location_detail / description
    place = (location_detail or area_name).strip()
    if len(place) > 45:
        place = place[:42].rstrip(" ,.-") + "…"
    if property_type == Property.PropertyType.FARM and acres:
        size = f"{acres:.2f}".rstrip("0").rstrip(".")
        title = f"{prefix} · {size} एकर · {place}"
    elif property_type == Property.PropertyType.FLAT and bhk:
        title = f"{bhk} BHK {prefix} · {place}"
    elif sq_ft and sq_ft > 1:
        title = f"{prefix} · {sq_ft} sq ft · {place}"
    else:
        title = f"{prefix} — {place}"
    if len(title) > 200:
        title = title[:197] + "…"
    return title


def parse_property_message(message: str) -> dict[str, Any]:
    """
    Return a dict suitable for PropertyForm initial / Property(**kwargs).

    Keys: title, description, area, location_detail, property_type,
          deal_status, sq_ft, price_per_sq_ft, total_price,
          plus meta: commercial, facing, warnings (list[str]).
    """
    raw = (message or "").strip()
    warnings: list[str] = []

    if not raw:
        return {
            "title": "",
            "description": "",
            "area": Property.Area.AMRAVATI_CITY,
            "location_detail": "",
            "property_type": Property.PropertyType.PLOT,
            "deal_status": Property.DealStatus.AVAILABLE,
            "sq_ft": None,
            "acres": None,
            "bhk": None,
            "price_per_sq_ft": None,
            "total_price": None,
            "commercial": False,
            "facing": "",
            "warnings": ["मेसेज रिकाम्या आहे / Empty message."],
        }

    property_type = _detect_property_type(raw)
    commercial = _is_commercial(raw)
    area = _detect_area(raw)
    deal_status = _detect_deal_status(raw)
    sq_ft = _extract_sq_ft(raw)
    bhk = _extract_bhk(raw)
    if bhk and property_type in (Property.PropertyType.PLOT, Property.PropertyType.OTHER):
        property_type = Property.PropertyType.FLAT
    acres = _extract_acres(raw) if property_type == Property.PropertyType.FARM else None
    if property_type != Property.PropertyType.FLAT:
        bhk = None
    price_per_sq_ft = _extract_price_per_sq_ft(raw)
    total_price = _extract_total_price(raw)
    location_detail = _extract_location_detail(raw, area)
    facing = _extract_facing(raw)

    if property_type == Property.PropertyType.FARM:
        if acres:
            sq_ft = max(1, int((acres * Decimal("43560")).quantize(Decimal("1"))))
        else:
            warnings.append("एकर सापडले नाहीत — कृपया तपासा.")
    elif property_type == Property.PropertyType.FLAT:
        if not bhk:
            warnings.append("BHK सापडले नाही — कृपया तपासा.")
        elif not sq_ft:
            sq_ft = 1
    elif not sq_ft:
        warnings.append("चौ.फुट / sq ft सापडले नाही — कृपया तपासा.")
    # Price is intentionally not required; website shows “Call for price”

    title = _build_title(
        property_type=property_type,
        commercial=commercial,
        location_detail=location_detail,
        area_code=area,
        sq_ft=sq_ft,
        acres=acres,
        bhk=bhk,
    )

    desc_parts = [raw]
    if facing:
        desc_parts.append(f"\n\nदिशा / Facing: {facing}")
    description = "\n".join(desc_parts).strip()

    # Derive missing price side when possible
    if property_type == Property.PropertyType.FARM and acres:
        if total_price is not None and price_per_sq_ft is None:
            price_per_sq_ft = (total_price / acres).quantize(Decimal("0.01"))
        if price_per_sq_ft is not None and total_price is None:
            total_price = (price_per_sq_ft * acres).quantize(Decimal("0.01"))
    else:
        if total_price is not None and price_per_sq_ft is None and sq_ft:
            price_per_sq_ft = (total_price / Decimal(sq_ft)).quantize(Decimal("0.01"))
        if price_per_sq_ft is not None and total_price is None and sq_ft:
            total_price = (price_per_sq_ft * Decimal(sq_ft)).quantize(Decimal("0.01"))

    return {
        "title": title,
        "description": description,
        "area": area,
        "location_detail": location_detail,
        "property_type": property_type,
        "deal_status": deal_status,
        "sq_ft": sq_ft,
        "acres": acres,
        "bhk": bhk,
        "price_per_sq_ft": price_per_sq_ft,
        "total_price": total_price,
        "commercial": commercial,
        "facing": facing,
        "warnings": warnings,
        "is_active": True,
        "is_featured": False,
    }
