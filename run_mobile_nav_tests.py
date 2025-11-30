#!/usr/bin/env python
"""
Simple test runner for mobile navigation tests
"""
import sys
sys.path.insert(0, '.')

from tests.test_mobile_navigation import (
    TestMobileNavigationHTML,
    TestMobileNavigationCSS,
    TestMobileNavigationJavaScript,
    TestMobileNavigationResponsiveness,
    TestMobileNavigationAccessibility
)

test_classes = [
    TestMobileNavigationHTML,
    TestMobileNavigationCSS,
    TestMobileNavigationJavaScript,
    TestMobileNavigationResponsiveness,
    TestMobileNavigationAccessibility
]

passed = 0
failed = 0

for test_class in test_classes:
    test_instance = test_class()
    methods = [m for m in dir(test_instance) if m.startswith('test_')]
    
    for method_name in methods:
        try:
            method = getattr(test_instance, method_name)
            method()
            print(f"✓ {test_class.__name__}::{method_name} PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {test_class.__name__}::{method_name} FAILED: {str(e)[:100]}")
            failed += 1

print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*60}")
