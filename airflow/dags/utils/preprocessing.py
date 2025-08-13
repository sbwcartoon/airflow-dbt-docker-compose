def mask_email(email: str, visible_len: int = 2) -> str:
    if "@" not in email:
        raise ValueError(f"Not a valid email address: {email}")

    username, domain = email.split("@", 1)

    if len(username) <= visible_len:
        username_mask = username[0] + "*" * (len(username) - 1)
        return f"{username_mask}@{domain}"
    else:
        username_mask = username[:visible_len] + "*" * (len(username) - visible_len)
        return f"{username_mask}@{domain}"
