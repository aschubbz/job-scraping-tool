import time
import json
import requests
from selenium import webdriver
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# User credentials and target URL
UPWORK_EMAIL = 'kevinbruyne0125@outlook.com'
UPWORK_PASSWORD = 'Mymother081*'
TARGET_URL = 'https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668420,531770282584862722,531770282580668419,531770282580668422,531770282580668418&contractor_tier=2,3&duration_v3=month,semester,ongoing&location=United%2520States&nbs=1&payment_verified=1&per_page=50&proposals=0-4,5-9,10-14,15-19&sort=recency&t=0,1&page=1'

# Initialize the WebDriver
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox

def login_upwork():
    driver.get('https://www.upwork.com/ab/account-security/login')
    time.sleep(2)

    # Type email and press continue
    # email_field = driver.find_element(By.ID, 'login_username')
    email_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'login_username'))
    )
    email_field.send_keys(UPWORK_EMAIL)
    
    # continue_button = driver.find_element(By.ID, 'login_password_continue')
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'login_password_continue'))
    )
    continue_button.click()
    time.sleep(2000)  # Wait for the next step to load
    # with SB(uc=True) as sb:
    #     sb.uc_gui_click_captcha()
    # try:
    #     captcha_element = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Verify you are human')]"))
    #     )
    #     print("Succeed in finding")
    #     # Find the checkbox within the CAPTCHA element and click it
    #     checkbox = captcha_element.find_element(By.TAG_NAME, 'input')
    #     if not checkbox.is_selected():
    #         checkbox.click()
    #         print("CAPTCHA checkbox clicked. Please verify manually if needed.")
        
    #     # Optionally, wait a bit for the user to complete any additional CAPTCHA steps
    #     time.sleep(10)  # Adjust as necessary for manual verification
    # except Exception as e:
    #     print("No CAPTCHA detected or an error occurred:", e)
    
    # Type password and press login
    # password_field = driver.find_element(By.ID, 'login_password')
    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'login_password'))
    )
    password_field.send_keys(UPWORK_PASSWORD)
    
    # login_button = driver.find_element(By.ID, 'login_control_continue')
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'login_control_continue'))
    )
    login_button.click()
    WebDriverWait(driver, 10).until(
        EC.url_changes('https://www.upwork.com/ab/account-security/login')
    )
    time.sleep(5)  # Wait for login to complete
    driver.get(TARGET_URL)

def fetch_jobs(api_url):
    response = requests.get(api_url)
    return response.json()

def main():
    login_upwork()
    
    time.sleep(5)  # Wait for the page to load

    # all_jobs = []

    # while True:
    #     # Fetch job data from the specified API
    #     api_url = "https://www.upwork.com/api/graphql/v1?alias=userJobSearch"
    #     job_data = fetch_jobs(api_url)
    #     all_jobs.extend(job_data['data']['searchJobs']['results'])  # Adjust based on actual API response structure

    #     # Check for a "Next" button and click it if it exists
    #     try:
    #         next_button = driver.find_element(By.XPATH, '//button[@data-test="next-page"]')
    #         next_button.click()
    #         time.sleep(5)  # Wait for the next page to load
    #     except Exception as e:
    #         print("No more pages or an error occurred:", e)
    #         break

    # # Save the data to a JSON file
    # with open('upwork_jobs.json', 'w') as json_file:
    #     json.dump(all_jobs, json_file, indent=4)

    driver.quit()

if __name__ == "__main__":
    main()