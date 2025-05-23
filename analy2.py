import json
from collections import defaultdict
import pandas as pd
import numpy as np
from operator import itemgetter
import statistics

# Load job data (replace with actual data from your file)
with open('merged_wed_night_summary.json', 'r') as file:
    job_data = json.load(file)

# Load clustering data from a JSON file
def load_clustering_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Analyze jobs and create clusters
def analyze_jobs(job_data, clustering_data):
    # Initialize a dictionary to store skills and their aggregated data
    skill_data = defaultdict(lambda: {
        "job_count": 0,
        "total_spent": 0,
        "total_reviews": 0,
        "hourly_budget_min": [],
        "hourly_budget_max": [],
        "payment_verified": 0,
        "total_applicants": 0,
        "duration": []
    })

    # Process each job listing
    for job in job_data:
        for skill in job["ontologySkills"]:
            skill_data[skill]["job_count"] += 1
            skill_data[skill]["total_spent"] += job["totalSpent"] or 0
            skill_data[skill]["total_reviews"] += job["totalReviews"] 
            if job["hourlyBudgetMin"] > 0:
                skill_data[skill]["hourly_budget_min"].append(job["hourlyBudgetMin"]) 
            if job["hourlyBudgetMax"] > 0:
                skill_data[skill]["hourly_budget_max"].append(job["hourlyBudgetMax"])
            skill_data[skill]["payment_verified"] += int(job["paymentVerificationStatus"] == "VERIFIED")
            skill_data[skill]["total_applicants"] += job["totalApplicants"] or 0
            duration_data = job["hourlyEngagementDuration"]
            if duration_data and isinstance(duration_data, dict):
                duration = duration_data["weeks"] or 0
                if duration > 0:
                    skill_data[skill]["duration"].append(duration)
            else:
                duration = 0
            

    # Prepare the final skills list
    final_skills = []
    for skill, data in skill_data.items():
        if data["job_count"] > 0:
            median_hourly_min = statistics.median(data["hourly_budget_min"]) if data["hourly_budget_min"] else 0
            median_hourly_max = statistics.median(data["hourly_budget_max"]) if data["hourly_budget_max"] else 0
            median_duration = statistics.median(data["duration"]) if data["duration"] else 0
            final_skills.append({
                "skill": skill,
                "job_count": data["job_count"],
                "pay_range": (median_hourly_min, median_hourly_max),
                "competition": data["total_applicants"],
                "payment_status": data["payment_verified"] / data["job_count"],
                # "duration": data["duration"] // data["job_count"] if data["job_count"] > 0 else 0,
                "duration" : median_duration,
                "client_spent": data["total_spent"]
            })

    # Sort skills based on criteria
    final_skills.sort(key=lambda x: (-x["job_count"], -x["pay_range"][1], x["competition"], -x["payment_status"], -x["duration"], -x["client_spent"]))

    # Get the top 30 skills
    # best_skills = final_skills[:30]

    # Create clusters based on clustering data
    # clusters = []
    # for specialty in clustering_data:
    #     cluster_skills = []
    #     for group in specialty["attributeGroups"]:
    #         for skill in group["attributes"]:
    #             if skill in skill_data:  # Check if the skill exists in the job data
    #                 cluster_skills.append(skill)

    #     # Aggregate data for the cluster
    #     if cluster_skills:
    #         total_jobs = sum(skill_data[skill]["job_count"] for skill in cluster_skills)
    #         total_spent = sum(skill_data[skill]["total_spent"] for skill in cluster_skills)
    #         # total_applicants = sum(skill_data[skill]["total_applicants"] for skill in cluster_skills)
    #         try:
    #             total_applicants = sum(skill_data[skill]["total_applicants"] for skill in cluster_skills)
    #         except KeyError as e:
    #             print(f"KeyError: {e} - Skill not found in skill_data")
    #         total_reviews = sum(skill_data[skill]["total_reviews"] for skill in cluster_skills)
    #         min_budget = min(skill_data[skill]["hourly_budget_min"] for skill in cluster_skills if skill_data[skill]["hourly_budget_min"])
    #         max_budget = max(skill_data[skill]["hourly_budget_max"] for skill in cluster_skills if skill_data[skill]["hourly_budget_max"])
    #         payment_verified = sum(skill_data[skill]["payment_verified"] for skill in cluster_skills) / total_jobs if total_jobs > 0 else 0
    #         avg_duration = sum(skill_data[skill]["duration"] for skill in cluster_skills) // total_jobs if total_jobs > 0 else 0

    #         clusters.append({
    #             "speciality": specialty["specialities"],
    #             "skills": cluster_skills,
    #             "job_count": total_jobs,
    #             "pay_range": (min_budget, max_budget),
    #             "competition": total_applicants,  # Total jobs as competition
    #             "payment_status": payment_verified,
    #             "duration": avg_duration,
    #             "client_spent": total_spent
    #         })


    # return best_skills, clusters, final_skills
    return final_skills

# Load clustering data from a JSON file
clustering_data_file_path = 'upwork_skills.json'  # Replace with your file path
clustering_data = load_clustering_data(clustering_data_file_path)

# Analyze the job data
# best_skills, clusters, final_skills = analyze_jobs(job_data, clustering_data)
final_skills = analyze_jobs(job_data, clustering_data)
# Print the results
# print("Top 30 Skills:")
# print(json.dumps(best_skills, indent=4))
df = pd.DataFrame(final_skills)
df.to_csv("./csv/Wed_night_all_skills.csv", index=False)
# df = pd.DataFrame(best_skills)
# df.to_csv("./csv/Thur_mor_best_skills.csv", index=False)

# print("\nSkill Clusters:")
# print(json.dumps(clusters, indent=4))
# df = pd.DataFrame(clusters)
# df.to_csv("./csv/Thur_mor_all_clusters.csv", index=False)
