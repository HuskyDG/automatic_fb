import os  # For environment variable handling
import json  # For handling JSON data
import time  # For time-related functions
import sys  # For system-specific parameters and functions
import copy # For deepcopy
from datetime import datetime  # For date and time manipulation
import pytz  # For timezone handling
from io import BytesIO  # For handling byte streams
import requests  # For making HTTP requests
from urllib.parse import urljoin, urlparse  # For URL manipulation
from hashlib import md5  # For hashing
from selenium import webdriver  # For web automation
from selenium.webdriver.common.by import By  # For locating elements
from selenium.webdriver.chrome.service import Service  # For Chrome service
from selenium.webdriver.common.action_chains import ActionChains  # For simulating user actions
from selenium.webdriver.support.ui import WebDriverWait  # For waiting for elements
from selenium.webdriver.support import expected_conditions as EC  # For expected conditions
from selenium.common.exceptions import *  # For handling exceptions
from selenium.webdriver.common.keys import Keys  # For keyboard actions
import google.generativeai as genai  # For generative AI functionalities
from pickle_utils import *  # For pickling data
from github_utils import *  # For GitHub file operations
from fb_getcookies import __chrome_driver__, is_facebook_logged_out, base_url_with_path  # For Facebook cookie handling
from aichat_utils import *  # For custom utility functions

sys.stdout.reconfigure(encoding='utf-8')

genai_key = os.getenv("GENKEY")
scoped_dir = os.getenv("SCPDIR")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Pass GitHub Token
GITHUB_REPO = os.getenv("GITHUB_REPO")   # Pass the repository (owner/repo)
STORAGE_BRANCE = os.getenv("STORAGE_BRANCE")
PASSWORD = os.getenv("PASSWORD", "")
encrypt_key = generate_fernet_key(PASSWORD)

if_running_on_github_workflows = (GITHUB_TOKEN is not None and GITHUB_TOKEN != "")

f_intro_txt = "setup/introduction.txt"
f_rules_txt = "setup/rules.txt"

with open(f_intro_txt, "r", encoding='utf-8') as f: # What kind of person will AI simulate?
    ai_prompt = f.read()

try:
    with open(f_rules_txt, "r", encoding='utf-8') as f: # How AI Responds
        rules_prompt = f.read()
except Exception:
    rules_prompt = """
- Reply naturally and creatively, as if you were a real person.
- Reply in Vietnamese or English depending on the conversation and the name of the person you are replying to. If the person you are replying to is not Vietnamese people, you can reply in English, or in their language.
- Do not switch languages ​​during a conversation unless the other person asks you to. Meaning: If the person you are talking to speaks Vietnamese, please only reply in Vietnamese. If the person you are talking to speaks English, please only reply in English.
- Do not switch languages ​​during a conversation unless requested by the other person.
- If you are speaking in Vietnamese, make sure to use appropriate pronouns when knowing the other person's age.
- Reply to communication messages briefly, unless the context requires detailed information, clarification, or a more personal and thoughtful response.
- Keep responses concise, relevant, and avoid repetition or robotic tone.
- Stay focused on the last message in the conversation.
- Avoid unnecessary explanations or details beyond the reply itself.
- Feel free to introduce yourself when meeting someone new.
- Make the chat engaging by asking interesting questions.
- Provide only the response content without introductory phrases or multiple options.
"""

cwd = os.getcwd()
print(cwd)

try:
    # Initialize the driver
    driver = __chrome_driver__(scoped_dir, False)
    actions = ActionChains(driver)

    tz_params = {'timezoneId': 'Asia/Ho_Chi_Minh'}
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

    chat_tab = driver.current_window_handle
    
    driver.switch_to.new_window('tab')
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    friend_tab = driver.current_window_handle

    driver.switch_to.new_window('tab')
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    profile_tab = driver.current_window_handle
 
    driver.switch_to.new_window('tab')
    driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)
    switch_to_mobile_view(driver)
    worker_tab = driver.current_window_handle
    
    driver.switch_to.window(chat_tab)
    
    wait = WebDriverWait(driver, 10)
    
    print("Đang tải dữ liệu từ cookies")
    
    try:
        with open("cookies.json", "r") as f:
            cache_fb = json.load(f)
    except Exception:
        cache_fb = []    
    try:
        with open("cookies_bak.json", "r") as f:
            bak_cache_fb = json.load(f)
    except Exception:
        bak_cache_fb = None

    try:
        with open("logininfo.json", "r") as f:
            login_info = json.load(f)
            onetimecode = login_info.get("onetimecode", "")
            work_jobs = parse_opts_string(login_info.get("work_jobs", "aichat,friends"))
    except Exception as e:
        onetimecode = ""
        work_jobs = parse_opts_string("aichat,friends")
        print(e)

    print("Danh sách jobs:", work_jobs)

    driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})
    driver.get("https://www.facebook.com")
    driver.delete_all_cookies()
    for cookie in cache_fb:
        cookie.pop('expiry', None)  # Remove 'expiry' field if it exists
        driver.add_cookie(cookie)
    print("Đã khôi phục cookies")
    driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": False})
    #print("Vui lòng xác nhận đăng nhập, sau đó nhấn Enter ở đây...")
    #input()
    print("Đang đọc thông tin cá nhân...")
    driver.get("https://www.facebook.com/profile.php")
    wait_for_load(driver)
    
    find_myname = driver.find_elements(By.CSS_SELECTOR, 'h1[class^="html-h1 "]')
    myname = find_myname[-1].text

    f_self_facebook_info = "self_facebook_info.bin"
    f_chat_history = "chat_histories.bin"
    if if_running_on_github_workflows:
        try:
            get_file(GITHUB_TOKEN, GITHUB_REPO, f_self_facebook_info, STORAGE_BRANCE, f_self_facebook_info)
        except Exception as e:
            print(e)
        try:
            # Get chat_histories
            get_file(GITHUB_TOKEN, GITHUB_REPO, f_chat_history + ".enc", STORAGE_BRANCE, f_chat_history + ".enc")
            decrypt_file(f_chat_history + ".enc", f_chat_history, encrypt_key)
        except Exception as e:
            print(e)

    chat_histories = pickle_from_file(f_chat_history, {})

    self_facebook_info = pickle_from_file(f_self_facebook_info, { "Facebook name" : myname, "Facebook url" :  driver.current_url })
    
    sk_list = [
            "?sk=about_work_and_education", 
            "?sk=about_places", 
            "?sk=about_contact_and_basic_info", 
            "?sk=about_family_and_relationships", 
            "?sk=about_details"
        ]
    
    if self_facebook_info.get("Last access", 0) == 0:
        self_facebook_info["Last access"] = int(time.time())
        # Loop through the profile sections
        for sk in sk_list:
            # Build the full URL for the profile section
            info_url = urljoin("https://www.facebook.com/profile.php", sk)
            driver.get(info_url)

            # Wait for the page to load
            wait_for_load(driver)

            # Find the info elements
            info_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class="xyamay9 xqmdsaz x1gan7if x1swvt13"] > div')

            # Loop through each info element
            for info_element in info_elements:
                title = find_and_get_text(info_element, By.CSS_SELECTOR, 'div[class="xieb3on x1gslohp"]')
                if title is not None:
                    detail = []

                    # Append the text lists to the detail array
                    detail.extend(find_and_get_list_text(info_element, By.CSS_SELECTOR, 'div[class="x1hq5gj4"]'))
                    detail.extend(find_and_get_list_text(info_element, By.CSS_SELECTOR, 'div[class="xat24cr"]'))

                    # Add title and details to the facebook_info dictionary
                    self_facebook_info[title] = detail
        pickle_to_file(f_self_facebook_info, self_facebook_info)
        if if_running_on_github_workflows:
            upload_file(GITHUB_TOKEN, GITHUB_REPO, f_self_facebook_info, STORAGE_BRANCE)

    gemini_dev_mode = work_jobs.get("aichat", "normal") == "devmode"
    instruction = get_instructions_prompt(myname, ai_prompt, self_facebook_info, rules_prompt, gemini_dev_mode)
    # Setup persona instruction
    genai.configure(api_key=genai_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction = instruction
    )
    for text in instruction:
        print(text)
    
    def init_fb():
        driver.switch_to.window(chat_tab)
        driver.get("https://www.facebook.com/messages/new")
        driver.switch_to.window(friend_tab)
        driver.get("https://www.facebook.com/friends")
        driver.switch_to.window(worker_tab)
        driver.get("https://www.facebook.com/home.php")

    f_facebook_infos = "facebook_infos.bin"
    try:
        if if_running_on_github_workflows:
            get_file(GITHUB_TOKEN, GITHUB_REPO, f_facebook_infos, STORAGE_BRANCE, f_facebook_infos)
    except Exception as e:
        print(e)
    facebook_infos = pickle_from_file(f_facebook_infos, {})

    print("Bắt đầu khởi động!")

    while True:
        try:
            if is_facebook_logged_out(driver.get_cookies()):
                if bak_cache_fb is not None:
                    print("Tài khoản bị đăng xuất, sử dụng cookies dự phòng")
                    # TODO: obtain new cookies
                    driver.delete_all_cookies()
                    for cookie in bak_cache_fb:
                        cookie.pop('expiry', None)  # Remove 'expiry' field if it exists
                        driver.add_cookie(cookie)
                    bak_cache_fb = None
                    init_fb()
                    time.sleep(1)
                    continue
                else:
                    print("Tài khoản bị đăng xuất")
                    break
            with open("exitnow.txt", "r") as file:
                content = file.read().strip()  # Read and strip any whitespace/newline
                if content == "1":
                    break
        except Exception:
            pass # Ignore all errors

        try:
            time.sleep(0.5)
            if "friends" in work_jobs:
                driver.switch_to.window(friend_tab)
                if base_url_with_path(driver.current_url) != "www.facebook.com/friends":
                    driver.get("https://www.facebook.com/friends")
                inject_reload(driver)

                try:
                    for button in driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Xác nhận"]'):
                        print("Chấp nhận kết bạn")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                except Exception:
                    pass
                try:
                    for button in driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Xóa"]'):
                        print("Xóa kết bạn")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                except Exception:
                    pass

            if "autolike" in work_jobs or "keeponline" in work_jobs:
                driver.switch_to.window(worker_tab)
            
            if "autolike" in work_jobs:
                inject_reload(driver, 30*60*1000)
                driver.execute_script("""
                    if (typeof window.executeLikes === 'undefined') {
                        window.executeLikes = true;
                        (async function randomClickDivs() {
                            // Find all divs with the specific aria-label
                            const divs = Array.from(document.querySelectorAll('div[aria-label*="like, double tap and hold for more reactions"]')).concat(Array.from(document.querySelectorAll('div[role="button"] > div[style="color:#1877f2;"]')));
                            if (divs.length === 0) {
                                console.log('No matching divs found.');
                                return;
                            }
                            console.log(`Found ${divs.length} matching divs.`);

                            // Shuffle the array to randomize the order
                            const shuffledDivs = divs.sort(() => 0.5 - Math.random());

                            // Select the first 5 divs from the shuffled array
                            const selectedDivs = shuffledDivs.slice(0, 5);

                            // Click each div with a 10-second delay
                            for (let i = 0; i < selectedDivs.length; i++) {
                                console.log(`Clicking div ${i + 1} of 5...`);
                                selectedDivs[i].click();

                                // Wait for 10 seconds before the next click
                                await new Promise(resolve => setTimeout(resolve, 10000));
                            }
                        })();
                    }
                """)
            elif "keeponline" in work_jobs:
                inject_reload(driver)

            if "aichat" in work_jobs:
                driver.switch_to.window(chat_tab)
                if base_url_with_path(driver.current_url) != "www.facebook.com/messages/new":
                    driver.get("https://www.facebook.com/messages/new")
                inject_reload(driver)
                try:
                    if len(onetimecode) >= 6:
                        otc_input = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="one-time-code"]')
                        driver.execute_script("arguments[0].setAttribute('class', '');", otc_input)
                        print("Giải mã đoạn chat được mã hóa...")
                        actions.move_to_element(otc_input).click().perform()
                        time.sleep(2)
                        for digit in onetimecode:
                            actions.move_to_element(otc_input).send_keys(digit).perform()  # Send the digit to the input element
                            time.sleep(1)  # Wait for 1s before sending the next digit
                        print("Hoàn tất giải mã!")
                        time.sleep(5)
                        continue
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, '*[class="__fb-light-mode x1n2onr6 x1vjfegm"]')
                        # Inject style to hide the element
                        driver.execute_script("arguments[0].style.display = 'none';", element)
                except Exception:
                    pass

                # find all unread single chats not group (span[class="x6s0dn4 xzolkzo x12go9s9 x1rnf11y xprq8jg x9f619 x3nfvp2 xl56j7k x1spa7qu x1kpxq89 xsmyaan"])
                chat_btns = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/messages/"]')
                chat_list = []
                for chat_btn in chat_btns:
                    #print(chat_btn.text)
                    try:
                        chat_btn.find_element(By.CSS_SELECTOR, 'span[class="x6s0dn4 xzolkzo x12go9s9 x1rnf11y xprq8jg x9f619 x3nfvp2 xl56j7k x1spa7qu x1kpxq89 xsmyaan"]')
                        chat_name = chat_btn.find_element(By.CSS_SELECTOR, 'span[class="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft"]').text
                        chat_list.append({ "obj" : chat_btn, "name" : chat_name })
                    except Exception:
                        continue

                for chat_info in chat_list:
                    chat_btn = chat_info["obj"]
                    driver.execute_script("arguments[0].click();", chat_btn)
                    time.sleep(1)
                    # Wait until box is visible
                    try:
                        main = WebDriverWait(driver, 15).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="main"]'))
                        )
                    except Exception as e:
                        print(e)

                    try:
                        button = driver.find_element(By.CSS_SELECTOR, 'p[class="xat24cr xdj266r"]')
                        driver.execute_script("arguments[0].click();", button)
                        button.send_keys(" ")
                    except Exception:
                        pass
                    
                    try:
                        profile_btn = driver.find_elements(By.CSS_SELECTOR, 'a[class="x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1rg5ohu x1a2a7pz xs83m0k"]')
                        facebook_info = None
                        if len(profile_btn) > 0:
                            profile_btn = profile_btn[0]
                            profile_link = urljoin(driver.current_url, profile_btn.get_attribute("href"))

                            facebook_info = facebook_infos.get(profile_link)
                            if facebook_info != None:
                                last_access_ts = facebook_info.get("Last access", 0)
                                
                                # Get the current time Unix timestamp minus 3 days (3 days = 3 * 24 * 60 * 60 seconds)
                                three_days_ago = int(time.time()) - 3 * 24 * 60 * 60
                                
                                if last_access_ts < three_days_ago:
                                    facebook_info = None

                            if facebook_info == None:
                                driver.switch_to.window(profile_tab)
                                driver.get(profile_link)
                                print(f"Đang lấy thông tin cá nhân từ {profile_link}")
                                
                                wait_for_load(driver)
                                time.sleep(0.5)
                
                                find_who_chatted = driver.find_elements(By.CSS_SELECTOR, 'h1[class^="html-h1 "]')
                                who_chatted = find_who_chatted[-1].text
                                
                                facebook_info = { "Facebook name" : who_chatted, "Facebook url" :  profile_link, "Last access" : int(time.time()) }
                                
                                # Loop through the profile sections
                                for sk in sk_list:
                                    # Build the full URL for the profile section
                                    info_url = urljoin(profile_link, sk)
                                    driver.get(info_url)

                                    # Wait for the page to load
                                    wait_for_load(driver)
                                    #time.sleep(0.5)

                                    # Find the info elements
                                    info_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class="xyamay9 xqmdsaz x1gan7if x1swvt13"] > div')

                                    # Loop through each info element
                                    for info_element in info_elements:
                                        title = find_and_get_text(info_element, By.CSS_SELECTOR, 'div[class="xieb3on x1gslohp"]')
                                        if title is not None:
                                            detail = []

                                            # Append the text lists to the detail array
                                            detail.extend(find_and_get_list_text(info_element, By.CSS_SELECTOR, 'div[class="x1hq5gj4"]'))
                                            detail.extend(find_and_get_list_text(info_element, By.CSS_SELECTOR, 'div[class="xat24cr"]'))

                                            # Add title and details to the facebook_info dictionary
                                            facebook_info[title] = detail
                                
                                facebook_infos[profile_link] = facebook_info
                            else:
                                who_chatted = facebook_info.get("Facebook name")

                            last_access_ts = facebook_info.get("Last access", 0)
                            facebook_info["Last access"] = int(time.time())
                            if pickle_to_file(f_facebook_infos, facebook_infos) == False:
                                print(f"Không thể sao lưu vào {f_facebook_infos}")
                            # First time upload
                            if last_access_ts == 0 and (if_running_on_github_workflows):
                                upload_file(GITHUB_TOKEN, GITHUB_REPO, f_facebook_infos, STORAGE_BRANCE)
                        else:
                            who_chatted = chat_info["name"]
                            facebook_info = { "Facebook group name" : who_chatted }
                    except Exception as e:
                        print(e)
                        continue

                    driver.switch_to.window(chat_tab)
                    print("Tin nhắn mới từ " + who_chatted)
                    print(json.dumps(facebook_info, ensure_ascii=False, indent=2))
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, 'p[class="xat24cr xdj266r"]')
                        driver.execute_script("arguments[0].click();", button)
                        button.send_keys(" ")
                    except Exception:
                        pass

                    parsed_url = urlparse(driver.current_url)

                    # Remove the trailing slash from the path, if it exists
                    urlpath = parsed_url.path.rstrip("/")
                    
                    # Split the path and extract the ID
                    path_parts = urlpath.split("/")
                    message_id = path_parts[-1] if len(path_parts) > 1 else "0"

                    time.sleep(1)

                    try:
                        msg_table = main.find_element(By.CSS_SELECTOR, 'div[role="grid"]')
                    except Exception:
                        continue
                    try:
                        msg_scroller = msg_table.find_element(By.CSS_SELECTOR, 'div[role="none"]')
                        #for _x in range(30):
                        #    # Scroll to the top of the message scroller
                        #    driver.execute_script("arguments[0].scrollTop = 0;", msg_scroller)
                        #    time.sleep(0.1)
                    except Exception:
                        msg_scroller = None

                    time.sleep(1)

                    # Get current date and time
                    current_datetime = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

                    # Format the output
                    day_and_time = current_datetime.strftime("%A, %d %B %Y - %H:%M:%S")
                    
                    prompt_list = []
                        
                    chat_history = chat_histories.get(message_id, [])
                    print(json.dumps(chat_history, indent=4))
                    chat_history_new = []

                    header_prompt = get_header_prompt(day_and_time, who_chatted, facebook_info)

                    prompt_list.append(f'The Messenger conversation with "{who_chatted}" is as json here:')
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, 'p[class="xat24cr xdj266r"]')
                        driver.execute_script("arguments[0].click();", button)
                        button.send_keys(" ")
                    except Exception:
                        pass

                    print("Đang đọc tin nhắn...")
                    for _x in range(30):
                        stop = False
                        for msg_element in reversed(msg_table.find_elements(By.CSS_SELECTOR, 'div[role="row"]:not([__read])')):
                            try: 
                                msg_element.find_element(By.CSS_SELECTOR, 'div[class="html-div xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a xyk4ms5"]').text
                                # our msg, at this point we should shop reading if we cached previous one
                                if len(chat_history) > 0:
                                    stop = True
                            except:
                                pass
                        if stop:
                            break
                            
                            driver.execute_script('arguments[0].setAttribute("__read", "yes");', msg_element)
                        driver.execute_script("""
                                var divs = document.querySelectorAll('div.x78zum5.xdt5ytf[data-virtualized="false"], div.x78zum5.xdt5ytf[data-virtualized="true"]');
                                divs.forEach(function(div) {
                                    var disabledDiv = document.createElement('disabled-div');
                                    disabledDiv.innerHTML = div.innerHTML;  // Keep the content inside
                                    div.parentNode.replaceChild(disabledDiv, div);  // Replace the div with the custom tag
                                });
                            """)
                        driver.execute_script("arguments[0].scrollTop = 0;", msg_scroller)
                        time.sleep(0.1)

                    for msg_element in reversed(msg_table.find_elements(By.CSS_SELECTOR, 'div[role="row"]')):
                        try:
                            timedate = msg_element.find_element(By.CSS_SELECTOR, 'span[class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1pg5gke xvq8zen xo1l8bm x12scifz"]')
                            chat_history_new.insert(0, {"message_type" : "conversation_event", "info" : timedate.text})
                        except Exception:
                            pass

                        try:
                            quotes_text = msg_element.find_element(By.CSS_SELECTOR, 'div[class="xi81zsa x126k92a"]').text
                        except Exception:
                            quotes_text = None

                        # Finding name
                        stop = False
                        try: 
                            msg_element.find_element(By.CSS_SELECTOR, 'div[class="html-div xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp x11i5rnm x12nagc x1mh8g0r x1yc453h x126k92a xyk4ms5"]').text
                            break
                            name = myname
                            mark = "your_text_message"
                        except Exception:
                            name = None
                            mark = "text_message"

                        if name == None:
                            try: 
                                name = msg_element.find_element(By.CSS_SELECTOR, 'img[class="x1rg5ohu x5yr21d xl1xv1r xh8yej3"]').get_attribute("alt")
                                name =  f"{who_chatted} ({name})"
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
                            image_elements = msg_element.find_elements(By.CSS_SELECTOR, 'img[class="xz74otr xmz0i5r x193iq5w"]')
                            for image_element in image_elements:
                                try:
                                    data_uri = image_element.get_attribute("src")
                                    _url = None
                                    if data_uri.startswith("data:image/jpeg;base64,"):
                                        # Extract the base64 string (remove the prefix)
                                        base64_str = data_uri.split(",")[1]
                                        # Decode the base64 string into binary data
                                        image_data = base64.b64decode(base64_str)
                                    else:
                                        image_data = requests.get(data_uri).content
                                        _url = data_uri

                                    image_hashcode = md5(image_data).hexdigest()
                                    image_name = f"files/img-{message_id}-{image_hashcode}"
                                    image_name = image_name[:40]
                                    os.makedirs(os.path.dirname(image_name), exist_ok=True)
                                    # Use BytesIO to create a file-like object for the image
                                    image_file = BytesIO(image_data)
                                    bytesio_to_file(image_file, image_name)
                                   
                                    chat_history_new.insert(0, {"message_type" : "file", "info" : {"name" : name, "msg" : "send image", "file_name" : image_name, "mime_type" : "image/jpeg" , "url" : _url }, "mentioned_message" : quotes_text})
                                except Exception:
                                    pass
                        except Exception:
                            pass

                        try:
                            video_element = msg_element.find_element(By.CSS_SELECTOR, 'video')
                            video_url = video_element.get_attribute("src")
                            video_data = get_file_data(driver, video_url)
                            video_hashcode = md5(video_data).hexdigest()
                            video_name = f"files/video-{message_id}-{video_hashcode}"
                            video_name = video_name[:40]
                            os.makedirs(os.path.dirname(video_name), exist_ok=True)
                            video_file = BytesIO(video_data)
                            bytesio_to_file(video_file, video_name)

                            chat_history_new.insert(0, {"message_type" : "file", "info" : {"name" : name, "msg" : "send video", "file_name" : video_name, "mime_type" : "video/mp4", "url" : None }, "mentioned_message" : quotes_text})
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
                        
                        chat_history_new.insert(0, {"message_type" : mark, "info" : {"name" : name, "msg" : msg}, "mentioned_message" : quotes_text })

                        try: 
                            react_elements = msg_element.find_elements(By.CSS_SELECTOR, 'img[height="16"][width="16"]')
                            emojis = ""
                            if len(react_elements) > 0:
                                for react_element in react_elements:
                                    emojis += react_element.get_attribute("alt")
                                emoji_info = f"The above message was reacted with following emojis: {emojis}"
                                
                                chat_history_new.insert(0, {"message_type" : "reactions", "info" : emoji_info})
                                
                        except Exception:
                            pass

                    print("Đã đọc xong!")

                    chat_history.extend(chat_history_new)

                    if len(chat_history) <= 0:
                        continue
                    last_msg = chat_history[-1]
                    for msg in chat_history:
                        final_last_msg = msg
                        if msg["message_type"] == "text_message" and is_cmd(msg["info"]["msg"]):
                            final_last_msg = copy.deepcopy(msg)
                            final_last_msg["info"]["msg"] = "<This is command message. It has been hidden>"
                        prompt_list.append(json.dumps(final_last_msg, ensure_ascii=False))
                        if msg["message_type"] == "file":
                            file_name = msg["info"]["file_name"]
                            mime_type = msg["info"]["mime_type"]
                            try:
                                file_upload = genai.get_file(file_name)
                            except Exception:
                                try:
                                    if msg["info"]["url"] is not None:
                                        get_raw_file(msg["info"]["url"], msg["info"]["file_name"])
                                    file_upload = genai.upload_file(path = file_name, mime_type = mime_type, name = file_name)
                                except Exception as e:
                                    print(e)
                                    continue
                            prompt_list.append(file_upload)
                        
                    for prompt in prompt_list:
                        print(prompt)

                    if last_msg["message_type"] == "your_text_message":
                        continue
                    is_command_msg = last_msg["message_type"] == "text_message" and is_cmd(last_msg["info"]["msg"])
                        
              
                    prompt_list.insert(0, header_prompt)
                    prompt_list.append(">> TYPE YOUR MESSAGE TO REPLY")
                    
                    caption = None
                    for _x in range(10):
                        try:
                            button = driver.find_element(By.CSS_SELECTOR, 'p[class="xat24cr xdj266r"]')
                            driver.execute_script("arguments[0].click();", button)
                            button.send_keys(" ")
                            if caption == None:
                                if is_command_msg:
                                    caption = parse_and_execute(last_msg["info"]["msg"])
                                else:
                                    caption = model.generate_content(prompt_list).text
                            button.send_keys(Keys.CONTROL + "a")  # Select all text
                            button.send_keys(Keys.DELETE)  # Delete the selected text
                            time.sleep(0.5)
                            button.send_keys(remove_non_bmp_characters(replace_emoji_with_shortcut(caption) + "\n"))

                            print("AI Trả lời:", caption)
                            chat_history.append({"message_type" : "your_text_message", "info" : {"name" : myname, "msg" : caption}, "mentioned_message" : None })
                            time.sleep(2)

                            break
                        except Exception as e:
                            if len(driver.find_elements(By.CSS_SELECTOR, 'div.x1n2onr6.x1ja2u2z.x9f619.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xyamay9.xkh2ocl.x57kliw.x1epquy7.x13fuv20.x178xt8z.x1l90r2v')):
                                break
                            print("Thử lại:", _x + 1)
                            print(e)
                            time.sleep(2)
                            continue
                    chat_histories[message_id] = chat_history
        except Exception as e:
            print(e)

    if if_running_on_github_workflows:
        upload_file(GITHUB_TOKEN, GITHUB_REPO, f_facebook_infos, STORAGE_BRANCE)
        if os.path.exists("files"):
            branch = upload_file(GITHUB_TOKEN, GITHUB_REPO, "files", generate_hidden_branch())
            for msg_id, chat_history in chat_histories.items():
                for msg in chat_history:
                    if msg["message_type"] == "file" and msg["info"]["url"] == None:
                        # Update url of file
                        msg["info"]["url"] = f'https://raw.githubusercontent.com/{GITHUB_REPO}/{branch}/{msg["info"]["file_name"]}'
        # Backup chat_histories
        pickle_to_file(f_chat_history + ".enc", chat_histories, encrypt_key)
        upload_file(GITHUB_TOKEN, GITHUB_REPO, f_chat_history + ".enc", STORAGE_BRANCE)
 
finally:
    driver.quit()
    