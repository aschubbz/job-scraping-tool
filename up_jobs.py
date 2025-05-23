import time
import json
import requests
from seleniumbase import SB

# User credentials and target URL
UPWORK_EMAIL = 'kevinbruyne0125@outlook.com'
UPWORK_PASSWORD = 'Mymother081*'
TARGET_URL = 'https://www.upwork.com/nx/search/jobs/?amount=1000-4999,5000-&category2_uid=531770282580668420,531770282584862722,531770282580668419,531770282580668422,531770282580668418&contractor_tier=2,3&duration_v3=month,semester,ongoing&location=United%2520States&nbs=1&payment_verified=1&per_page=50&proposals=0-4,5-9,10-14,15-19&sort=recency&t=0,1'
# TARGET_URL = 'https://www.upwork.com/nx/search/jobs/?category2_uid=531770282580668420,531770282580668419,531770282580668418&contractor_tier=2,3&duration_v3=month,semester,ongoing&location=United%2520States&nbs=1&payment_verified=1&sort=recency'
API_URL = "https://www.upwork.com/api/graphql/v1?alias=userJobSearch"
ALL_JOBS = []
# def extract_network_traffic(logs):
#     for entry in logs:
#         try:
#             message = json.loads(entry["message"])["message"]
#             method = message.get("method")
#             params = message.get("params", {})

#             if method == "Network.requestWillBeSent":
#                 request = params.get("request", {})
#                 url = request.get("url", "")
#                 if API_URL == url:
#                     print(f"Request → {request['method']} {url}")
#                     headers = request.get("headers", {})
#                     if request.get("postData"):
#                         print(f"  Payload: {request['postData'][:300]}")

#             elif method == "Network.responseReceived":
#                 response = params.get("response", {})
#                 url = response.get("url", "")
#                 if "upwork" in url:
#                     print(f"Response ← {response['status']} {url}")
#                     print(f"  Content-Type: {response['headers'].get('content-type', '')}")

#         except Exception as e:
#             print(f"Error parsing log entry: {e}")

def extract_network_responses(logs, target_url, driver):
    request_ids = {}

    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
            method = message.get("method")
            params = message.get("params", {})

            if method == "Network.requestWillBeSent":
                request = params.get("request", {})
                url = request.get("url", "")
                if target_url in url:
                    request_id = params.get("requestId")
                    request_ids[request_id] = url

            elif method == "Network.responseReceived":
                response = params.get("preview", {})
                request_id = params.get("requestId")
                url = response.get("url", "")
                if request_id in request_ids:
                    # print("Answer", response)
                    # print(f"Response ← {preview['status']} {url}")
                    # Try to get response body via CDP (not guaranteed to work in all cases)
                    try:
                        body = driver.execute_cdp_cmd(
                            "Network.getResponseBody",
                            {"requestId": request_id}
                        )
                        if body:
                            preview = body.get("body", "")
                            return preview
                    except Exception as e:
                        print(f"  Could not retrieve response body: {e}")

        except Exception as e:
            print(f"Error parsing log entry: {e}")

def filter_job_data(total_jobs):
    filtered_jobs = []

    for job in total_jobs:
        total_spent = job.get("upworkHistoryData", {}).get("client", {}).get("totalSpent")
        total_spent_amount = total_spent['amount'] if total_spent else "0"
        filtered_job = {
            "id": job.get("id", ""),
            "title": job.get("title", ""),
            "description": job.get("description", ""),
            "ontologySkills": [skill.get("prettyName", "") for skill in job.get("ontologySkills", [])],
            "connectPrice": job.get("connectPrice", 0),
            "paymentVerificationStatus": job.get("upworkHistoryData", {}).get("client", {}).get("paymentVerificationStatus", ""),
            "totalReviews": job.get("upworkHistoryData", {}).get("client", {}).get("totalReviews", 0),
            "totalFeedback": job.get("upworkHistoryData", {}).get("client", {}).get("totalFeedback", 0.0),
            # "totalSpent": job.get("upworkHistoryData", {}).get("client", {}).get("totalSpent", {}).get("amount", "0"),
            "totalSpent" : float(total_spent_amount or 0),
            "jobType": job.get("jobTile", {}).get("job", {}).get("jobType", ""),
            "hourlyBudgetMax": float(job.get("jobTile", {}).get("job", {}).get("hourlyBudgetMax", 0) or 0),
            "hourlyBudgetMin": float(job.get("jobTile", {}).get("job", {}).get("hourlyBudgetMin", 0) or 0),
            "hourlyEngagementType": job.get("jobTile", {}).get("job", {}).get("hourlyEngagementType", ""),
            "contractorTier": job.get("jobTile", {}).get("job", {}).get("contractorTier", ""),
            "sourcingTimestamp": job.get("jobTile", {}).get("job", {}).get("sourcingTimestamp", ""),
            "createTime": job.get("jobTile", {}).get("job", {}).get("createTime", ""),
            "publishTime": job.get("jobTile", {}).get("job", {}).get("publishTime", ""),
            "enterpriseJob": job.get("jobTile", {}).get("job", {}).get("enterpriseJob", False),
            "personsToHire": job.get("jobTile", {}).get("job", {}).get("personsToHire", 0),
            "premium": job.get("jobTile", {}).get("job", {}).get("premium", False),
            "totalApplicants": job.get("jobTile", {}).get("job", {}).get("totalApplicants", 0),
            "hourlyEngagementDuration": job.get("jobTile", {}).get("job", {}).get("hourlyEngagementDuration", {}),
            "fixedPriceAmount": job.get("jobTile", {}).get("job", {}).get("fixedPriceAmount", 0)
        }
        filtered_jobs.append(filtered_job)
    return filtered_jobs

def login_upwork():
    with SB(uc=True, headless=False, log_cdp=True) as sb:
        sb.open('https://www.upwork.com/ab/account-security/login')
        time.sleep(3)

        # Type email and press continue
        sb.wait_for_element_clickable('input#login_username')  # Wait for the email field to be visible
        sb.type('input#login_username', UPWORK_EMAIL)  # Type email
        
        sb.wait_for_element_clickable('button#login_password_continue')  # Wait for continue button to be clickable
        sb.click('button#login_password_continue')  # Click continue
        time.sleep(3)  # Wait for the next step to load
        
        # Click on the CAPTCHA to bypass it
        sb.uc_gui_click_captcha()

        # Type password and press login
        sb.wait_for_element_clickable('input#login_password')  # Wait for the password field to be visible
        sb.type('input#login_password', UPWORK_PASSWORD)  # Type password
        
        sb.wait_for_element_clickable('button#login_control_continue')  # Wait for login button to be clickable
        sb.click('button#login_control_continue')  # Click login
        
        time.sleep(3)
        sb.wait_for_element_visible('img.nav-avatar.nav-user-avatar')
        # time.sleep(3)  # Wait for login to complete
        # sb.go_to("https://www.upwork.com/freelancers/~015dd2504c66f34983")
        # sb.uc_gui_click_captcha()
        time.sleep(10)
        # sb.wait_for_element_visible('img.nav-avatar.nav-user-avatar')
        # sb.go_to(TARGET_URL)
        # sb.uc_gui_click_captcha()
        time.sleep(3)
        
        all_jobs = []

        while True:
            try:
                sb.wait_for_element_visible('//button[@data-test="next-page"]')
                sb.wait_for_element_clickable('//button[@data-test="next-page"]')
                # Click the next button
                sb.click('//button[@data-test="next-page"]')
                time.sleep(3)
                responses = extract_network_responses(sb.driver.get_log("performance"), API_URL, sb.driver)
                if isinstance(responses, str):
                    try:
                        responses = json.loads(responses)
                        print("REsponses", responses)  # Convert JSON string to a dictionary
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        responses = {}  # Handle the error case
                total_jobs = responses.get("data", {}).get("search", {}).get("universalSearchNuxt", {}).get("userJobSearchV1", {}).get("results", {})
                all_jobs.extend(filter_job_data(total_jobs))

                with open('upwork_wed_night_jobs.json', 'w') as json_file:
                    json.dump(all_jobs, json_file, indent=4)
            except Exception as e:
                print("No more pages or error occurred:", e)
                break

def main():
    login_upwork()

if __name__ == "__main__":
    main()
