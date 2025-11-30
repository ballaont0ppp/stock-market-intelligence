"""
XSS (Cross-Site Scripting) Protection Utilities
Provides utilities for preventing XSS attacks
"""
import html
import re
from markupsafe import Markup, escape


def sanitize_html(text: str, allowed_tags: list = None) -> str:
    """
    Sanitize HTML content by escaping or removing dangerous tags
    
    Args:
        text: HTML text to sanitize
        allowed_tags: List of allowed HTML tags (default: None = escape all)
        
    Returns:
        Sanitized HTML string
    
    Note: Jinja2 auto-escaping is the primary defense. This is for additional sanitization.
    """
    if not text:
        return ""
    
    # If no tags are allowed, escape everything
    if allowed_tags is None:
        return html.escape(text)
    
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove event handlers (onclick, onerror, etc.)
    text = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*on\w+\s*=\s*\S+', '', text, flags=re.IGNORECASE)
    
    # Remove javascript: protocol
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Remove data: protocol (can be used for XSS)
    text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
    
    # Remove vbscript: protocol
    text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
    
    return text


def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input for display
    
    This escapes HTML entities to prevent XSS attacks.
    Use this for user-generated content that will be displayed in templates.
    
    Args:
        text: User input text
        
    Returns:
        Escaped text safe for HTML display
    """
    if not text:
        return ""
    
    # Escape HTML entities
    return html.escape(str(text))


def sanitize_url(url: str) -> str:
    """
    Sanitize URL to prevent XSS through URL injection
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL or empty string if dangerous
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    url_lower = url.lower()
    
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return ""
    
    # Only allow http, https, and relative URLs
    if not (url.startswith('http://') or url.startswith('https://') or url.startswith('/')):
        return ""
    
    return url


def create_safe_markup(text: str) -> Markup:
    """
    Create safe markup from trusted HTML
    
    WARNING: Only use this for HTML that you trust and control.
    Never use this with user-generated content.
    
    Args:
        text: Trusted HTML text
        
    Returns:
        Markup object that won't be escaped by Jinja2
    """
    return Markup(text)


# XSS Prevention Guidelines
"""
XSS PREVENTION BEST PRACTICES:

1. JINJA2 AUTO-ESCAPING (PRIMARY DEFENSE):
   - Jinja2 automatically escapes variables in templates
   - {{ user_input }} is automatically escaped
   - Never disable auto-escaping unless absolutely necessary

2. NEVER USE |safe FILTER WITH USER INPUT:
   ✗ BAD:  {{ user_comment|safe }}  # Allows XSS!
   ✓ GOOD: {{ user_comment }}       # Auto-escaped

3. SANITIZE USER INPUT:
   - Use sanitize_user_input() for additional protection
   - Validate input format before storing in database

4. CONTENT SECURITY POLICY (CSP):
   - Set CSP headers to restrict script sources
   - Prevent inline scripts and eval()

5. ESCAPE IN JAVASCRIPT CONTEXT:
   ✗ BAD:  <script>var name = "{{ user_name }}";</script>
   ✓ GOOD: <script>var name = {{ user_name|tojson }};</script>

6. VALIDATE URLS:
   - Use sanitize_url() for user-provided URLs
   - Never allow javascript: or data: protocols

7. HTTP-ONLY COOKIES:
   - Set HttpOnly flag on session cookies
   - Prevents JavaScript access to cookies

EXAMPLES OF SAFE TEMPLATES:

<!-- Auto-escaped by Jinja2 -->
<p>{{ user.full_name }}</p>
<p>{{ comment.text }}</p>

<!-- Safe JSON in JavaScript -->
<script>
    var userData = {{ user_data|tojson }};
</script>

<!-- Safe URL -->
<a href="{{ url|safe_url }}">Link</a>

<!-- Trusted HTML (admin-controlled content only) -->
{% autoescape false %}
    {{ admin_html_content }}
{% endautoescape %}

NEVER DO THIS:

<!-- Unescaped user input - VULNERABLE! -->
<p>{{ user_comment|safe }}</p>  ✗ DANGEROUS!

<!-- Direct JavaScript injection - VULNERABLE! -->
<script>
    var name = "{{ user_name }}";  ✗ DANGEROUS!
</script>

<!-- Unvalidated URL - VULNERABLE! -->
<a href="{{ user_url }}">Link</a>  ✗ DANGEROUS!
"""


def add_csp_headers(response):
    """
    Add Content Security Policy headers to response
    
    Args:
        response: Flask response object
        
    Returns:
        Response with CSP headers
    """
    # Content Security Policy
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    response.headers['Content-Security-Policy'] = csp_policy
    
    return response


def add_security_headers(response, is_production=False):
    """
    Add comprehensive security headers to response
    
    Args:
        response: Flask response object
        is_production: Whether running in production mode
        
    Returns:
        Response with security headers
    """
    # X-Content-Type-Options: Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # X-Frame-Options: Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # X-XSS-Protection: Enable browser XSS filter
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Strict-Transport-Security: Force HTTPS (production only)
    if is_production:
        # max-age=31536000 (1 year), includeSubDomains
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Referrer-Policy: Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions-Policy: Control browser features
    response.headers['Permissions-Policy'] = (
        'geolocation=(), '
        'microphone=(), '
        'camera=(), '
        'payment=(), '
        'usb=(), '
        'magnetometer=(), '
        'gyroscope=(), '
        'accelerometer=()'
    )
    
    # Content Security Policy
    response = add_csp_headers(response)
    
    return response
