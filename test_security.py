"""
Quick security implementation test
Tests basic security features to verify implementation
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all security modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.utils.xss_protection import (
            sanitize_html,
            sanitize_user_input,
            sanitize_url,
            add_security_headers
        )
        print("✓ XSS protection utilities imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import XSS protection: {e}")
        return False
    
    try:
        from app.utils.sql_security import safe_execute_query
        print("✓ SQL security utilities imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SQL security: {e}")
        return False
    
    try:
        from app.utils.validators import (
            validate_email,
            validate_password,
            validate_amount,
            sanitize_sql_input,
            validate_alphanumeric
        )
        print("✓ Validators imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import validators: {e}")
        return False
    
    return True


def test_xss_sanitization():
    """Test XSS sanitization functions"""
    print("\nTesting XSS sanitization...")
    
    from app.utils.xss_protection import sanitize_html, sanitize_user_input, sanitize_url
    
    # Test HTML sanitization
    malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
    sanitized = sanitize_html(malicious_html)
    if '<script>' not in sanitized:
        print("✓ Script tags removed from HTML")
    else:
        print("✗ Script tags not removed")
        return False
    
    # Test user input sanitization
    user_input = '<img src=x onerror=alert("XSS")>'
    sanitized = sanitize_user_input(user_input)
    if '&lt;' in sanitized and '&gt;' in sanitized:
        print("✓ User input properly escaped")
    else:
        print("✗ User input not escaped")
        return False
    
    # Test URL sanitization
    safe_url = 'https://example.com/page'
    dangerous_url = 'javascript:alert("XSS")'
    
    if sanitize_url(safe_url) == safe_url:
        print("✓ Safe URL passed through")
    else:
        print("✗ Safe URL blocked")
        return False
    
    if sanitize_url(dangerous_url) == '':
        print("✓ Dangerous URL blocked")
    else:
        print("✗ Dangerous URL not blocked")
        return False
    
    return True


def test_sql_sanitization():
    """Test SQL injection prevention"""
    print("\nTesting SQL sanitization...")
    
    from app.utils.validators import sanitize_sql_input
    
    # Test SQL comment removal
    malicious_input = "admin'--"
    sanitized = sanitize_sql_input(malicious_input)
    if '--' not in sanitized:
        print("✓ SQL comments removed")
    else:
        print("✗ SQL comments not removed")
        return False
    
    # Test semicolon removal
    malicious_input = "'; DROP TABLE users;"
    sanitized = sanitize_sql_input(malicious_input)
    if ';' not in sanitized:
        print("✓ Semicolons removed")
    else:
        print("✗ Semicolons not removed")
        return False
    
    return True


def test_validation():
    """Test input validation functions"""
    print("\nTesting input validation...")
    
    from app.utils.validators import (
        validate_email,
        validate_password,
        validate_amount,
        validate_quantity
    )
    
    # Test email validation
    valid, _ = validate_email('user@example.com')
    if valid:
        print("✓ Valid email accepted")
    else:
        print("✗ Valid email rejected")
        return False
    
    valid, _ = validate_email('invalid-email')
    if not valid:
        print("✓ Invalid email rejected")
    else:
        print("✗ Invalid email accepted")
        return False
    
    # Test password validation
    valid, _ = validate_password('StrongP@ss123')
    if valid:
        print("✓ Strong password accepted")
    else:
        print("✗ Strong password rejected")
        return False
    
    valid, _ = validate_password('weak')
    if not valid:
        print("✓ Weak password rejected")
    else:
        print("✗ Weak password accepted")
        return False
    
    # Test amount validation
    valid, _ = validate_amount(100.50)
    if valid:
        print("✓ Valid amount accepted")
    else:
        print("✗ Valid amount rejected")
        return False
    
    valid, _ = validate_amount(-10)
    if not valid:
        print("✓ Negative amount rejected")
    else:
        print("✗ Negative amount accepted")
        return False
    
    # Test quantity validation
    valid, _ = validate_quantity(100)
    if valid:
        print("✓ Valid quantity accepted")
    else:
        print("✗ Valid quantity rejected")
        return False
    
    valid, _ = validate_quantity(0)
    if not valid:
        print("✓ Zero quantity rejected")
    else:
        print("✗ Zero quantity accepted")
        return False
    
    return True


def test_config():
    """Test security configuration"""
    print("\nTesting security configuration...")
    
    from app.config import Config, ProductionConfig
    
    # Test base config
    if Config.SESSION_COOKIE_HTTPONLY:
        print("✓ HttpOnly cookies enabled")
    else:
        print("✗ HttpOnly cookies not enabled")
        return False
    
    if Config.SESSION_COOKIE_SAMESITE == 'Lax':
        print("✓ SameSite=Lax configured")
    else:
        print("✗ SameSite not configured correctly")
        return False
    
    if Config.WTF_CSRF_ENABLED:
        print("✓ CSRF protection enabled")
    else:
        print("✗ CSRF protection not enabled")
        return False
    
    # Test production config
    if ProductionConfig.SESSION_COOKIE_SECURE:
        print("✓ Secure cookies enabled in production")
    else:
        print("✗ Secure cookies not enabled in production")
        return False
    
    return True


def main():
    """Run all security tests"""
    print("=" * 60)
    print("Security Implementation Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("XSS Sanitization", test_xss_sanitization),
        ("SQL Sanitization", test_sql_sanitization),
        ("Input Validation", test_validation),
        ("Security Configuration", test_config),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All security tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
