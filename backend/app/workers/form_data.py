def get_form_data(profile):
    if profile:
        return {
            "name": f"{profile.first_name or ''} {profile.last_name or ''}".strip()
            or "John Doe",
            "email": profile.email or "contact@example.com",
            "message": profile.message or "I am interested in your services.",
            "phone": profile.phone_number or "",
        }
    return {
        "name": "John Doe",
        "email": "contact@example.com",
        "message": "I am interested in your services.",
    }
