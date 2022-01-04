import sys
import string
import time
import pickle
import requests
from bs4 import BeautifulSoup 
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pynput.mouse import Button, Controller

# Click Chromecast TAG: google-cast-launcher

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

# If title is longer than 30 chars, cut off the buffer overflow

# Hash discord client ID

# (Store dict for each resolution and provider, then store that in X_AXS, etc)
# Use dict for screen resolution:
# if 1920x1080, use the right X and Y axis 
# and have number system for device listed;
# if chromecast is the 3rd device shown, do (default_y * device_num)
# to choose the proper device

mouse = Controller() 
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

# Second Monitor
# X_AX = 3583
# Y_AX = 1032
# X_OFFSET = 180
# Y_OFFSET = 762

# Prepare content
data = str(sys.argv[1]).lower().split(",")
content_type = int(sys.argv[3])
content = " ".join((data[0].lower().translate(str.maketrans('', '', string.punctuation)).strip()).split())
date = -1
if ("from year" in content):
    temp = content.split("from year")
    content = temp[0]
    date = int(temp[1])
    print(date)

if ("by date" in content):
    temp = content.split("by date")
    content = temp[0]
    date = int(temp[1])
    print(date)

season = 1
episode = 1
season_id = ''
provider_sleep = 0

content_sleep = 3

# data = "Curb your enthusiasm season 9, 10".lower().split(",")
# content_type = 1
# # content = " ".join(data[0].translate(str.maketrans('', '', string.punctuation)).lower().strip().split())
# content = " ".join(data[0].translate(str.maketrans('', '', string.punctuation)).lower().split())
# season = 1
# episode = 1
# season_id = ''

def update_tv_list(tv_list, content, season, episode):
    tv_list[content.lower()] = str(str(season) + "x" + str(episode))
    with open('tv_list.txt', 'wb') as f_list:
        pickle.dump(tv_list, f_list)

if (content_type == 1):

    if ("season" in data[0].lower()):
        extract = content.split("season")
        content = extract[0].strip()
        season = extract[1].strip()

    # Finds the next episode to watch if episode not specified
    with open('tv_list.txt', 'rb') as f_list:
        tv_list = pickle.load(f_list)

    try:
        episode = data[1].strip()
    except:
        try:
            watched = tv_list[content.lower()]
            watched = str(watched).split("x")
            season = int(watched[0])
            episode = int(watched[1])
        except:
            episode = 1

def init_chrome():
    # chrome_options.add_argument('--user-data-dir=/Users/logan/Documents/VSCode/LoganProfile')
    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument("no-default-browser-check")
    chrome_options.add_argument("no-first-run")
    chrome_options.add_argument('--window-size=1920,1080')   
    chrome_options.add_extension('uBlock.crx') # Add uBlock to prevent redirects
    return chrome_options

driver = webdriver.Chrome(options=init_chrome())

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

# This grabs the correct title of the desired content to search for (IMDB is more trustworthy than Google)
# BeautifulSoup is twice as fast as selenium
def get_safe_search(content):
    result = requests.get('https://www.imdb.com/find?q=' + content.replace(' ', '%20') + ('&s=tt&ttype=tv&ref_=fn_tv' if content_type == 1 else '&s=tt&ttype=ft&ref_=fn_ft'))
    soup = BeautifulSoup(result.content, 'lxml')
    listings = soup.find_all('td')

    content = content.replace(" ", "")
    for i in listings:
        title = i.find('a').text
        no_punc_no_space = " ".join(title.translate(str.maketrans('', '', string.punctuation)).lower().split()).replace(" ", "")
        if content == no_punc_no_space:
            content = title
            break

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

    # soap2day's search requires the exact text to get the result,
    # so this grabs the correct title of the desired content to search for (IMDB is more trustworthy than Google)
    content = get_safe_search(content)
    
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

    driver.get(MAIN_URL + "search/keyword/" + safe_content)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumbnail')))
    
    if (content_type == 1):
        results = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div[2]/h5/a[1]')

        count = 0
        for i in results:
            count += 1
            if (content == i.get_attribute('innerHTML')):
                # If a date was provided; choose the right result
                if (date != -1):
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
            episode = int(episode) + 1

        update_tv_list(tv_list, content, season, episode)
    else:
        results = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/h5/a')

        count = 0
        for i in results:
            count += 1
            if (content == i.get_attribute('innerHTML')):
                # If a date was provided; choose the right result
                if (date != -1):
                    temp_date = driver.find_element_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[' + str(count) + ']/div/div[1]/div')
                    if (not str(date) in temp_date.get_attribute('innerHTML')):
                        continue
                i.click()
                break

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumbnail')))
        driver.execute_script('window.scrollTo(0, 500)')

    start_chromecast()

def get_stream():
    if (PROVIDER == 0):
        ummagurau(tv_list, content, season, episode, date)
    elif (PROVIDER == 1):
        soap2day(tv_list, content, season, episode, date)

def main():
    get_stream()
    print("Script Finished.")

if __name__ == "__main__":
    main()
