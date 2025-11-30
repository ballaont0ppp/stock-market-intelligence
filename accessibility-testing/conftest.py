"""
Pytest configuration and fixtures for accessibility testing
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config
import time


@pytest.fixture(scope='session')
def driver():
    """Create a WebDriver instance for the test session"""
    if config.BROWSER.lower() == 'chrome':
        options = ChromeOptions()
        if config.HEADLESS_MODE:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}')
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    
    elif config.BROWSER.lower() == 'firefox':
        options = FirefoxOptions()
        if config.HEADLESS_MODE:
            options.add_argument('--headless')
        options.add_argument(f'--width={config.WINDOW_WIDTH}')
        options.add_argument(f'--height={config.WINDOW_HEIGHT}')
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
    
    else:
        raise ValueError(f"Unsupported browser: {config.BROWSER}")
    
    driver.implicitly_wait(config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope='session')
def authenticated_driver(driver):
    """Create an authenticated WebDriver session"""
    # Navigate to login page
    driver.get(f"{config.APP_URL}/auth/login")
    time.sleep(2)
    
    try:
        # Fill in login form
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        
        email_input.send_keys(config.TEST_USER_EMAIL)
        password_input.send_keys(config.TEST_USER_PASSWORD)
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains('/dashboard')
        )
        
        print("Successfully authenticated test user")
    except Exception as e:
        print(f"Warning: Could not authenticate test user: {e}")
        print("Some tests requiring authentication may fail")
    
    return driver


@pytest.fixture(scope='function')
def screenshot_on_failure(request, driver):
    """Take screenshot on test failure"""
    yield
    
    if request.node.rep_call.failed and config.SCREENSHOT_ON_FAILURE:
        test_name = request.node.name
        screenshot_path = config.SCREENSHOTS_DIR / f"{test_name}_failure.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for screenshot fixture"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope='session')
def admin_driver(driver):
    """Create an authenticated admin WebDriver session"""
    # Navigate to login page
    driver.get(f"{config.APP_URL}/auth/login")
    time.sleep(2)
    
    try:
        # Fill in login form with admin credentials
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        
        email_input.clear()
        email_input.send_keys(config.ADMIN_EMAIL)
        password_input.clear()
        password_input.send_keys(config.ADMIN_PASSWORD)
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect
        time.sleep(3)
        
        print("Successfully authenticated admin user")
    except Exception as e:
        print(f"Warning: Could not authenticate admin user: {e}")
    
    return driver


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "visual: mark test as visual accessibility test"
    )
    config.addinivalue_line(
        "markers", "motor: mark test as motor accessibility test"
    )
    config.addinivalue_line(
        "markers", "cognitive: mark test as cognitive accessibility test"
    )
    config.addinivalue_line(
        "markers", "wcag_a: mark test as WCAG Level A compliance test"
    )
    config.addinivalue_line(
        "markers", "wcag_aa: mark test as WCAG Level AA compliance test"
    )
    config.addinivalue_line(
        "markers", "wcag_aaa: mark test as WCAG Level AAA compliance test"
    )
