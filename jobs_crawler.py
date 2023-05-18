from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import csv
import re
from csv import writer
import logging
from webdriver_manager.core.logger import set_logger

## Set Custom Logging ##
logger = logging.getLogger("upwork_helper_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("upwork_helper.log"))

set_logger(logger)

## Set Chrome Driver Options ##

chrome_options = Options()
# chrome_options.add_argument("--incognito")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--user-data-dir=C:/Users/Acer/AppData/Local/Google/Chrome/User Data')
# chrome_options.add_argument('--profile-directory=Profile 1'),
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless") # This won't show the window
chrome_options.binary_location = "/usr/bin/google-chrome-stable"

print('Enter keyword: ')
keyword = input()

url = f"https://www.upwork.com/nx/jobs/search/?q={keyword}&sort=recency"
# url = f'https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi'

driver = webdriver.Chrome(options=chrome_options)

driver.get(url)
time.sleep(60)

counter = 0

## Check if the Upwork website is reached out
logger.info(driver.title)

def jobs_crawler():
    #open document and start writing process
    with open('UpworkJobs.csv','a+', encoding="utf-8", newline='') as fd:
        csv_writer = writer(fd, delimiter=",")
    
        # write title
        csv_writer.writerow([
                    'Job Title',
                    'Job Type',
                    'Contractor Tier'
                    ])
    
        while True:
    
            # wait content to be loaded
            titleContent = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3[class='my-0 p-sm-right job-tile-title'] > a")))
            logger.info(f"title: {titleContent.getText()}")
            
            # detect next button
            nextButton = driver.find_elements(By.CSS_SELECTOR, "button[class='up-pagination-item up-btn up-btn-link'] > div[class='next-icon up-icon']")
    
            # take web element
            jobTitle = driver.find_elements(By.CSS_SELECTOR, "h3[class='my-0 p-sm-right job-tile-title'] > a")
            jobType = driver.find_elements(By.CSS_SELECTOR, "strong[data-test='job-type']")
            contractorTier = driver.find_elements(By.CSS_SELECTOR, "span[data-test='contractor-tier']")
            # write data to document
            for el in range(len(jobTitle)):
                csv_writer.writerow([
                    jobTitle[el].text,
                    jobType[el].text,
                    contractorTier[el].text
                    ])
                
            # detect next button disabled
            if (len(nextButton) == 0):
                break          
            
            # move to next page
            nextButton[0].click()
            time.sleep(2)
    
            counter += 1
            logger.info('page: ' + str(counter))

            if (counter == 5):
                break