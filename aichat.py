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
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8')

genai_key = os.getenv("GENKEY")

ai_prompt = os.getenv("AI_PROMPT")

if ai_prompt == None or ai_prompt == "":
    ai_prompt = """
- I am a Vietnamese people, Capricorn male, born on January 17, 2000. Originally from Hanoi, I now reside in vibrant Ho Chi Minh City. A proud graduate of the Industrial University of Ho Chi Minh City (IUH), I currently work as an IT engineer, with evenings generally free to explore my personal interests.
- I am passionate about savoring morning coffee, listening to Calum Scott’s heartfelt music, traveling, and immersing myself in the beauty of the sea. I particularly enjoy the cool weather of Da Lat and the serene beaches of Phan Thiet.
- While I am single and open to finding a meaningful relationship, my work commitments often keep me busy, leaving limited time to focus on love for now.
- In addition to my professional work, I am also developing a personal AI project, which you can find on my GitHub: https://github.com/HuskyDG/automatic_fb.
- Feel free to reach out to me at:
  Phone: 0339876543
  Email: shiweinguyen@gmail.com
"""

cwd = os.getcwd()
print(cwd)

genai.configure(api_key=genai_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def escape_string(input_string):
    """
    Escapes special characters in a string, including replacing newlines with \\n.
    :param input_string: The string to be escaped.
    :return: The escaped string.
    """
    escaped_string = input_string.replace("\\", "\\\\")  # Escape backslashes
    escaped_string = escaped_string.replace("\n", "\\n")  # Escape newlines
    escaped_string = escaped_string.replace("\t", "\\t")  # Escape tabs (optional)
    escaped_string = escaped_string.replace("\"", "\\\"")  # Escape double quotes
    escaped_string = escaped_string.replace("\'", "\\\'")  # Escape single quotes
    return escaped_string

emoji_to_shortcut = [
    {"emoji": "👍", "shortcut": "(y)"},
    {"emoji": "😇", "shortcut": "O:)"},
    {"emoji": "😈", "shortcut": "3:)"},
    {"emoji": "❤️", "shortcut": "<3"},
    {"emoji": "😞", "shortcut": ":("},
    {"emoji": "☹️", "shortcut": ":["},
    {"emoji": "😊", "shortcut": "^_^"},
    {"emoji": "😕", "shortcut": "o.O"},
    {"emoji": "😲", "shortcut": ":O"},
    {"emoji": "😘", "shortcut": ":*"},
    {"emoji": "😢", "shortcut": ":'("},
    {"emoji": "😎", "shortcut": "8-)"},
    {"emoji": "😆", "shortcut": ":v"},
    {"emoji": "😸", "shortcut": ":3"},
    {"emoji": "😁", "shortcut": ":-D"},
    {"emoji": "🐧", "shortcut": "<(\")"},
    {"emoji": "😠", "shortcut": ">:("},
    {"emoji": "😜", "shortcut": ":P"},
    {"emoji": "😮", "shortcut": ">:O"},
    {"emoji": "😕", "shortcut": ":/"},
    {"emoji": "🤖", "shortcut": ":|]"},
    {"emoji": "🦈", "shortcut": "(^^^)"},
    {"emoji": "😑", "shortcut": "-_-"},
    {"emoji": "💩", "shortcut": ":poop:"},
    {"emoji": "😭", "shortcut": "T_T"},
]

# Create a dictionary for quick lookup
emoji_dict = {item["emoji"]: item["shortcut"] for item in emoji_to_shortcut}

def replace_emoji_with_shortcut(text):
    # Use regex to find all emojis and replace them
    for emoji, shortcut in emoji_dict.items():
        text = text.replace(emoji, shortcut)
    return text

def wait_for_load(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def remove_non_bmp_characters(input_string):
    return ''.join(c for c in input_string if ord(c) <= 0xFFFF)
    
def inject_reload(driver):
    # Insert JavaScript to reload the page after 5 minutes (300,000 ms)
    reload_script = """
            if (typeof window.reloadScheduled === 'undefined') {
                window.reloadScheduled = true;
                setTimeout(function() {
                    location.reload();
                }, 300000);  // 5 minutes in milliseconds
            }
    """
    driver.execute_script(reload_script)

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
    chrome_options.add_argument(f"window-size={1920*2},{1080*2}")  # Set custom window size
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox') 
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--force-device-scale-factor=0.25")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    actions = ActionChains(driver)

    tz_params = {'timezoneId': 'Asia/Ho_Chi_Minh'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

    chat_tab = driver.current_window_handle
    
    driver.switch_to.new_window('tab')
    friend_tab = driver.current_window_handle

    driver.switch_to.new_window('tab')
    profile_tab = driver.current_window_handle
    
    driver.switch_to.window(chat_tab)
    
    wait = WebDriverWait(driver, 10)
    
    print("Đang tải dữ liệu từ cookies")
    
    try:
        f = open("cookies.json", "r")
        cache_fb = json.load(f)
    except Exception:
        cache_fb = json.loads(os.getenv("COOKIES")) #legacy
    
    onetimecode = os.getenv("ONETIMECODE")
    if onetimecode == None or onetimecode == "":
        try:
            f = open("one-time-code.txt", "r")
            onetimecode = f.read()
        except Exception as e:
            onetimecode = ""
            print(e)

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
    
    print(myname)
    
    driver.switch_to.window(chat_tab)
    driver.get("https://www.facebook.com/messages/t/156025504001094")
    wait_for_load(driver)
    time.sleep(2)
    
    driver.switch_to.window(friend_tab)
    driver.get("https://www.facebook.com/friends")
    wait_for_load(driver)
    time.sleep(2)
    
    while True:
        try:
            with open("exitnow.txt", "r") as file:
                content = file.read().strip()  # Read and strip any whitespace/newline
                if content == "1":
                    break
        except Exception:
            pass # Ignore all errors

        try:
            new_chat_coming = False
            time.sleep(0.5)
            driver.switch_to.window(friend_tab)
            inject_reload(driver)

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

            driver.switch_to.window(chat_tab)
            inject_reload(driver)
            try:
                otc_input = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="one-time-code"]')
                driver.execute_script("arguments[0].setAttribute('class', '');", otc_input)
                print("Giải mã đoạn chat được mã hóa...")
                actions.move_to_element(otc_input).click().perform()
                time.sleep(2)
                for digit in onetimecode:
                    actions.move_to_element(otc_input).send_keys(digit).perform()  # Send the digit to the input element
                    time.sleep(1)  # Wait for 1s before sending the next digit
                continue
            except Exception:
                pass

            # find all unread single chats not group (span[class="x6s0dn4 xzolkzo x12go9s9 x1rnf11y xprq8jg x9f619 x3nfvp2 xl56j7k x1spa7qu x1kpxq89 xsmyaan"])
            chat_btns = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/messages/"]')
            for chat_btn in chat_btns:
                #print(chat_btn.text)
                try:
                    chat_btn.find_element(By.CSS_SELECTOR, 'span[class="x6s0dn4 xzolkzo x12go9s9 x1rnf11y xprq8jg x9f619 x3nfvp2 xl56j7k x1spa7qu x1kpxq89 xsmyaan"]')
                except Exception:
                    continue

                new_chat_coming = True
                
                driver.execute_script("arguments[0].click();", chat_btn)
                time.sleep(2)
                
                try:
                    profile_btn = driver.find_element(By.CSS_SELECTOR, 'a[class="x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1rg5ohu x1a2a7pz xs83m0k"]')
                    profile_link = urljoin(driver.current_url, profile_btn.get_attribute("href"))
                    
                    driver.switch_to.window(profile_tab)
                    driver.get(profile_link)
                    
                    wait_for_load(driver)
    
                    find_who_chatted = driver.find_elements(By.CSS_SELECTOR, 'h1[class^="html-h1 "]')
                    who_chatted = find_who_chatted[-1].text
                except Exception:
                    continue
                
                driver.switch_to.window(chat_tab)
                print("Tin nhắn mới với " + who_chatted)

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

                js_code = """
                    const targetDivs = document.querySelectorAll('div[dir="auto"][class^="html-div "]');

                    targetDivs.forEach(div => {
                      // Replace img elements
                      const imgs = div.querySelectorAll('img[height="16"][width="16"]');
                      imgs.forEach(img => {
                        const span = document.createElement('span');
                        span.textContent = img.alt || 'No alt content';
                        img.replaceWith(span);
                      });

                      // Update span elements with a specific class
                      const spans = div.querySelectorAll('span[class="html-span xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs x3nfvp2 x1j61x8r x1fcty0u xdj266r xat24cr xgzva0m xhhsvwb xxymvpz xlup9mm x1kky2od"]');
                      spans.forEach(span => {
                        span.setAttribute('class', '');
                      });
                    });
                """

                # Execute the JavaScript code
                driver.execute_script(js_code)

                # Get current date and time
                current_datetime = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

                # Format the output
                day_and_time = current_datetime.strftime("%A, %d %B %Y - %H:%M:%S")

                header_prompt = f"""
I am creating a chat bot / message response model and using your reply as a response. 

Imagine you are me: {myname}
{ai_prompt}

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


Currently, it is {day_and_time}, you receives a message from "{who_chatted}". The Messenger conversation with "{who_chatted}" is as json here:

"""
                prompt = "["

                for msg_element in msg_elements:
                    try:
                        timedate = msg_element.find_element(By.CSS_SELECTOR, 'span[class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1pg5gke xvq8zen xo1l8bm x12scifz"]')
                        prompt += "\n{\"conversation_event\" : \"" + timedate.text + "\"},"
                    except Exception:
                        pass
                        
                    # Finding name
                    try: 
                        msg_element.find_element(By.CSS_SELECTOR, 'div[class="html-div xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a xyk4ms5"]').text
                        name = "Your message"
                    except Exception:
                        name = None

                    if name == None:
                        try: 
                            name = msg_element.find_element(By.CSS_SELECTOR, 'h4').text
                            name =  f"{who_chatted} ({name})"
                        except Exception:
                            name = None
                    if name == None:
                        try: 
                            name = msg_element.find_element(By.CSS_SELECTOR, 'span[class="html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs xzpqnlu x1hyvwdk xjm9jq1 x6ikm8r x10wlt62 x10l6tqk x1i1rx1s"]').text
                            name =  f"{who_chatted} ({name})"
                        except Exception:
                            name = None
                    
                    msg = None
                    try:
                        msg = msg_element.find_element(By.CSS_SELECTOR, 'div[dir="auto"][class^="html-div "]').text
                    except Exception:
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
                        
                        img_detail = model.generate_content(["Photo description", image])
                       
                        prompt += "\n{\"conversation_image_info\": \"" + escape_string(name) + " send an image: " + escape_string(img_detail.text) + "\"},"
                    except Exception:
                        pass

                    try: 
                        react_elements = msg_element.find_elements(By.CSS_SELECTOR, 'img[height="32"][width="32"]')
                        emojis = ""
                        if msg == None and len(react_elements) > 0:
                            for react_element in react_elements:
                                emojis += react_element.get_attribute("alt")
                            msg = emojis
                    except Exception:
                        pass

                    if msg == None:
                        try:
                            msg_element.find_element(By.CSS_SELECTOR, 'div[aria-label="Like, thumbs up"]')
                            msg = "👍"
                        except Exception:
                            msg = None

                    if msg == None:
                        continue
                    if name == None:
                        name = "None"
                    prompt += "\n{\"conversation_message\": {\"" + escape_string(name) + "\" : \"" + escape_string(msg) + "\"}},"

                    try: 
                        react_elements = msg_element.find_elements(By.CSS_SELECTOR, 'img[height="16"][width="16"]')
                        emojis = ""
                        if len(react_elements) > 0:
                            for react_element in react_elements:
                                emojis += react_element.get_attribute("alt")
                            emoji_info = f"The above message was reacted with following emojis: {emojis}"
                            
                            prompt += "\n{\"conversation_reactions\" : \"" + escape_string(emoji_info) + "\"},"
                            
                    except Exception:
                        pass

                prompt = prompt[:-1]
                prompt += "\n]"
                for _x in range(10):
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, 'p[class="xat24cr xdj266r"]')
                        button.send_keys(" ")
                        caption=model.generate_content(header_prompt + prompt + "\n\n>> TYPE YOUR MESSAGE TO REPLY").text
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                        button.send_keys(remove_non_bmp_characters(replace_emoji_with_shortcut(caption) + "\n"))
                        
                        print(prompt)
                        print("AI Trả lời:", caption)
                        time.sleep(2)

                        break
                    except Exception as e:
                        print("Thử lại:", _x + 1)
                        print(e)
                        time.sleep(2)
                        continue
                
            if new_chat_coming:
                driver.get("https://www.facebook.com/messages/t/156025504001094")
        except Exception as e:
            print(e)

finally:
    driver.quit()
    
