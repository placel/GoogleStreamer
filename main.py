import sys
import string
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pynput.mouse import Button, Controller

mouse = Controller() 

# PROVIDER = int(sys.argv[2])
PROVIDER = 1

# TO DO: Remove punctuation from both searched and results so they match

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
count = len(data)
content_type = 0
content = " ".join((data[0].lower().translate(str.maketrans('', '', string.punctuation)).strip()).split()).replace(" ", "")
season = 1
episode = 1
season_id = ''
provider_sleep = 0

content_sleep = 3

# data = "Avengers endgame".lower().split(",")
# count = len(data)
# content_type = 0
# # content = " ".join(data[0].translate(str.maketrans('', '', string.punctuation)).lower().strip().split())
# content = " ".join(data[0].translate(str.maketrans('', '', string.punctuation)).lower().split()).replace(" ", "")
# print(content)
# season = 1
# episode = 1
# season_id = ''

if (count == 1):
    content_type = 0 # 0 For Movie
else:
    content_type = 1 # 1 For TV Show
    episode = data[1].strip()
    has_season = "season" in data[0].lower()
    if ("season" in data[0].lower()):
        extract = content.split("season")
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
    time.sleep(1)

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

def ummagurau():
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

def soap2day(content):
    driver.get('https://www.imdb.com/find?q=' + content.replace(' ', '%20') + ('&s=tt&ttype=tv&ref_=fn_tv' if content_type == 1 else '&s=tt&ttype=ft&ref_=fn_ft'))

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/table/tbody/tr/td[2]/a')))
    listings = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/table/tbody/tr/td[2]/a')

    for i in listings:
        title = i.get_attribute('innerHTML')
        no_punc_no_space = " ".join(title.translate(str.maketrans('', '', string.punctuation)).lower().split()).replace(" ", "")
        if content == no_punc_no_space:
            content = title
            break
    
    driver.get(MAIN_URL)
    try:
        while(True):
            WebDriverWait(driver, .1).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-success'))).click()
    except:
        pass

    # Remove {':', ','}

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

        for i in results:
            if (content == i.get_attribute('innerHTML')):
                i.click()
                break

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumbnail')))

        seasons = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div')

        season_count = len(seasons)
        get_season = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div[' + str(int(season_count) - (int(season) -1)) + ']/div/div/a')

        for i in get_season:
            if (str(episode) == i.get_attribute('innerHTML').split(".")[0]):
                i.click()
                break
    else:
        results = driver.find_elements_by_xpath('/html/body/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/h5/a')

        for i in results:
            if (content == i.get_attribute('innerHTML')):
                i.click()
                break

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'thumbnail')))
        driver.execute_script('window.scrollTo(0, 500)')

    start_chromecast()

def get_stream():
    if (PROVIDER == 0):
        ummagurau()
    elif (PROVIDER == 1):
        soap2day(content)

def main():
    get_stream()
    print("Script Finished.")

if __name__ == "__main__":
    main()
