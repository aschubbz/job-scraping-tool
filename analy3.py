import json
from collections import defaultdict
import statistics
import pandas as pd

# Load job data
with open('merged_wed_mor_summary.json', 'r') as file:
    job_data = json.load(file)

# Load clustering data
def load_clustering_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Create clusters based on job data
def create_clusters_from_jobs(job_data, clustering_data):
    # Initialize clusters dictionary
    clusters = defaultdict(lambda: {
        "job_count": 0,
        "total_spent": 0,
        "total_reviews": 0,
        "hourly_budget_min": [],
        "hourly_budget_max": [],
        "payment_verified": 0,
        "total_applicants": 0,
        "duration": 0,
        "skills": []
    })

    # Iterate over job data
    for job in job_data:
        title = job.get("title", "")
        description = job.get("description", "")
        skills = job.get("ontologySkills", [])

        # Determine matching clusters based on skills
        for specialty in clustering_data:
            for group in specialty["attributeGroups"]:
                for skill in group["attributes"]:
                    if skill in skills:
                        # Aggregate data for the matching cluster
                        cluster_name = specialty["specialities"]
                        clusters[cluster_name]["job_count"] += 1
                        clusters[cluster_name]["total_spent"] += job.get("totalSpent", 0)
                        clusters[cluster_name]["total_reviews"] += job.get("totalReviews", 0)
                        clusters[cluster_name]["hourly_budget_min"].append(job.get("hourlyBudgetMin", 0))
                        clusters[cluster_name]["hourly_budget_max"].append(job.get("hourlyBudgetMax", 0))
                        clusters[cluster_name]["payment_verified"] += int(job.get("paymentVerificationStatus") == "VERIFIED")
                        clusters[cluster_name]["total_applicants"] += job.get("totalApplicants") or 0

                        # Calculate duration
                        duration_data = job.get("hourlyEngagementDuration", {})
                        duration = duration_data.get("weeks", 0) if isinstance(duration_data, dict) else 0
                        clusters[cluster_name]["duration"] += duration

                        # Track skills for the cluster
                        if skill not in clusters[cluster_name]["skills"]:
                            clusters[cluster_name]["skills"].append(skill)

    # Convert clusters dictionary to a list for easier handling
    final_clusters = []
    for cluster_name, data in clusters.items():
        if data["job_count"] > 0:
            min_budget = min(data["hourly_budget_min"]) if data["hourly_budget_min"] else 0
            max_budget = max(data["hourly_budget_max"]) if data["hourly_budget_max"] else 0
            avg_duration = data["duration"] // data["job_count"] if data["job_count"] > 0 else 0
            payment_status = data["payment_verified"] / data["job_count"] if data["job_count"] > 0 else 0

            final_clusters.append({
                "speciality": cluster_name,
                "job_count": data["job_count"],
                "pay_range": (min_budget, max_budget),
                "competition": data["total_applicants"],
                "payment_status": payment_status,
                "duration": avg_duration,
                "client_spent": data["total_spent"],
                "skills": data["skills"]
            })

    return final_clusters

# Load clustering data
clustering_data_file_path = 'upwork_skills.json'  # Replace with your file path
clustering_data = load_clustering_data(clustering_data_file_path)

# Create clusters from job data
clusters = create_clusters_from_jobs(job_data, clustering_data)

# Print the resulting clusters
print(json.dumps(clusters, indent=4))
df = pd.DataFrame(clusters)
df.to_csv("./csv/wed_mor_1_all_clusters.csv", index=False)
