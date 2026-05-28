def normalize_phone(phone: str) -> str:
    """Normalize phone to +7XXXXXXXXXX format."""
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone
