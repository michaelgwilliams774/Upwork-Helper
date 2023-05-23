from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from inputimeout import inputimeout, TimeoutOccurred
import time
import csv
import re
from csv import writer
from csv import DictReader
import random
# import pandas as pd
# import xlrd
# Custom Logging
import logging
from webdriver_manager.core.logger import set_logger
# Handling Exception
from selenium.common.exceptions import NoSuchElementException


## Set Custom Logging ##
logger = logging.getLogger("upwork_helper_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler("upwork_helper.log"))

set_logger(logger)

## Set Chrome Driver Options ##

chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222") #Important for open chromebrowser
# chrome_options.add_argument("--incognito")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument('--user-data-dir=C:/Users/Acer/AppData/Local/Google/Chrome/User Data')
# chrome_options.add_argument('--profile-directory=Profile 1'),
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless") # This won't show the window
chrome_options.page_load_strategy = 'normal'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.binary_location = "/usr/bin/chromium"

driver = webdriver.Chrome(options=chrome_options)

# Authenticate Upwork
def keyboard_dummyClick(element, word, delay):
    for c in word:
        element.send_keys(c)
        time.sleep(random.uniform(0.1, delay))
    
def authenticate(email, password, sec_answer):
    url = f"https://www.upwork.com/ab/account-security/login"
    driver.get(url)
    driver.add_cookie({"name":"cookie_domain", "value": ".upwork.com"})
    driver.add_cookie({"name":"lang", "value": "en"})
    driver.add_cookie({"name":"IR_gbd", "value": "upwork.com"})
    time.sleep(10)
    
    username = driver.find_element(By.ID, "login_username")
    continueWithEmailBtn = driver.find_element(By.ID, "login_password_continue")
    keyboard_dummyClick(username, email, 0.3)
    continueWithEmailBtn.click()
    time.sleep(3)
    
    passwordInput = driver.find_element(By.ID, "login_password")
    loginBtn = driver.find_element(By.ID, "login_control_continue")
    keyboard_dummyClick(passwordInput, password, 0.2)
    loginBtn.click()
    time.sleep(10)
    
    # If it goes to the security answer page:
    if check_exists_by_id("login_answer"):
        securityAnswerInput = driver.find_element(By.ID, "login_answer")
        continueBtn = driver.find_element(By.ID, "login_control_continue")
        keyboard_dummyClick(securityAnswerInput, sec_answer, 0.2)
        continueBtn.click()
        time.sleep(3)

def upwork_login():
    with open('./UpworkCredentials.csv', newline='') as fd:
        csv_reader = DictReader(fd)
        for row in csv_reader:
            if authenticate(row['Email'], row['Password'], row['Security_Answer']):
                scraping = jobs_crawler()
                if scraping:
                    bid_status = bid_project()
                    if bid_status:
                        log_out()
    return True

# Scrape the latest jobs and save to UpworkJobs.csv
def jobs_crawler():
    ### Get the User input for filtering options ###
    print('Enter keyword to search: ')
    keyword = input()
    print()
    
    print('Find payment verified jobs?:(y or n) ')
    verified = input()
    print()
    if verified == 'y' or verified == 'Y' or verified == 'yes':
        payment_verified = '&payment_verified=1'
    else:
        payment_verified = ''
    
    print('Filter by location:(e.g United States,United Kingdom) ')
    location = input()
    print()
    if len(location):
        location = f'&location={location}'
   #################################################

    # url = f"https://www.upwork.com/nx/jobs/search/?q={keyword}&sort=recency" # without Login
    url = f"https://www.upwork.com/nx/jobs/search/?q={keyword}&sort=recency{payment_verified}{location}" # with login
    driver.get(url)
    driver.add_cookie({"name":"cookie_domain", "value": ".upwork.com"})
    driver.add_cookie({"name":"lang", "value": "en"})
    driver.add_cookie({"name":"IR_gbd", "value": "upwork.com"})
    time.sleep(30)

    ## Check if the Upwork website is reached out
    # logger.info(driver.title)
    counter = 0
    #open document and start writing process
    with open('./UpworkJobs.csv','w', encoding="utf-8", newline='') as fd:
        csv_writer = writer(fd, delimiter=",")
    
        # write title
        csv_writer.writerow([
                    'Job Title',
                    'Job link',
                    'Job Type',
                    'Fixed Salary',
                    'Work Load',
                    'Skills',
                    'Spent',
                    'Country',
                    'Payment Verification',
                    'Contractor Tier',
                    'Description'
                    ])
    
        # while True:  # This will be used when we need to navigate to next pages
        # wait content to be loaded
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h3[class='my-0 p-sm-right job-tile-title'] > a")))

        # detect next button
        # nextButton = driver.find_elements(By.CSS_SELECTOR, "button[class='up-pagination-item up-btn up-btn-link'] > div[class='next-icon up-icon']")

        # take web element
        jobCard = driver.find_elements(By.CSS_SELECTOR, "section[data-test='JobTile']")
        # write data to document
        for el in range(len(jobCard)):
            titleEls = jobCard[el].find_elements(By.CSS_SELECTOR, "h3[class='my-0 p-sm-right job-tile-title'] > a")
            typeEls = jobCard[el].find_elements(By.CSS_SELECTOR, "strong[data-test='job-type']")
            salaryEls = jobCard[el].find_elements(By.CSS_SELECTOR, "span[data-test='budget']")
            workLoadEls = jobCard[el].find_elements(By.CSS_SELECTOR, "span[data-test='duration']")
            contractorTierEls = jobCard[el].find_elements(By.CSS_SELECTOR, "span[data-test='contractor-tier']")
            skillTagEls = jobCard[el].find_elements(By.CSS_SELECTOR, "a[class='up-skill-badge text-muted'] > span")
            paymentEls = jobCard[el].find_elements(By.CSS_SELECTOR, "small[data-test='payment-verification-status'] > strong")
            spentEls = jobCard[el].find_elements(By.CSS_SELECTOR, "span[data-test='EarnedAmountFormatted'")
            countryEls = jobCard[el].find_elements(By.CSS_SELECTOR, "small[data-test='client-country'] > strong")
            descriptionEls = jobCard[el].find_elements(By.CSS_SELECTOR, "span[data-test='job-description-text']")

            csv_writer.writerow([
                titleEls[0].text if len(titleEls) else '',
                titleEls[0].get_attribute("href") if len(titleEls) else '',
                typeEls[0].text if len(typeEls) else '',
                salaryEls[0].text if len(salaryEls) else '',
                workLoadEls[0].text if len(workLoadEls) else '',
                ','.join((tag.text for tag in skillTagEls)), 
                spentEls[0].text if len(spentEls) else '',
                countryEls[0].text if len(countryEls) else '',
                paymentEls[0].text if len(paymentEls) else '',
                contractorTierEls[0].text if len(contractorTierEls) else '',
                descriptionEls[0].text if len(descriptionEls) else ''
                ])

        # detect next button disabled
        # if (len(nextButton) == 0):
        #     break          

        # move to next page
        # nextButton[0].click()
        # time.sleep(2)

#         counter += 1
#         logger.info('page: ' + str(counter))

#         if (counter == 2):
#             break
    print("Successfully got the job list")
    logger.info("Successfully got the job list")
    return True

# Bid for the project
def bid_project():
    time.sleep(10)
    projects = []
    temp = []
    with open('./UpworkJobs.csv', newline='') as fd:
        csv_reader = DictReader(fd)
        for row in csv_reader:
            temp.append(row)
        
    bid_status = _make_bid_on_projects(temp)
    return bid_status
    # logger.info('projects - ', len(projects))

            
def _make_bid_on_projects(jobs_file_content):
    ### Read jobs file and return the filtered projects ###
    projects = []
    for row in jobs_file_content:
        spent = row['Spent'].split('$').pop()     
        if 'K+' in spent:
            spent = spent.replace('K+', '000')
        elif 'M+' in spent:
            spent = spent.replace('M+', '000000')
        
        row['Spent'] = int(spent)
        
        if row['Job Type'] == 'Fixed-price':
            projects.append(row)
            projects[-1]['Type'] = 'fixed'
            projects[-1]['Budget'] = int(row['Fixed Salary'].split('$').pop().replace(',', ''))
        
        elif "Hourly" in row['Job Type']:
            projects.append(row)
            projects[-1]['Type'] = 'hourly'
            if len(row['Fixed Salary'].split(':')) > 1:
                projects[-1]['Budget'] = int(row['Fixed Salary'].split(':').pop(1).split('$').pop().replace(',', ''))
            else:
                projects[-1]['Budget'] = 0
    
    filtered_projects = filter_by_AI_projects(projects)
    
    # bid for projects
    for item in filtered_projects:
        if _bid_for_project(item):
            continue
        else:
            print("Error in bid for fixed project")
            logger.info("Error occurred in bidding for fixed project")
            break
        driver.get_screenshot_as_file("screenshot_bid_project.png")
    return True
        
def filter_by_AI_bid(project):
    # open workbook
    # wb = xlrd.open_workbook(r'.\UpworkBids.xlsx')
    # # open first sheet
    # sheet = wb.sheet_by_index(0)
    with open('./UpworkBids.csv', newline='') as fd:
        csv_reader = DictReader(fd, delimiter=';')
        bids = []
        for row in csv_reader:
            print(row)
            bids.append({
                "Bid_content": row['Bid_content']
            })
            tag = row['Tag']
            bid = row['Bid_content']
            project_description = project['Description']
            # clean string
            pat = re.compile(r'[^a-zA-Z ]+')
            tag = re.sub(pat, '', tag).lower()
            project_description = re.sub(pat, '', project_description).lower()
            
            # split string
            splits = project_description.split()
            
            result = {}
            for x in tag.split():
                result[x] = 0
                for y in project_description.split():
                    if x == y:
                        result[x] += 1
            bids[-1]['Match_case'] = sum(result.values()) / len(result.values())
        
        return (sorted(bids, key = lambda x: x['Match_case'], reverse = True))[0]['Bid_content'].replace('. ', '.\n')

def filter_by_AI_projects(projects):
    ### Temporary emulation of AI ###
    ### We will add real AI feature in this subroutine later ###
    # logger.info('projects type - ', type(projects))
    filtered_by_budget = sorted(projects, key = lambda x: x['Budget'], reverse = True)[:5]
    filtered_by_spent = sorted(projects, key = lambda x: x['Spent'], reverse = True)[:5]
    for item in filtered_by_spent:
        if item not in filtered_by_budget:
            filtered_by_budget.append(item)
    return filtered_by_budget

def _bid_for_hourly_project(project):
    ### Make bid for hourly project###
    return
    
def _bid_for_project(project):
    ### Make bid for fixed project ###
    driver.get(project['Job link'])
    time.sleep(5)
    try:
        applyNowBtn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Apply Now']")
        try:
            disabled = applyNowBtn.get_attribute("disabled")
            if disabled:
                print('Apply Now button is disabled')
                return True
            else:
                print('Apply Now button is enabled')
                applyNowBtn.click()
        except:
            return True
    except NoSuchElementException:
        return True
    
    # After clicking "Apply Now" button, it will be redirected to new page - apply page
    # So we need to wait
    time.sleep(10)
    # WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='up-modal-dialog']")))
    # When make bid for the first time after creating the account,
    # you may get "Use connects to submit proposals" dialog
    print(check_exists_by_css("div[class='up-modal-dialog']"))
    if check_exists_by_css("div[class='up-modal-dialog']"):
        modalDialog = driver.find_element(By.CSS_SELECTOR, "div[class='up-modal-dialog']")
        try:
            if modalDialog.find_element(By.CSS_SELECTOR, "h2[class='text-center']").text == "Use Connects to submit proposals":
                closeBtn = driver.find_element(By.CSS_SELECTOR, "div[class='up-modal-footer'] > div > div > button")
                closeBtn.click()
        except NoSuchElementException:
            return False
    
    driver.implicitly_wait(15)
    if check_exists_by_css("input[name='milestoneMode'][value='default']"): # This will be only for fixed projects
        # Handle milestone mode
        milestoneRadioBtn = driver.find_element(By.CSS_SELECTOR, "input[name='milestoneMode'][value='default']")
        driver.execute_script("arguments[0].click();", milestoneRadioBtn) # Javascript Executor - radio button often has "ElementClickInterceptedException"
        # milestoneRadioBtn[1].click()

        durationDropDown = driver.find_element(By.CSS_SELECTOR, "div[aria-describedby='duration-error']")
        durationDropDown.click()
        time.sleep(5)
        dropdownOptions = driver.find_elements(By.CSS_SELECTOR, "ul[aria-labelledby='duration-label'] > li")
        dropdownOptions[-1].click() # select "less than one month"
    
    # Cover Letter Area
    coverLetterTextArea = driver.find_element(By.CSS_SELECTOR, "textarea[aria-labelledby='cover_letter_label']")
    bidText = filter_by_AI_bid(project)
    coverLetterTextArea.send_keys(bidText)
    # Questions Area
    if check_exists_by_css("div[class='fe-proposal-job-questions questions-area'] > div[class='form-group up-form-group'] > div > textarea[class='up-textarea']"):
        questionsAreas = driver.find_elements(By.CSS_SELECTOR, "div[class='fe-proposal-job-questions questions-area'] > div[class='form-group up-form-group'] > div > textarea[class='up-textarea']")
        for questionEl in questionAreas:
            questionEl.send_keys("Let's jump on a quick call to discuss further details")
    
    # Send for 8/6/4 default connects
    sendBtn = driver.find_element(By.CSS_SELECTOR, "footer[class*='pb-10 mt-20'] > div > button")
    sendBtn.click()
    
    # Understand Upwork TOS or Escrow Modal
    print(check_exists_by_css("div[class='up-modal-dialog']"))
    if check_exists_by_css("div[class='up-modal-dialog']"):
        modalDialog = driver.find_element(By.CSS_SELECTOR, "div[class='up-modal-dialog']")
        try:
            # if modalDialog.find_element(By.CSS_SELECTOR, "h2[class='up-modal-title']").text.strip() == "Stay safe & build your reputation":
            agreeCheckBox = modalDialog.find_element(By.CSS_SELECTOR, "input[name='checkbox']")
            driver.execute_script("arguments[0].click();", agreeCheckBox)
            time.sleep(2)
            submitBtn = modalDialog.find_element(By.CSS_SELECTOR, "div[class='up-modal-footer'] > div > button[class='up-btn up-btn-primary m-0 btn-primary']")
            submitBtn.click()
            time.sleep(3)
            return True
        except NoSuchElementException:
            print("Error in agreeing TOS")
            return False
    
    return False

# Utilities
def check_exists_by_id(element_id):
    try:
        temp = driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_css(element_class):
    try:
        temp = driver.find_element(By.CSS_SELECTOR, element_class)
    except NoSuchElementException:
        return False
    return True

def log_out():
    try:
        avatarBtn = driver.find_element(By.CSS_SELECTOR, "button[data-cy='menu-trigger']")
        avatarBtn.click()
        time.sleep(5)
        logoutBtn = driver.find_element(By.CSS_SELECTOR, "button[data-cy='logout-trigger']")
        time.sleep(5)
    except NoSuchElementException:
        return False
    return True