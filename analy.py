import json
from collections import defaultdict
import numpy as np
import pandas as pd
from operator import itemgetter

# Load your JSON data
with open('upwork_tue_lunch_jobs.json', 'r') as file:
    jobs = json.load(file)

# Initialize skill aggregation
skill_stats = defaultdict(lambda: {
    "job_count": 0,
    "min_hourly_rates": [],
    "max_hourly_rates": [],
    "applicants": [],
    "verified_count": 0,
    "durations": [],
    "client_spent": []
})

# Aggregate stats per skill
for job in jobs:
    skills = job.get("ontologySkills", [])
    min_rate = job.get("hourlyBudgetMin") or 0
    max_rate = job.get("hourlyBudgetMax") or 0
    applicants = job.get("totalApplicants") or 0
    is_verified = job.get("paymentVerificationStatus") == "VERIFIED"
    # duration = job.get("hourlyEngagementDuration", {}).get("weeks") or 0
    duration_data = job.get("hourlyEngagementDuration")
    if duration_data and isinstance(duration_data, dict):
        duration = duration_data.get("weeks") or 0
    else:
        duration = 0
    spent = job.get("totalSpent") or 0

    for skill in skills:
        skill_stats[skill]["job_count"] += 1
        if min_rate > 0: skill_stats[skill]["min_hourly_rates"].append(min_rate)
        if max_rate > 0: skill_stats[skill]["max_hourly_rates"].append(max_rate)
        skill_stats[skill]["applicants"].append(applicants)
        if is_verified: skill_stats[skill]["verified_count"] += 1
        skill_stats[skill]["durations"].append(duration)
        skill_stats[skill]["client_spent"].append(spent)

# Compute aggregate metrics
skills_summary = []

for skill, stats in skill_stats.items():
    job_count = stats["job_count"]
    avg_min_rate = np.median(stats["min_hourly_rates"]) if stats["min_hourly_rates"] else 0
    avg_max_rate = np.median(stats["max_hourly_rates"]) if stats["max_hourly_rates"] else 0
    avg_applicants = np.mean(stats["applicants"])
    verified_ratio = stats["verified_count"] / job_count
    avg_duration = np.mean(stats["durations"])
    avg_spent = np.mean(stats["client_spent"])

    skills_summary.append({
        "skill": skill,
        "job_count": job_count,
        "avg_min_rate": round(avg_min_rate, 2),
        "avg_max_rate": round(avg_max_rate, 2),
        "avg_applicants": round(avg_applicants, 2),
        "verified_ratio": round(verified_ratio, 2),
        "avg_duration_weeks": round(avg_duration, 2),
        "avg_spent": round(avg_spent, 2)
    })

# Sort by priority: job_count, pay, applicants, verified, duration, spent
skills_summary.sort(
    key=lambda x: (
        -x["job_count"],
        -(x["avg_min_rate"] + x["avg_max_rate"])/2,
        x["avg_applicants"],
        -x["verified_ratio"],
        -x["avg_duration_weeks"],
        -x["avg_spent"]
    )
)

# Output best 30 skills
top_30 = skills_summary[:30]

# Save to CSV or print
df = pd.DataFrame(skills_summary)
df.to_csv("all_skills.csv", index=False)
print(df)

# Explanation for inclusion
print("\nExplanation for top 30 skills:")
for skill in top_30:
    print(f"{skill['skill']}: {skill['job_count']} jobs, ${skill['avg_min_rate']}-{skill['avg_max_rate']}/hr, {skill['avg_applicants']} applicants avg, {int(skill['verified_ratio']*100)}% verified, {skill['avg_duration_weeks']} weeks avg duration, ${skill['avg_spent']} avg spent")
