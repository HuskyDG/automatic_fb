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

cwd = os.getcwd()

import pyotp
def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

def get_fb_cookies(username, password, otp_secret = None, alt_account = 0, finally_stop = False, filename = "cookies.json"):
    try:
        # Set Chrome options
        chrome_options = Options()
        prefs = {
            "profile.default_content_setting_values.popups": 2,  # Block popups
            "profile.default_content_setting_values.notifications": 1  # 1 allows notifications, 2 blocks
        }
        chrome_options.add_experimental_option("prefs", prefs)
        #chrome_options.add_argument("--headless=new")  # Enable advanced headless mode
        chrome_options.add_argument("--disable-gpu")   # Disable GPU acceleration for compatibility
        chrome_options.add_argument("window-size=1920,1080")  # Set custom window size
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox') 
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("disable-infobars")
        
        driver = webdriver.Chrome(options=chrome_options)

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        actions = ActionChains(driver)
        
        wait = WebDriverWait(driver, 10)
        
        def find_element_when_clickable(by, selector):
            return wait.until(EC.element_to_be_clickable((by, selector)))

        driver.get("https://www.facebook.com/login")
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(0.5)

        email_input = find_element_when_clickable(By.NAME, "email")
        password_input = find_element_when_clickable(By.NAME, "pass")
        actions.move_to_element(email_input).click().perform()
        time.sleep(random.randint(3,6))
        actions.move_to_element(email_input).send_keys(username).perform()
        actions.move_to_element(password_input).click().perform()
        time.sleep(random.randint(3,6))
        actions.move_to_element(password_input).send_keys(password).perform()
        
        time.sleep(random.randint(3,6))
        button = find_element_when_clickable(By.CSS_SELECTOR, 'button[id="loginbutton"]')
        actions.move_to_element(button).click().perform()
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        #input()
        time.sleep(5)
        if driver.current_url.startswith("https://www.facebook.com/two_step_verification/"):
            url_veri = driver.current_url
            for i in range(10):
                try:
                    other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'div[role="button"]')
                    actions.move_to_element(other_veri_btn).click().perform() # Click other verification method
                    time.sleep(random.randint(5,8))
                    other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'div[id=":r5:"]')
                    actions.move_to_element(other_veri_btn).click().perform() # Click App Auth method
                    time.sleep(random.randint(5,8))
                    other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'div[class="x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xtvsq51 xi112ho x17zwfj4 x585lrc x1403ito x1fq8qgq x1ghtduv x1oktzhs"]')
                    actions.move_to_element(other_veri_btn).click().perform() # Click Continue
                    time.sleep(random.randint(5,8))
                    other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'input[type="text"]')
                    actions.move_to_element(other_veri_btn).click().perform() # Click on input code
                    time.sleep(random.randint(5,8))
                    actions.move_to_element(other_veri_btn).send_keys(generate_otp(otp_secret)).perform() # Type in code on input
                    time.sleep(random.randint(5,8))
                    other_veri_btn = find_element_when_clickable(By.CSS_SELECTOR, 'div[class="x1ja2u2z x78zum5 x2lah0s x1n2onr6 xl56j7k x6s0dn4 xozqiw3 x1q0g3np x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xtvsq51 xi112ho x17zwfj4 x585lrc x1403ito x1fq8qgq x1ghtduv x1oktzhs"]')
                    actions.move_to_element(other_veri_btn).click().perform() # Click Confirmed
                    break
                except Exception as e:
                    print(f"Try again {i}:", e)
                    driver.get(url_veri)
                    time.sleep(5)
            
        #input()
        
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
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
        find_myname = driver.find_elements(By.CSS_SELECTOR, 'h1[class^="html-h1 "]')
        myname = find_myname[-1].text
        print(myname)

        if finally_stop:
            input("Press Enter to extract the cookies")
        
        f = open(filename, "w")
        json.dump(driver.get_cookies(), f)
        f.close()

    finally:
        driver.quit()
