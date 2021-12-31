import sys
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pynput.mouse import Button, Controller
mouse = Controller() 

# TO DO: Remove punctuation from both searched and results so they match

MAIN_URL = "https://www1.ummagurau.com/"
TYPE = {0: "Movie"}, {1: "TV"}

# First Monitor
X_AX = 1663
Y_AX = 1032
X_OFFSET = 116
Y_OFFSET = 873

# Second Monitor
# X_AX = 3583
# Y_AX = 1032
# X_OFFSET = 180
# Y_OFFSET = 762

# Prepare content
data = str(sys.argv[1]).lower().split(",")
count = len(data)
content_type = 0
content = data[0].lower().strip()
season = 1
episode = 1
season_id = ''

# data = "Euphoria season 1, 8".lower().split(",")
# count = len(data)
# content_type = 0
# content = data[0].lower().strip()
# season = 1
# episode = 1
# season_id = ''

content_sleep = 3

if (count == 1):
    content_type = 0 # 0 For Movie
else:
    content_type = 1 # 1 For TV Show
    episode = data[1].strip()
    has_season = "season" in data[0].lower()
    if ("season" in data[0].lower()):
        extract = data[0].split("season")
        content = extract[0].strip()
        season = extract[1].strip()

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

def search():
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

def get_episode():
    # Only change season if it's not the first season 
    if (int(season) > 1):
        button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-episodes"]/div/div[2]/div[1]/div[1]/div/button')))
        button.click()

        seasons = driver.find_elements_by_xpath('//*[@id="content-episodes"]/div/div[2]/div[1]/div[1]/div/div/a')
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

    # episodes[int(episode)-1].click()
    time.sleep(2)

def get_movie():
    # Grab movie links by providers
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content-episodes"]/div/div/ul/li/a')))
    links = driver.find_elements_by_xpath('//*[@id="content-episodes"]/div/div/ul/li/a')

    # Try first link
    links[0].click()
    content_sleep = 3
    time.sleep(content_sleep)

def get_stream():
    if (content_type == 1):
        get_episode()
    else:
        get_movie()

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
    time.sleep(2.5)

# Chromecast Button
def start_chromecast():
    mouse.position = (X_AX, Y_AX)
    mouse.click(Button.left)
    mouse.click(Button.left)
    time.sleep(1.5)
    mouse.position = (X_AX - X_OFFSET, Y_AX - Y_OFFSET)
    time.sleep(1)
    mouse.click(Button.left)

def main():
    search()
    get_stream()
    play()
    fullscreen()
    start_chromecast()
    print("Script Finished.")

if __name__ == "__main__":
    main()
