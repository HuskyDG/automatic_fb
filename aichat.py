from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import *
import os
import json
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import google.generativeai as genai
import sys
from PIL import Image
import base64
from io import BytesIO
import requests
import pytz
import threading

# Function to stop the script
def stop_script():
    print("1 hour has passed! Exiting the script.")
    sys.exit(0)

# Set the time limit (1 hour = 3600 seconds)
time_limit = 3600  # seconds

# Start the timer
timer = threading.Timer(time_limit, stop_script)

sys.stdout.reconfigure(encoding='utf-8')

chat_pass = os.getenv("PASSWORD")
genai_key = os.getenv("GENKEY")

genai.configure(api_key=genai_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def wait_for_load(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def remove_non_bmp_characters(input_string):
    return ''.join(c for c in input_string if ord(c) <= 0xFFFF)

try:
    # Set Chrome options
    chrome_options = Options()
    prefs = {
        "profile.default_content_setting_values.popups": 2,  # Block popups
        "profile.default_content_setting_values.notifications": 1  # 1 allows notifications, 2 blocks
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")  # Enable advanced headless mode
    chrome_options.add_argument("--disable-gpu")   # Disable GPU acceleration for compatibility
    chrome_options.add_argument("window-size=1920,1080")  # Set custom window size
    chrome_options.add_argument("--start-maximized")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    tz_params = {'timezoneId': 'Asia/Ho_Chi_Minh'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

    chat_tab = driver.current_window_handle
    
    driver.switch_to.new_window('tab')
    friend_tab = driver.current_window_handle
    
    driver.switch_to.window(chat_tab)
    
    wait = WebDriverWait(driver, 10)

    
    print("Đang tải dữ liệu từ cookies")
    cache_fb = json.loads(os.getenv("COOKIES"))
        
    driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})
    driver.get("https://www.facebook.com")
    driver.delete_all_cookies()
    for cookie in cache_fb:
        driver.add_cookie(cookie)
    print("Đã khôi phục cookies")
    driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": False})
    #print("Vui lòng xác nhận đăng nhập, sau đó nhấn Enter ở đây...")
    #input()
    
    
    driver.get("https://www.facebook.com/profile.php")
    wait_for_load(driver)
    
    find_myname = driver.find_elements(By.CSS_SELECTOR, 'h1[class^="html-h1 "]')
    myname = find_myname[-1].text
    
    timer.start()
    
    print(myname)
    
    level_chat = 100
    max_level_chat = 100
    
    driver.switch_to.window(chat_tab)
    driver.get("https://www.facebook.com/messages/")
    wait_for_load(driver)
    time.sleep(2)
    
    driver.switch_to.window(friend_tab)
    driver.get("https://www.facebook.com/friends")
    wait_for_load(driver)
    time.sleep(2)
    
    while True:
        try:
            driver.switch_to.window(friend_tab)
            try:
                for button in driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Xác nhận"]'):
                    print("Chấp nhận kết bạn")
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)
            except Exception:
                pass
            try:
                for button in driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Xóa"]'):
                    print("Xóa kết bạn")
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)
            except Exception:
                pass

            # Insert JavaScript to reload the page after 5 minutes (300,000 ms)
            reload_script = """
            setTimeout(function() {
                location.reload();
            }, 300000);  // 5 minutes in milliseconds
            """
            driver.execute_script(reload_script)

            driver.switch_to.window(chat_tab)
            driver.get("https://www.facebook.com/messages/")
            wait_for_load(driver)
            time.sleep(5)
            try:
                element = driver.find_element(By.CSS_SELECTOR, 'input[class="x1i10hfl x9f619 xggy1nq x1s07b3s x1kdt53j x1a2a7pz x5yr21d x17qophe xg01cxk x10l6tqk x13vifvy xh8yej3"]')
                element.click()
                time.sleep(2)
                for digit in chat_pass:
                    element.send_keys(digit)  # Send the digit to the input element
                    time.sleep(0.5)  # Wait for 0.5 seconds before sending the next digit
                time.sleep(10)
            except Exception:
                pass
            
            # find all unread single chats not group (span[class="x6s0dn4 xzolkzo x12go9s9 x1rnf11y xprq8jg x9f619 x3nfvp2 xl56j7k x1spa7qu x1kpxq89 xsmyaan"])
            chat_btns = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/messages/"]')
            for chat_btn in chat_btns:
                #print(chat_btn.text)
                try:
                    chat_btn.find_element(By.CSS_SELECTOR, 'span[class="x6s0dn4 xzolkzo x12go9s9 x1rnf11y xprq8jg x9f619 x3nfvp2 xl56j7k x1spa7qu x1kpxq89 xsmyaan"]')
                    who_chatted = chat_btn.find_element(By.CSS_SELECTOR, 'span[class="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft"]').text
                except Exception:
                    continue
                
                print("Tin nhắn mới")
                
                driver.execute_script("arguments[0].click();", chat_btn)
                time.sleep(2)

                try:
                    msg_scroller = driver.find_element(By.CSS_SELECTOR, 'div[class="x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xish69e x16o0dkt"]')
                    for _x in range(30):
                        driver.execute_script("""
    var divs = document.querySelectorAll('div.x78zum5.xdt5ytf[data-virtualized="false"]');
    divs.forEach(function(div) {
        var disabledDiv = document.createElement('disabled-div');
        disabledDiv.innerHTML = div.innerHTML;  // Keep the content inside
        div.parentNode.replaceChild(disabledDiv, div);  // Replace the div with the custom tag
    });
""")
                        driver.execute_script("""
    var divs = document.querySelectorAll('div.x78zum5.xdt5ytf[data-virtualized="true"]');
    divs.forEach(function(div) {
        var disabledDiv = document.createElement('disabled-div');
        disabledDiv.innerHTML = div.innerHTML;  // Keep the content inside
        div.parentNode.replaceChild(disabledDiv, div);  // Replace the div with the custom tag
    });
""")

                        driver.execute_script("arguments[0].scrollTop = 0;", msg_scroller)
                        time.sleep(0.1)
                except Exception:
                    pass

                try:
                    msg_table = driver.find_element(By.CSS_SELECTOR, 'div[class="x1uipg7g xu3j5b3 xol2nv xlauuyb x26u7qi x19p7ews x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x10wlt62"]')
                except Exception:
                    continue
                    
                try:
                    msg_elements = msg_table.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
                except Exception:
                    continue

                # Get current date and time
                current_datetime = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

                # Format the output
                day_and_time = current_datetime.strftime("%A, %d %B %Y - %H:%M:%S")

                prompt = f"""

Currently, it is {day_and_time}. I am creating a message response model and using your reply as a response. 

Imagine you are me: {myname}
- You are male, born on 17/01/2000, Capricorn, from Hanoi, and currently living in Ho Chi Minh City.
- You graduated from Industrial University of Ho Chi Minh City (IUH) and work as an IT engineer. 
- You're usually free in the evenings. 
- You love morning coffee, listening to Calum Scott's music, traveling, watching the sea, and enjoying the cold air in Da Lat and the beaches of Phan Thiet. 
- You're single and looking for someone to talk to. Your phone number is 0339876543. 

Note: 
- Using your creativity, please reply to the following conversation naturally, as if you were a real person. 
- You can respond in Vietnamese or English depending on the content of the chat and the person you are talking to. 
- You can speak English if the name of the person you are talking to is not Vietnamese. 
- Keep your responses concise if possible and avoid repetitive or mechanical replies. 
- Respond as naturally and human-like as possible.
- Respond to the point, especially the last message
- Do not explain or add any details beyond the message in your content
- You can introduce yourself when getting to know each other.
- To make the conversation less boring, you can ask the other person some interesting questions.
- IMPORTANT! The content you create for me is the content of the reply message.

The Messenger conversation with "{who_chatted}" is as follows:

"""

                for msg_element in msg_elements[-level_chat:]:
                    try:
                        timedate = msg_element.find_element(By.CSS_SELECTOR, 'span[class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1pg5gke xvq8zen xo1l8bm x12scifz"]')
                        prompt += "\n--- " + timedate.text + " ---"
                    except NoSuchElementException:
                        pass
                        
                    # Finding name
                    try: 
                        msg_element.find_element(By.CSS_SELECTOR, 'div[class="html-div xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a xyk4ms5"]').text
                        name = "Tin nhắn của bạn"
                    except NoSuchElementException:
                        name = None

                    if name == None:
                        try: 
                            name = "- " + msg_element.find_element(By.CSS_SELECTOR, 'h4').text
                        except NoSuchElementException:
                            name = None
                    if name == None:
                        try: 
                            name = "- " + msg_element.find_element(By.CSS_SELECTOR, 'span[class="html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs xzpqnlu x1hyvwdk xjm9jq1 x6ikm8r x10wlt62 x10l6tqk x1i1rx1s"]').text
                        except NoSuchElementException:
                            name = None
                    
                    msg = None
                    try:
                        msg = msg_element.find_element(By.CSS_SELECTOR, 'div[dir="auto"][class^="html-div "]').text
                    except NoSuchElementException:
                        pass
                    
                    try:
                        image_element = msg_element.find_element(By.CSS_SELECTOR, 'img[class="xz74otr xmz0i5r x193iq5w"]')
                        data_uri = image_element.get_attribute("src")
                        
                        if data_uri.startswith("data:image/jpeg;base64,"):
                            # Extract the base64 string (remove the prefix)
                            base64_str = data_uri.split(",")[1]

                            # Decode the base64 string into binary data
                            image_data = base64.b64decode(base64_str)

                        else:
                            image_data = requests.get(data_uri).content

                        # Use BytesIO to create a file-like object for the image
                        image_file = BytesIO(image_data)
                        # Open the image with PIL
                        image = Image.open(image_file)
                        
                        img_detail = model.generate_content(["Mô tả bức ảnh", image])
                        
                        msg = f"<Đã gửi 1 bức ảnh: {img_detail.text}>"
                    except Exception:
                        pass
                    
                    if msg == None:
                        continue
                    if name == None:
                        info_msg = "  " + msg
                    else:
                        info_msg = name + ": " + msg
                    prompt += "\n" + info_msg

                for _x in range(10):
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, 'p[class="xat24cr xdj266r"]')
                        button.send_keys(" ")
                        caption=model.generate_content(prompt).text
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                        button.send_keys(remove_non_bmp_characters(caption + "\n"))
                        
                        print(prompt)
                        print("AI Trả lời:", caption)
                        time.sleep(2)

                        break
                    except Exception as e:
                        print("Thử lại:", _x + 1)
                        print(e)
                        time.sleep(2)
                        continue
                
                print(prompt)
                print("AI Trả lời:", caption)
                time.sleep(2)
                
                if level_chat < max_level_chat:
                    level_chat += 1
            
        except Exception as e:
            print(e)
        

finally:
    driver.quit()
    
