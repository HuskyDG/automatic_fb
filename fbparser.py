import re
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

def is_facebook_profile_url(url):
    # Define the regex pattern
    pattern = r'^https?://(www\.)?facebook\.com/profile\.php\?id=[^&]+'
    # Check if the URL matches the pattern
    return re.match(pattern, url) is not None

def get_facebook_id(fburl, selenium_cookies = None):
    session = requests.Session()
    cookies = {cookie["name"]: cookie["value"] for cookie in selenium_cookies} if selenium_cookies else None
    source = session.get(fburl, cookies=cookies)
    soup = BeautifulSoup(source.text, 'html.parser')
    myid = soup.find('meta', {'property': 'al:android:url'})
    if myid != None:
        myid = myid['content']
    if myid != None:
        myid = myid.lstrip("fb://profile/")
    if myid == None:
        if is_facebook_profile_url(fburl):
            parsed_url = urlparse(fburl)
            query_params = parse_qs(parsed_url.query)
            myid = query_params.get('id', [None])[0]
    return myid

def get_facebook_profile_url(selenium_cookies):
    """Fetch the Facebook profile URL using cookies from cookies.json."""
    try:
        # Convert list format to dictionary for requests
        cookies = {cookie["name"]: cookie["value"] for cookie in selenium_cookies}

        # Send request to Facebook profile page
        response = requests.get("https://www.facebook.com/profile.php", cookies=cookies, allow_redirects=True)

        # Return the final URL (after any redirections)
        return response.url

    except Exception as e:
        return f"Error: {e}"