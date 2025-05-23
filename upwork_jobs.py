import time
import json
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# User credentials and target URL
UPWORK_EMAIL = 'kevinbruyne0125@outlook.com'
UPWORK_PASSWORD = 'Mymother081*'
TARGET_URL = 'https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668420,531770282584862722,531770282580668419,531770282580668422,531770282580668418&contractor_tier=2,3&duration_v3=month,semester,ongoing&location=United%2520States&nbs=1&payment_verified=1&per_page=50&proposals=0-4,5-9,10-14,15-19&sort=recency&t=0,1&page=1'
API_URL = "https://www.upwork.com/api/graphql/v1?alias=userJobSearch"

def login_upwork():
    driver = uc.Chrome()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get('https://www.upwork.com/ab/account-security/login')
        wait.until(EC.visibility_of_element_located((By.ID, 'login_username'))).send_keys(UPWORK_EMAIL)
        driver.find_element(By.ID, 'login_password_continue').click()

        # Wait for CAPTCHA (if it shows up)
        time.sleep(10)
        # Manually solve CAPTCHA if necessary

        wait.until(EC.visibility_of_element_located((By.ID, 'login_password'))).send_keys(UPWORK_PASSWORD)
        driver.find_element(By.ID, 'login_control_continue').click()

        # Wait for avatar to confirm login
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img.nav-avatar.nav-user-avatar')))
        print("Login successful.")

        driver.get(TARGET_URL)
        time.sleep(5)

        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-test="next-page"]'))).click()
        time.sleep(6)

        # You could scrape data from the page if needed
        # job_data = fetch_jobs(API_URL)
        logs = driver.execute_cdp_cmd('Network.getResponseBody', {})

# Check the network requests
        network_requests = driver.execute_cdp_cmd('Network.getResponseBody', {})
        for request in network_requests['result']['response']['url']:
            if API_URL in request['url']:  # Replace with the actual API endpoint
                print("API Response:", request['response']['body'])
        print("-----------API DATA-----------")
        # print(job_data)

        with open('upwork_jobs.json', 'w') as json_file:
            json.dump(job_data, json_file, indent=4)

    finally:
        driver.quit()

def fetch_jobs(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs: {e}")
        return None

def main():
    login_upwork()

if __name__ == "__main__":
    main()
