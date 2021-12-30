import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pynput.mouse import Button, Controller

print(str(sys.argv[1]))

# Subtract or add pixels for amount of monitors

data = str(sys.argv[1]).split(",")
count = len(data)
content_type = 0
content = data[0].lower()
episode = -1


if (count == 1):
    content_type = 0 # 0 For Movie
else:
    content_type = 1
    episode = data[1].strip()

# content_type = 1
# content = "mr robot"
# episode = 6

mouse = Controller()

chrome_options = Options()
chrome_options.add_argument('--user-data-dir=/Users/logan/Documents/VSCode/LoganProfile')
chrome_options.add_argument('log-level=3')

driver = webdriver.Chrome(options=chrome_options)

MAIN_URL = "https://www1.ummagurau.com/"

# Go to start page
driver.get(MAIN_URL)

# Search For Content
search_field = driver.find_element_by_xpath('//*[@id="search-home"]/div/form/input')
search_field.send_keys(content)
search_field.send_keys(Keys.RETURN)

#Find the right show
content_list = driver.find_elements_by_class_name("flw-item")

for i in content_list:
    string = str(i.get_attribute("innerHTML").split('title="')[1])
    print(string)
    is_found = str(content) in string.lower()
    if (is_found):
        content_link = string.split('"') # Match the partial link text to the actual name
        link = str(driver.find_element_by_partial_link_text(content_link[0]).get_attribute("href"))
        driver.get(link)
        break

if (content_type == 1):
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "slce-list")))
    element = element.get_attribute("innerHTML")
    id = element.split('"')[5]
    time.sleep(1)
    second = driver.find_element_by_id(str(id)).get_attribute("innerHTML")
    nav = second.split('<ul class="nav">')[1]
    links = nav.split('<li class="nav-item">')

    for i in range(1, len(links)):
        if (str("Eps " + str(episode) + ":") in links[i]):
            driver.find_element_by_id(links[i].split('"')[1]).click()
            break
else:
    print("movie")
# Let page load
time.sleep(3)

# Initial Play Click
mouse.position = (3579, 1030)
time.sleep(1)

# Fullscreen and pause clicks
mouse.click(Button.left)
mouse.click(Button.left)
mouse.click(Button.left)
time.sleep(1)

# Chromecast Button
mouse.position = (3583, 1032)
mouse.click(Button.left)
mouse.move(-180, -762)
time.sleep(1)
mouse.click(Button.left)

print("Script Finished.")