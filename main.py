import base64
import json
import sys
import re
import string
import time
import pickle
import requests
from pynput import keyboard
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By 
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller

# s2dfree no captcha
# https://s2dfree.is/enter.html

# jwDefaults
# cast.framework
# jwplayer().getPlaylist() - Get VTT 
# window.cast.framework.CastContext.getInstance().b
# window.cast.framework.CastContext.getInstance().requestSession() ------ requestSession(successCallback, errorCallback, sessionRequest)
# chrome.cast.media.Track = new chrome.cast.media.Track(customSubtitle, chrome.cast.media.TrackType.TEXT);
# https://developers.google.com/cast/docs/reference/web_sender/chrome.cast.media.LoadRequest#activeTrackIds ------ activeTracks
#  Media - Track - Scopes - Global - Caption
# You can set the active tracks in the media activeTrackIds request.
# -------------------
# https://developers.google.com/cast/docs/reference/web_sender/chrome.cast.media.LoadRequest#LoadRequest ----- Load Requests
# Media - WebVTT
# https://developers.google.com/android/reference/com/google/android/gms/cast/CastDevice#public-method-summary ----- CastDevice informations

# If content not found in IMDB, just pick the first result

# Some content with ... Won't work, have to seperate the name to get a result
# . ex 'Once Upon A Time... In Hollywood' into 'Once Upon A Time', or 'In Hollywood'

# Implement the Trakt API to track all content watched

# Skip intro:
# XPATH: //*[@id="player"]/div[2]/div[7]/div/div/div
# CLASS: jw-text-track-cue jw-reset
# -----------------------
# Subtitles CLASS: jw-settings-submenu-button, then by attribute 'aria-controls' and val 'jw-settings-submenu-captions'
# Or click 'c' on keyboard until either XPATH: //*[@id="player"]/div[2]/div[12]/div[4]/div[2]/div[15]/div/div 
# or CLASS: 'jw-text' == "English"
# Then in a duplicated tab, seek through every 1-2 seconds and check subtitle text.
# if ('THEME MUSIC') or similar is found, store time, then seek until next subtitle and store that time.
# then switch tabs and skip the casting tab to that time in the episode
#-------------------
# https://gist.github.com/lorey/079c5e178c9c9d3c30ad87df7f70491d
#---------------------------------
# Potential Keywords: (make a filter function)
# 'THEME MUSIC'
# 'Episode {episode number like 6x02}'
# '{Name of the episode}' sometimes in ""
# domain name of the .srt author site like www.subtitles.com
# 'Transcript'
# 'Subtitles'
# largest gap from one subtitle section to another
# '<font color' or </font>
# Ignore first gap (might be commercial for a different show)
 # Big gap and then next line contains a keyword

# 123movies
# Uses iFrame
#//*[@id="myVideo"]/div[2]/div[12]/div[4]/div[2]

mouse = Controller() 
keyboard = Controller()

tv_list = dict()

try:   
    PROVIDER = int(sys.argv[2])
except:
    PROVIDER = 1

PROVIDERS = [
    "https://www1.ummagurau.com/", 
    "https://soap2day.ac/"]

X_AXS = [
    1663,
    1205 ]

Y_AXS = [
    1032,
    1028 ]

X_OFFSETS = [
    -116,
    323 ]

Y_OFFSETS = [
    -873,
    -790 ]

MAIN_URL = PROVIDERS[PROVIDER]
X_AX = X_AXS[PROVIDER]
Y_AX = Y_AXS[PROVIDER]
X_OFFSET = X_OFFSETS[PROVIDER]
Y_OFFSET = Y_OFFSETS[PROVIDER]

# Prepare content
try:
    data = str(sys.argv[1]).lower().split(",")
    content_type = int(sys.argv[3])
    content = " ".join((data[0].lower().translate(str.maketrans('', '', string.punctuation)).strip()).split())
    date = -1
    if ("from year" in content):
        temp = content.split("from year")
        content = temp[0]
        date = int(temp[1])

    if ("by date" in content):
        temp = content.split("by date")
        content = temp[0]
        date = int(temp[1])

    if ("by year" in content):
        temp = content.split("by year")
        content = temp[0]
        date = int(temp[1])

    season = -1
    episode = -1
    season_id = ''
    provider_sleep = 0
except:
    data = "curb your enthusiasm".lower().split(",")
    content_type = 1
    # content = " ".join(data[0].translate(str.maketrans('', '', string.punctuation)).lower().strip().split())
    content = " ".join(data[0].translate(str.maketrans('', '', string.punctuation)).lower().split())
    season = -1
    episode = -1
    season_id = ''
    date = -1

content_sleep = 3

def get_tv_list(tv_list, content, date):
    print("Content: " + content)
    print("Date: " + str(date))
    try:
        with open('tv_list.txt', 'rb') as f_list:
            tv_list = pickle.load(f_list)
            up_next = tv_list[content.lower() + " (" + str(date) + ")"]
            print("BEFORE: " + str(tv_list))
    except:
        up_next = "error"
    return up_next
    
def update_tv_list(tv_list, content, season, episode):
    print("Content: " + content)
    tv_list[content.lower()] = str(str(season) + "x" + str(episode))
    print("AFTER: " + str(tv_list))
    try:
        with open('tv_list.txt', 'wb') as f_list:
            pickle.dump(tv_list, f_list)
    except:
        pass

# Prepares TV Shows 
if (content_type == 1):

    if ("season" in data[0].lower()):
        extract = content.split("season")
        content = extract[0].strip()
        season = extract[1].strip()

    try:
        episode = data[1].strip()
    except:
        episode = -1

def init_chrome():
    # chrome_options.add_argument('--user-data-dir=/Users/logan/Documents/VSCode/LoganProfile')
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument("no-default-browser-check")
    chrome_options.add_argument("no-first-run")
    chrome_options.add_extension('uBlock.crx') # Add uBlock to prevent redirects
    chrome_options.add_argument('--window-size=1920,1080')   
    return webdriver.Chrome(desired_capabilities=caps, options=chrome_options)

driver = init_chrome()

# Initial Play Click
def play():
    mouse.position = (X_AX, Y_AX)
    mouse.click(Button.left) # Hide Popup
    time.sleep(2)

# Fullscreen and pause clicks
def fullscreen():
    mouse.click(Button.left)
    mouse.click(Button.left)
    mouse.click(Button.left)
    time.sleep(2)

# Chromecast Button
def start_chromecast():
    mouse.position = (X_AX, Y_AX)
    time.sleep(2)
    mouse.click(Button.left)
    mouse.click(Button.left)
    time.sleep(1)
    mouse.position = (X_AX + X_OFFSET, Y_AX + Y_OFFSET)
    time.sleep(.5)
    # while(True):
    #     print(mouse.position)
    #     time.sleep(5)
    mouse.click(Button.left)

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def skip_intro():
    skip_buffer = 3
    time.sleep(5) # Wait for subtitles to load
    browser_log = driver.get_log('performance') 
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]

    for log in events:
        try:
            request_id = log["params"]["requestId"]
            url = log["params"]["response"]["url"]
        except:
            continue

        if "English.srt" in url:
            response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})

            captions = re.split(r'(\d\d:\d\d:\d\d,\d\d\d --> )', str(base64.b64decode(response['body'])), 70) # Change depending on the runtime of the show
            captions.pop()
            captions.pop()

            start_time = 0
            skip_to = 0
            count = 0
            skip_to = 0
            for i in range(2, len(captions)):
                print("Line: " + captions[i -1] + captions[i])
                if (count == -1):
                    break
                
                if "!!!!!!" in captions[i]:
                    print("INTRO FOUND:")
                    print(captions[i])
                    count = -1
                    break
                else:
                    try:
                        first = captions[i - 1].split(",")[0].split(":")
                        next_sub = captions[i + 1].split(",")[0].split(":")
                        gap = ((int(next_sub[1]) * 60) + int(next_sub[2])) - ((int(first[1]) * 60) + int(first[2])) 
                        if (gap > skip_to):
                            skip_to = gap
                            start_time = (int(first[1]) * 60) + int(first[2])
                    except:
                        pass
                    print("Gap: " + str(gap))
                    print()

                i += 2
            print("Max Gap: " + str(skip_to))

            # Don't skip if the intro is less than 7 seconds (handles short intros)
            if (skip_to >= 7):
                while(True):
                    current_time = int(driver.execute_script('return jwplayer().getPosition()'))
                    if current_time >= start_time:
                        break
                    time.sleep(1)
                driver.execute_script('jwplayer().seek(' + str(start_time + skip_to - skip_buffer) + ');')
            break

# Doesn't need X and Y axis, only uses keys and elements to cast (much faster and no init required)
def cast(device):
    # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="player"]/div[2]/div[12]/div[1]/div/div/div[2]/div'))).click()
    # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'google-cast-launcher'))).click()
    while(True):
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'google-cast-launcher'))).click()
            break
        except:
            continue
        
    time.sleep(.2)
    for i in range(0, int(device)):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)    

    time.sleep(5)
    driver.minimize_window()

# This grabs the correct title of the desired content to search for (IMDB is more trustworthy than Google)
# BeautifulSoup is twice as fast as selenium
def get_safe_search(content):
    result = requests.get('https://www.imdb.com/find?q=' + content.replace(' ', '%20') + ('&s=tt&ttype=tv&ref_=fn_tv' if content_type == 1 else '&s=tt&ttype=ft&ref_=fn_ft'))
    soup = BeautifulSoup(result.content, 'lxml')
    listings = soup.find_all('td') # Can be optimized to use class instead; cut listings in half

    found = False
    content = content.replace(" ", "")
    for i in listings:
        title = i.find('a').text
        no_punc_no_space = " ".join(title.translate(str.maketrans('', '', string.punctuation)).lower().split()).replace(" ", "")
        if content == no_punc_no_space:
            # content = title + "$%" + str(i.encode_contents()).split("</a>")[1].replace("(TV Series)", "").replace("(TV Mini Series)", "").replace("'", "").strip()
            content = title + "$%" + str(re.search(r"(\d\d\d\d)", str(i.encode_contents()).split("</a>")[1]).group()).strip()
            found = True
            break

    # Fix to include date in case for better search
    if (not found and len(listings) > 0):
        content = listings[1].find('a').text + "$%" + str(re.search(r"(\d\d\d\d)", str(i.encode_contents()).split("</a>")[1]).group()).strip()

    return content

def ummagurau(tv_list, content, season, episode, date):
    # Go to start page
    driver.get(MAIN_URL)

    # Search For Content
    search_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-home"]/div/form/input')))
    search_field.send_keys(content)
    search_field.send_keys(Keys.RETURN)

    # Grab resulting content
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-wrapper"]/div/section/div[5]/div/div/div[2]/h2/a')))
    content_list = driver.find_elements_by_xpath('//*[@id="main-wrapper"]/div/section/div[5]/div/div/div[2]/h2/a')
    type_list = driver.find_elements_by_xpath('//*[@id="main-wrapper"]/div/section/div[5]/div/div/div[2]/div/span[4]')

    # Click the right result 
    counter = 0
    for i in content_list:
        if (content in i.get_attribute('title').lower()):
            if ("TV" in type_list[counter].get_attribute('innerHTML')):
                i.click()
                break
        counter += 1
    
    if (content_type == 1):
        # Only change season if it's not the first season 
        season_count = 1
        if (int(season) > 1):
            button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-episodes"]/div/div[2]/div[1]/div[1]/div/button')))
            button.click()

            seasons = driver.find_elements_by_xpath('//*[@id="content-episodes"]/div/div[2]/div[1]/div[1]/div/div/a')
            season_count = len(seasons)
            
            time.sleep(.5)
            seasons[int(season)-1].click()
            season_id = seasons[int(season)-1].get_attribute('id').split("-")[1]
        else:
            season_id = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-episodes"]/div/div[2]/div[1]/div[3]/div/div[1]'))).get_attribute('id').split("-")[2]

        # Get Episodes and click the right one
        time.sleep(.5)
        episodes = driver.find_elements_by_xpath('//*[@id="ss-episodes-' + str(season_id) + '"]/ul/li/a')

        for i in episodes:
            if (("Eps " + str(episode) + ":") in i.get_attribute('title')):
                i.click()
        
        if (int(season) + 1 <= season_count and int(episode) + 1 > len(episodes)):
            season = int(season) + 1
            episode = 1
        else:
            episode = int(episode) + 1

        update_tv_list(tv_list, content, season, episode)
        # episodes[int(episode)-1].click()
        time.sleep(2)
    else:
        # Grab movie links by providers
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-episodes"]/div/div/ul/li/a')))
        links = driver.find_elements_by_xpath('//*[@id="content-episodes"]/div/div/ul/li/a')

        # Try first link
        links[0].click()
        content_sleep = 3
        time.sleep(content_sleep)
    
    play()
    fullscreen()
    start_chromecast()

def soap2day(tv_list, content, season, episode, date):
    # Don't know why 'content' doesn't exist in this context if it's not passed
    
    # The site has some sort of bot detection, and may show multiple welcome pages before it lets you in.
    # This tries to click  the 'Home' button forever until you're allowed access
    driver.get(MAIN_URL)
    try:
        while(True):
            WebDriverWait(driver, .1).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-success'))).click()
    except:
        pass

    # Remove certain punctuation from searching text because this site only looks at what comes after or before, but not combined
    # ex. Searching for 'Avengers: Endgame' shows 0 results, but searching for 'Avengers' or 'Endgame' alone returns the proper content
    safe_content = content
    if (':' in content):
        safe_content = content.split(':')[1]
    if (',' in content):
        safe_content = content.split(',')[1]
    if (';' in content):
        safe_content = content.split(';')[1]
    if ("..." in content):
        try:
            safe_content = content.split("...")[1]
        except:
            safe_content = content.split("...")[0]

    # Max search length is 30; If greater, only keep the first 30 chars
    driver.get(MAIN_URL + "search/keyword/" + (safe_content if len(safe_content) <= 30 else safe_content[:30]))
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumbnail')))
    
    if (content_type == 1):
        results = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div[2]/h5/a[1]')

        count = 0
        for i in results:
            count += 1
            if (content == i.get_attribute('innerHTML')):
                # If a date was provided; choose the right result
                temp_date = driver.find_element_by_xpath('/html/body/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[' + str(count) + ']/div/div[1]/div')
                if (not str(date) in temp_date.get_attribute('innerHTML')):
                    continue
                i.click()
                break

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumbnail')))

        seasons = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div')
        
        # The site shows seasons in reverse order (season 1 is at the bottom of the page);
        # this 'hash function' finds the right xpath element to seach for the given season
        get_season = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div[' + str(int(len(seasons)) - (int(season) -1)) + ']/div/div/a')
        
        for i in get_season:
            if (str(episode) == i.get_attribute('innerHTML').split(".")[0]):
                i.click()
                break
        
        # If the last episode, and theres another season available, set to the next season on episode 1
        if (int(season) + 1 <= len(seasons) and int(episode) + 1 > len(get_season)):
            season = int(season) + 1
            episode = 1
        else:
            episode = episode if int(season) + 1 and int(episode) + 1 > len(get_season) > len(seasons) else int(episode) + 1

        content += " (" + str(date) + ")"
        update_tv_list(tv_list, content, season, episode)
    else:
        results = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/h5/a')

        # Needs fix for when dates don't corrospond; ex Cabin in the Woods IMDB (2011) and soap2day (2012)
        count = 0
        for i in results:
            count += 1
            if (content == i.get_attribute('innerHTML')):
                # If a date was provided; choose the right result
                if (date != -1):
                    temp_date = driver.find_element_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[' + str(count) + ']/div/div[1]/div').get_attribute('innerHTML')
                    if (str(date) in temp_date):
                        pass
                    elif (str(date - 1) in temp_date): # Sometimes the IMDB date and the soap2day date does not match even if it's the right content
                        pass
                    elif (str(date + 1) in temp_date):
                        pass
                    else:
                        continue
                i.click()
                break
        content += " (" + str(date) + ")"

    cast(2)
    # This print tell the Discord Bot what to display as status
    if (content_type == 1):
        print("Content: " + content + ": " + str(season) + "x" + str(int(episode) -1))
    else:
        print("Content: " + content)

def get_stream(tv_list, content, season, episode, date):
    # Get Proper searching text
    content = get_safe_search(content)
    temp = content.split("$%")
    content = temp[0]
    
    try:
        if (date == -1):
            date = int(temp[1].replace("(", "").replace(")", ""))
    except:
        pass

    # If it's a TV Show, check if it's in the watched list
    if (content_type == 1):
        if (int(season) != -1 or int(episode) != -1):
            season = int(season) if int(season) >= 1 else 1
            episode = int(episode) if int(episode) >= 1 else 1
        else:
            up_next = get_tv_list(tv_list, content, date)
            print(up_next)
            if (up_next != "error"):
                season = int(up_next.split("x")[0])
                episode = int(up_next.split("x")[1])
            else:
                season = 1
                episode = 1

    if (PROVIDER == 0):
        ummagurau(tv_list, content, season, episode, date)
    elif (PROVIDER == 1):
        soap2day(tv_list, content, season, episode, date)

def main():
    get_stream(tv_list, content, season, episode, date)
    # skip_intro()
    print("Script Finished.")

if __name__ == "__main__":
    main()