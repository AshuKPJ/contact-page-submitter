"""Application constants"""

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
]

# Browser launch arguments
BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
]

# Form field detection patterns
FORM_FIELD_PATTERNS = {
    "name": ['input[name*="name"]:not([name*="first"]):not([name*="last"])'],
    "first_name": ['input[name*="first"]', 'input[name*="fname"]'],
    "last_name": ['input[name*="last"]', 'input[name*="lname"]'],
    "email": ['input[type="email"]', 'input[name*="email"]'],
    "phone": ['input[type="tel"]', 'input[name*="phone"]'],
    "message": ['textarea[name*="message"]', 'textarea[name*="comment"]'],
}

# Contact form indicators
CONTACT_FORM_INDICATORS = [
    "contact",
    "message",
    "inquiry",
    "email",
    "send",
    "submit",
    "get in touch",
    "reach out",
]

# Email exclusion patterns
EXCLUDED_EMAIL_PATTERNS = [
    "noreply@",
    "no-reply@",
    "donotreply@",
    "admin@",
    "webmaster@",
    "postmaster@",
]
