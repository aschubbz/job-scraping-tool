import time
import json
import requests
from seleniumbase import SB

# User credentials and target URL
UPWORK_EMAIL = 'kevinbruyne0125@outlook.com'
UPWORK_PASSWORD = 'Mymother081*'
TARGET_URL = 'https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668420,531770282584862722,531770282580668419,531770282580668422,531770282580668418&contractor_tier=2,3&duration_v3=month,semester,ongoing&location=United%2520States&nbs=1&payment_verified=1&per_page=50&proposals=0-4,5-9,10-14,15-19&sort=recency&t=0,1&page=1'
API_URL = "https://www.upwork.com/api/graphql/v1?alias=userJobSearch"

def login_upwork():
    with SB(uc=True, headless=False, log_cdp=True) as sb:
        sb.open('https://www.upwork.com/ab/account-security/login')
        time.sleep(5)

        # Type email and press continue
        sb.wait_for_element_clickable('input#login_username')  # Wait for the email field to be visible
        sb.type('input#login_username', UPWORK_EMAIL)  # Type email
        
        sb.wait_for_element_clickable('button#login_password_continue')  # Wait for continue button to be clickable
        sb.click('button#login_password_continue')  # Click continue
        time.sleep(6)  # Wait for the next step to load
        
        # Click on the CAPTCHA to bypass it
        sb.uc_gui_click_captcha()

        # Type password and press login
        sb.wait_for_element_clickable('input#login_password')  # Wait for the password field to be visible
        sb.type('input#login_password', UPWORK_PASSWORD)  # Type password
        
        sb.wait_for_element_clickable('button#login_control_continue')  # Wait for login button to be clickable
        sb.click('button#login_control_continue')  # Click login
        sb.wait_for_element_visible('img.nav-avatar.nav-user-avatar')
        time.sleep(10)  # Wait for login to complete
        sb.go_to(TARGET_URL)
        time.sleep(5)
        sb.wait_for_element_visible('//button[@data-test="next-page"]')
        sb.wait_for_element_clickable('//button[@data-test="next-page"]')
        # Click the next button
        sb.click('//button[@data-test="next-page"]')
        time.sleep(6) 
        all_jobs = []
        # while True:
        # job_data = fetch_jobs(API_URL)

        # for req in sb.driver.requests:
        #     if req.response and API_URL in req.url:  # Check if the response exists and if the URL matches
        #         print(
        #             f"{req.method:<6} {req.url}  "
        #             f"{req.response.status_code}  "
        #             f"{req.response.headers.get('Content-Type', '')}"
        #         )
        
        # print("-----------API DATA-----------", job_data)
        # with open('upwork_jobs.json', 'w') as json_file:
        #     json.dump(job_data, json_file, indent=4)

# def fetch_jobs(api_url):
#     try:
#         response = requests.get(api_url)
#         response.raise_for_status()  # Raises an error for bad responses (4xx and 5xx)
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching jobs: {e}")
#         return None  # or handle the error as needed

def main():
    login_upwork()
    
    # with SB(uc=True) as sb:
    #     sb.open(TARGET_URL)
    #     time.sleep(5) 

        # Uncomment and modify the following block as needed to fetch jobs
        # all_jobs = []
        # while True:
        #     api_url = "https://www.upwork.com/api/graphql/v1?alias=userJobSearch"
        #     job_data = fetch_jobs(api_url)
        #     all_jobs.extend(job_data['data']['searchJobs']['results'])  # Adjust based on actual API response structure

        #     try:
        #         next_button = sb.find_element((By.XPATH, '//button[@data-test="next-page"]'))
        #         next_button.click()
        #         time.sleep(5)  # Wait for the next page to load
        #     except Exception as e:
        #         print("No more pages or an error occurred:", e)
        #         break

        # Save the data to a JSON file
        # with open('upwork_jobs.json', 'w') as json_file:
        #     json.dump(all_jobs, json_file, indent=4)

if __name__ == "__main__":
    main()
