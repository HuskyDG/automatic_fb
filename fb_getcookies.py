from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import random
from urllib.parse import urlparse
from fbparser import get_facebook_profile_url
import re

def hide_email(email):
    match = re.match(r'(\w)(\w+)(\w)(@.+)(\.\w+)', email)
    if match:
        return f"{match.group(1)}***{match.group(3)}{match.group(4)[0]}@***{match.group(5)}"
    return email  # Return original if it doesn't match

cwd = os.getcwd()

import pyotp
def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key.replace(" ",""))
    return totp.now()

def base_url_with_path(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc + parsed_url.path.rstrip("/")

def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        # Random delay to emulate human typing speed
        time.sleep(random.uniform(0.1, 0.25))  # Between 100ms to 250ms

def parse_cookies(cookies_text):
    """
    Parse a cookies string in the format "name1=value1;name2=value2;..."
    and return a list of dictionaries suitable for `add_cookie`.
    """
    cookies = []
    for cookie_pair in cookies_text.split(';'):
        name, value = cookie_pair.strip().split('=', 1)
        cookies.append({'name': name, 'value': value, "domain": ".facebook.com", "httpOnly": False, "path": "/", "sameSite": "Lax", "secure": False })
    return cookies

def __chrome_driver__(scoped_dir = None, headless = True, incognito = False):
    # Set up Chrome options
    chrome_options = Options()
    # Block popups and notifications
    prefs = {
        "profile.default_content_setting_values.popups": 2,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # Enable headless mode if requested
    if headless:
        chrome_options.add_argument("--headless=new")
    if incognito:
        chrome_options.add_argument("--incognito")
    # Set window size and disable GPU for consistency
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    # Stealth options to mask automation
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("disable-infobars")
    # Other useful options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=en-US")
    # (Optional) Set a common user agent string
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                 "AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/105.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    # Use a specific user data directory if provided
    if scoped_dir:
        chrome_options.add_argument(f"--user-data-dir={scoped_dir}")
        
    # Define the path to the directory containing unpacked extension directories
    extensions_dir = f"{cwd}/setup/plugins"

    # Iterate through every directory under the path and add as an unpacked extension
    for dir_name in os.listdir(extensions_dir):
        extension_path = os.path.join(extensions_dir, dir_name)
        if os.path.isdir(extension_path):  # Check if it's a directory
            chrome_options.add_argument(f"--load-extension={extension_path}")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    # Load a blank page and further modify navigator properties to mask automation flags
    driver.get("data:text/html,<html><head></head><body></body></html>")
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    return driver

def is_facebook_logged_out(cookies):
    for cookie in cookies:
        if cookie.get("name", "") == "c_user":
            return False  # User is logged in if "c_user" cookie is present
    return True  # User is logged out if "c_user" cookie is not found

def check_cookies_(cookies):
    if cookies == None:
        return None
    try:
        current_url = get_facebook_profile_url(cookies)
        _url = base_url_with_path(current_url)
        if _url == "www.facebook.com" or _url == "www.facebook.com/login" or _url.startswith("www.facebook.com/checkpoint/"):
            return None
        print("Đăng nhập thành công:", _url)
    except Exception as e:
        print(f"Error: {e}")
        return None
    return cookies


def check_cookies(filename=None):
    try:
        cookies = None
        if filename:
            with open(filename, "r", encoding='utf-8') as f:
                cookies = json.load(f)
        return check_cookies_(cookies), cookies
    except Exception as e:
        print(f"Error loading cookies from file: {e}")
        return None, cookies

def get_fb_cookies(username, password, otp_secret = None, alt_account = 0, cookies = None, incognito = False, finally_stop = False):
    if password is None or password == "":
        return None
    try:
        scoped_dir = os.getenv("SCPDIR")
        driver = __chrome_driver__(scoped_dir, False, incognito)

        actions = ActionChains(driver)
        
        wait = WebDriverWait(driver, 20)

        if type(cookies) == list:
            driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})
            driver.get("https://www.facebook.com")
            wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            driver.delete_all_cookies()
            for cookie in cookies:
                cookie.pop('expiry', None)  # Remove 'expiry' field if it exists
                driver.add_cookie(cookie)
            print("Đã khôi phục cookies")
            driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": False})

        def find_element_when_clickable(by, selector):
            return wait.until(EC.element_to_be_clickable((by, selector)))
        
        def find_element_when_clickable_in_list(elemlist):
            for btn_select in elemlist:
                try:
                    return find_element_when_clickable(btn_select[0], btn_select[1])
                    break
                except Exception:
                    continue
            return None

        driver.get("https://www.facebook.com/login")
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(0.5)

        email_input = find_element_when_clickable(By.NAME, "email")
        password_input = find_element_when_clickable(By.NAME, "pass")
        actions.move_to_element(email_input).click().perform()
        time.sleep(random.randint(5,10))
        human_typing(email_input, username)
        actions.move_to_element(password_input).click().perform()
        time.sleep(random.randint(5,10))
        human_typing(password_input, password)
        
        time.sleep(random.randint(5,10))
        button = find_element_when_clickable_in_list([
            (By.CSS_SELECTOR, 'button[id="loginbutton"]'),
            (By.CSS_SELECTOR, 'button[type="submit"]')
        ])
        actions.move_to_element(button).click().perform()
        print(f"{hide_email(username)}: Đang đăng nhập...")
        time.sleep(1)
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)

        _url = base_url_with_path(driver.current_url)
        print(_url)
        if  (_url == "www.facebook.com/two_step_verification/two_factor" or 
            _url == "www.facebook.com/auth_platform/afad"):
            print(f"{hide_email(username)}: Đang chờ Xác minh đăng nhập thủ công. Hãy phê duyệt từ thiết bị khác trong vòng 20 giây...")
            for i in range(20):
                _url = base_url_with_path(driver.current_url)
                if  (_url == "www.facebook.com/two_step_verification/two_factor" or 
                    _url == "www.facebook.com/auth_platform/afad"):
                    time.sleep(1)
                else:
                    break
        _url = base_url_with_path(driver.current_url)
        if  (_url == "www.facebook.com/two_step_verification/two_factor" or 
            _url == "www.facebook.com/auth_platform/afad"):
            try:
                print(f"{hide_email(username)}: Chưa phê duyệt đang nhập. Đang tiến hành Xác minh đăng nhập 2 bước tự động với OTP")
                other_veri_btn = find_element_when_clickable_in_list([
                    (By.XPATH, '//span[contains(text(), "Thử cách khác")]'),
                    (By.XPATH, '//span[contains(text(), "Try another way")]')
                    ])
                print(f"{hide_email(username)}: Nhấn thay đổi phương thức xác thực")
                actions.move_to_element(other_veri_btn).click().perform() # Click other verification method
                time.sleep(random.randint(5,8))
                other_veri_btn = find_element_when_clickable_in_list([
                    (By.XPATH, '//div[contains(text(), "Ứng dụng xác thực")]'),
                    (By.XPATH, '//div[contains(text(), "Authentication app")]')
                    ])
                print(f"{hide_email(username)}: Chọn xác thực bằng mã OTP từ ứng dụng xác thực")
                actions.move_to_element(other_veri_btn).click().perform() # Click App Auth method
                time.sleep(random.randint(5,8))
                other_veri_btn = find_element_when_clickable_in_list([
                    (By.XPATH, '//span[contains(text(), "Tiếp tục")]'),
                    (By.XPATH, '//span[contains(text(), "Continue")]')
                    ])
                print(f"{hide_email(username)}: Nhấn vào nút Tiếp tục")
                actions.move_to_element(other_veri_btn).click().perform() # Click Continue
                time.sleep(random.randint(5,8))
                other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'input[type="text"]')
                actions.move_to_element(other_veri_btn).click().perform() # Click on input code
                time.sleep(random.randint(5,8))
                print(f"{hide_email(username)}: Đã nhập mã OTP")
                actions.move_to_element(other_veri_btn).send_keys(generate_otp(otp_secret)).perform() # Type in code on input
                time.sleep(random.randint(5,8))
                other_veri_btn = find_element_when_clickable_in_list([
                    (By.XPATH, '//span[contains(text(), "Tiếp tục")]'),
                    (By.XPATH, '//span[contains(text(), "Continue")]')
                    ])
                print(f"{hide_email(username)}: Nhấn xác nhận")
                actions.move_to_element(other_veri_btn).click().perform() # Click Confirmed
            except Exception as e:
                print(f"Error: {e}")

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)
        _url = base_url_with_path(driver.current_url)
        print(_url)
        if _url == "www.facebook.com/two_factor/remember_browser":
            button = find_element_when_clickable_in_list([
                (By.CSS_SELECTOR, 'div[class="x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xtvsq51 xi112ho x17zwfj4 x585lrc x1403ito x1fq8qgq x1ghtduv x1oktzhs"]')
            ])
            if button != None:
                print(f"{hide_email(username)}: Ghi nhớ trình duyệt")
                actions.move_to_element(button).click().perform()
                time.sleep(5)

        driver.get("https://www.facebook.com/profile.php")

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        if alt_account > 0:
            accounts_btn = find_element_when_clickable(By.CSS_SELECTOR, 'image[style="height:40px;width:40px"]')
            actions.move_to_element(accounts_btn).click().perform() # Click on accounts setting
            time.sleep(1)
            account_list_panel = find_element_when_clickable(By.CSS_SELECTOR, 'div[role="list"][class="html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd"]')
            account_list_btns = account_list_panel.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            if alt_account <= len(account_list_btns):
                actions.move_to_element(account_list_btns[alt_account -1]).click().perform()
                time.sleep(3)

        driver.get("https://www.facebook.com/profile.php")

        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        if finally_stop:
            input("<< Nhấn Enter để tiếp tục >>")
        cookies = driver.get_cookies()
        _url = base_url_with_path(driver.current_url)
        if _url == "www.facebook.com" or _url == "www.facebook.com/login" or _url.startswith("www.facebook.com/checkpoint/"):
            raise Exception(f"Đăng nhập thất bại [{_url}]")
        print(f"{hide_email(username)}: Đăng nhập thành công [{driver.current_url}]")
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()
        
    return cookies
