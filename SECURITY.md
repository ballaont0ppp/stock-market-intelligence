# Security Implementation Guide

This document outlines the security measures implemented in the Stock Portfolio Management Platform.

## Overview

The platform implements multiple layers of security to protect user data and prevent common web vulnerabilities:

1. **Session Security** - Secure cookie configuration
2. **CSRF Protection** - Cross-Site Request Forgery prevention
3. **SQL Injection Prevention** - Parameterized queries and input validation
4. **XSS Prevention** - Cross-Site Scripting protection
5. **Security Headers** - HTTP security headers

## 1. Session Security

### Configuration

Session security is configured in `app/config.py`:

```python
# Session Security
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # 24 hour timeout
SESSION_COOKIE_HTTPONLY = True   # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_SECURE = False    # True in production (requires HTTPS)
```

### Production Settings

In production (`ProductionConfig`), additional security is enforced:

```python
SESSION_COOKIE_SECURE = True  # Requires HTTPS
```

### Features

- **24-hour session timeout**: Sessions expire after 24 hours of inactivity
- **HttpOnly cookies**: Prevents JavaScript from accessing session cookies (XSS protection)
- **SameSite=Lax**: Protects against CSRF attacks
- **Secure flag (production)**: Ensures cookies are only sent over HTTPS

## 2. CSRF Protection

### Implementation

CSRF protection is implemented using Flask-WTF:

```python
# In app/__init__.py
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
csrf.init_app(app)

# In app/config.py
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None
```

### Usage in Forms

All WTForms automatically include CSRF tokens:

```html
<form method="POST">
    {{ form.hidden_tag() }}  <!-- Includes CSRF token -->
    <!-- form fields -->
</form>
```

For non-WTForm POST requests, manually add CSRF token:

```html
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- form fields -->
</form>
```

### Error Handling

CSRF validation failures are handled in `app/utils/error_handlers.py`:

```python
@app.errorhandler(400)
def bad_request_error(error):
    if 'csrf' in str(error).lower():
        flash('Security validation failed. Please try again.', 'error')
        return redirect(request.referrer or url_for('dashboard.index'))
```

## 3. SQL Injection Prevention

### Primary Defense: SQLAlchemy ORM

The application uses SQLAlchemy ORM for all database operations, which automatically uses parameterized queries:

```python
# ✓ SAFE - Parameterized query via ORM
user = User.query.filter_by(email=user_email).first()

# ✓ SAFE - Multiple conditions
holdings = Holdings.query.filter(
    Holdings.user_id == user_id,
    Holdings.quantity > 0
).all()
```

### Raw SQL Queries (When Necessary)

If raw SQL is absolutely necessary, use `safe_execute_query()` from `app/utils/sql_security.py`:

```python
from app.utils.sql_security import safe_execute_query

# ✓ SAFE - Parameterized raw query
result = safe_execute_query(
    "SELECT * FROM users WHERE email = :email",
    {"email": user_email}
)
```

### Input Validation

All user inputs are validated using functions from `app/utils/validators.py`:

```python
from app.utils.validators import (
    validate_email,
    validate_amount,
    validate_quantity,
    sanitize_sql_input
)

# Validate email format
is_valid, error_msg = validate_email(email)

# Validate monetary amount
is_valid, error_msg = validate_amount(amount, min_value=0.01)

# Sanitize input (defense-in-depth)
clean_input = sanitize_sql_input(user_input)
```

### What NOT to Do

```python
# ✗ DANGEROUS - String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!

# ✗ DANGEROUS - String formatting
query = "SELECT * FROM users WHERE id = {}".format(user_id)  # VULNERABLE!
```

## 4. XSS Prevention

### Primary Defense: Jinja2 Auto-Escaping

Jinja2 automatically escapes all variables in templates:

```html
<!-- ✓ SAFE - Auto-escaped -->
<p>{{ user.full_name }}</p>
<p>{{ comment.text }}</p>
```

### Content Security Policy (CSP)

CSP headers are automatically added to all responses in `app/utils/xss_protection.py`:

```python
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  img-src 'self' data: https:;
  frame-ancestors 'none';
```

### Custom Jinja2 Filters

Two custom filters are available for additional protection:

```html
<!-- Sanitize URL -->
<a href="{{ user_url|safe_url }}">Link</a>

<!-- Sanitize user input -->
<p>{{ user_comment|sanitize }}</p>
```

### JavaScript Context

When embedding data in JavaScript, use the `tojson` filter:

```html
<script>
    // ✓ SAFE - Properly escaped JSON
    var userData = {{ user_data|tojson }};
</script>
```

### What NOT to Do

```html
<!-- ✗ DANGEROUS - Unescaped user input -->
<p>{{ user_comment|safe }}</p>

<!-- ✗ DANGEROUS - Direct JavaScript injection -->
<script>
    var name = "{{ user_name }}";  // Use |tojson instead!
</script>
```

## 5. Security Headers

### Implemented Headers

All responses include the following security headers (configured in `app/utils/xss_protection.py`):

#### X-Content-Type-Options
```
X-Content-Type-Options: nosniff
```
Prevents browsers from MIME-sniffing responses away from the declared content-type.

#### X-Frame-Options
```
X-Frame-Options: DENY
```
Prevents the page from being embedded in frames (clickjacking protection).

#### X-XSS-Protection
```
X-XSS-Protection: 1; mode=block
```
Enables browser's built-in XSS filter.

#### Strict-Transport-Security (Production Only)
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
Forces HTTPS for 1 year. Only enabled in production.

#### Referrer-Policy
```
Referrer-Policy: strict-origin-when-cross-origin
```
Controls referrer information sent with requests.

#### Permissions-Policy
```
Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=()
```
Disables unnecessary browser features.

### Implementation

Headers are automatically added to all responses via `@app.after_request`:

```python
@app.after_request
def add_security_headers_to_response(response):
    from app.utils.xss_protection import add_security_headers
    is_production = not app.debug and not app.testing
    response = add_security_headers(response, is_production=is_production)
    return response
```

## Additional Security Measures

### Password Hashing

Passwords are hashed using bcrypt with a work factor of 12:

```python
# In app/config.py
BCRYPT_LOG_ROUNDS = 12

# In app/services/auth_service.py
hashed = bcrypt.generate_password_hash(password).decode('utf-8')
```

### Rate Limiting

Login attempts are rate-limited (implemented in `app/utils/rate_limiter.py`):
- Maximum 5 failed attempts per email
- 15-minute cooldown period

### Input Validation

Comprehensive validation functions in `app/utils/validators.py`:
- `validate_email()` - Email format validation
- `validate_password()` - Password strength requirements
- `validate_amount()` - Monetary value validation
- `validate_quantity()` - Stock quantity validation
- `validate_stock_symbol()` - Symbol format validation
- `sanitize_string()` - General string sanitization
- `sanitize_sql_input()` - SQL-specific sanitization

## Security Checklist

### Development
- [ ] Use HTTPS in development (optional)
- [ ] Test CSRF protection on all forms
- [ ] Validate all user inputs
- [ ] Use SQLAlchemy ORM for database queries
- [ ] Never use `|safe` filter with user input
- [ ] Test XSS prevention in templates

### Production Deployment
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Use strong `SECRET_KEY` (not default)
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up database user with minimal permissions
- [ ] Enable application logging
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Backup encryption keys securely

## Security Testing

### Manual Testing

1. **CSRF Testing**: Try submitting forms without CSRF tokens
2. **SQL Injection**: Test with inputs like `' OR '1'='1`
3. **XSS Testing**: Test with inputs like `<script>alert('XSS')</script>`
4. **Session Testing**: Verify session timeout and cookie flags

### Automated Testing

Consider using security scanning tools:
- OWASP ZAP
- Burp Suite
- SQLMap (for SQL injection testing)
- XSStrike (for XSS testing)

## Reporting Security Issues

If you discover a security vulnerability, please email security@example.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

Do not publicly disclose security issues until they have been addressed.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

## Version History

- **v1.0** (2024-01-15): Initial security implementation
  - Session security configuration
  - CSRF protection
  - SQL injection prevention
  - XSS prevention
  - Security headers
