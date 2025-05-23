import time
import json
import requests
from selenium import webdriver 
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# User credentials and target URL
UPWORK_EMAIL = 'kevinbruyne0125@outlook.com'
UPWORK_PASSWORD = 'Mymother081*'
TARGET_URL = 'https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668420,531770282584862722,531770282580668419,531770282580668422,531770282580668418&contractor_tier=2,3&duration_v3=month,semester,ongoing&location=United%2520States&nbs=1&payment_verified=1&per_page=50&proposals=0-4,5-9,10-14,15-19&sort=recency&t=0,1&page=1'

def login_upwork():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')

    # Start Selenium Wire driver
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get('https://www.upwork.com/ab/account-security/login')
        
        wait.until(EC.presence_of_element_located((By.ID, 'login_username'))).send_keys(UPWORK_EMAIL)
        driver.find_element(By.ID, 'login_password_continue').click()

        # Wait for potential CAPTCHA
        time.sleep(10)

        wait.until(EC.presence_of_element_located((By.ID, 'login_password'))).send_keys(UPWORK_PASSWORD)
        driver.find_element(By.ID, 'login_control_continue').click()

        # Wait for login completion (avatar image as indicator)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img.nav-avatar.nav-user-avatar')))
        print("[+] Logged in successfully.")

        # Go to jobs page
        driver.get(TARGET_URL)
        time.sleep(5)

        # Click next page button (optional)
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-test="next-page"]')))
            next_btn.click()
            time.sleep(5)
        except Exception:
            print("[-] Next page button not found or clickable.")

        # Intercept the network request to fetch GraphQL job data
        job_data = None
        for request in driver.requests:
            if request.response and "graphql" in request.url and request.method == "POST" and request.url == "https://www.upwork.com/api/graphql/v1?alias=userJobSearch":
                try:
                    job_data = request.response.body.decode('utf-8')
                    break
                except Exception as e:
                    print("Error decoding job data:", e)

        if job_data:
            job_json = json.loads(job_data)
            with open('upwork_jobs.json', 'w') as f:
                json.dump(job_json, f, indent=4)
            print("[+] Job data saved to upwork_jobs.json")
        else:
            print("[-] No job data intercepted.")

    finally:
        driver.quit()

def main():
    login_upwork()

if __name__ == "__main__":
    main()
