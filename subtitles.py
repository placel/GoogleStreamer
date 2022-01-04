import json
import time
import base64
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
 
chrome_options = Options()
chrome_options.add_extension('uBlock.crx') # Add uBlock to prevent redirects

driver = webdriver.Chrome(desired_capabilities=caps, options=chrome_options)
driver.get('https://soap2day.ac')

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

while True:
    browser_log = driver.get_log('performance') 
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]

    count = 0
    for log in events:
        try:
            request_id = log["params"]["requestId"]
            url = log["params"]["response"]["url"]
        except:
            continue
        if "English.srt" in url:
            response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
            caption_txt = str(base64.b64decode(response['body']))
            # Split by caption number regex

            # RegEx that splits at the caption number into an array
            # ex. \\n92\\r\\n
            captions = re.split(r"\\n\d{1,3}\\r\\n", caption_txt, 150)
            count = 0
            for i in captions:
                print(i)
                if "THEME MUSIC" in i:
                    print("INTRO FOUND:")
                    print(i)
                    print(count)
                    break
                count += 1
            exit()

    
    time.sleep(5)
