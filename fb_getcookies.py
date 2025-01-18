from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import sys

sys.stdout.reconfigure(encoding='utf-8')

def wait_for_load(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

try:
    # Set Chrome options
    chrome_options = Options()
    prefs = {
        "profile.default_content_setting_values.popups": 2,  # Block popups
        "profile.default_content_setting_values.notifications": 1  # 1 allows notifications, 2 blocks
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-gpu")   # Disable GPU acceleration for compatibility
    chrome_options.add_argument("window-size=375,900")  # Set mobile size
    chrome_options.add_argument("--start-maximized")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    tz_params = {'timezoneId': 'Asia/Ho_Chi_Minh'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.facebook.com/login")
    print("Vui lòng xác nhận đăng nhập, sau đó nhấn Enter ở đây để xuất cookies...")
    input()
    print(driver.get_cookies())

finally:
    driver.quit()
