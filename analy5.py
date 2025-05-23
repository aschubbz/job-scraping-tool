import json
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd

# Load job data and skill taxonomy
with open('merged_wed_mor_summary.json') as f:
    job_data = json.load(f)

with open('upwork_skills.json') as f:
    skill_taxonomy = json.load(f)

# Build skill-to-speciality/group mapping
skill_to_meta = {}
for entry in skill_taxonomy:
    speciality = entry['specialities']
    for group in entry['attributeGroups']:
        group_name = group['GroupName']
        for attr in group['attributes']:
            skill_to_meta[attr.lower()] = {
                'speciality': speciality,
                'group_name': group_name
            }

# Initialize aggregation per group
group_stats = defaultdict(lambda: {
    'group_name': '',
    'specialities': set(),
    'job_count': 0,
    'total_applicants': 0,
    'reviews': [],
    'duration_weeks': [],
    'total_spents': 0,
    'min_budget': [],
    'max_budget': []
})
data = []
labels = []

for job in job_data:
    job_skills = set(s.lower() for s in job.get('ontologySkills', []))
    title = job.get('title', '').lower()
    description = job.get('description', '').lower()
    all_text = f"{title}"

    # Match skills to groups
    for skill, meta in skill_to_meta.items():
        if skill in job_skills or skill in all_text:
            data.append(all_text)  # Use job text as input
            labels.append(meta['group_name'])

print("Finished make data and labels")

df = pd.DataFrame({'text': data, 'label': labels})

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

# Create a pipeline for vectorization and model training
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Train the model
model.fit(X_train, y_train)

print("Finished Train the model")

# Function to predict group name for a new job
def predict_group(job_title, job_description, job_skills):
    all_text = f"{job_title} {job_description} {' '.join(job_skills)}"
    predicted_group = model.predict([all_text])[0]
    return predicted_group

print("Starting process each job")
# Process each job
for job in job_data:
    job_skills = job.get('ontologySkills', [])
    all_text = (job.get('title', '') + ' ' + job.get('description', '')).lower()

    # matched_groups = set()

    # # Match by skill tags and text content
    # for skill, meta in skill_to_meta.items():
    #     if predict_group(job.get('title', ''), job.get('description', ''), job.get('ontologySkills', [])) == meta['group_name']:
    #     # if skill in [s.lower() for s in job_skills] or skill in all_text:
    #         group_id = meta['group_name']
    #         matched_groups.add(group_id)
    #         group_stats[group_id]['group_name'] = group_id
    #         group_stats[group_id]['specialities'].add(meta['speciality'])

    # # Update stats
    # for group_id in matched_groups:
    #     stats = group_stats[group_id]
    #     stats['job_count'] += 1
    #     stats['total_applicants'] += job.get('totalApplicants') or 0

    #     if job.get('totalFeedback', 0) > 0:
    #         stats['reviews'].append(job['totalReviews'])

    #     duration = (job.get('hourlyEngagementDuration') or {}).get('weeks', 0)
    #     if duration > 0:
    #         stats['duration_weeks'].append(duration)

    #     stats['total_spents'] += job.get('totalSpent') or 0

    #     min_budget = job.get('hourlyBudgetMin', 0)
    #     if min_budget > 0:
    #         stats['min_budget'].append(min_budget)

    #     max_budget = job.get('hourlyBudgetMax', 0)
    #     if max_budget > 0:
    #         stats['max_budget'].append(max_budget)
    
    predicted_group = predict_group(
        job.get('title', ''), 
        job.get('description', ''), 
        job.get('ontologySkills', [])
    )
    print("Finished one Prediction", predicted_group)
    # print("Skill To Meta", skill_to_meta)
    # matching_metas = [meta for meta in skill_to_meta.items() if meta['group_name'] == predicted_group]
    # matched_speciality = skill_to_meta.get(predicted_group)
    matched_speciality = ''
    for attr, meta in skill_to_meta.items():
        if meta['group_name'] == predicted_group:
            # matched_specialities.append(meta['speciality'])
            matched_speciality = meta['speciality']
    print("Matched Speciality", matched_speciality)
    # for meta in matching_metas:
    group_id = predicted_group
    group_stats[group_id]['group_name'] = group_id
    # group_stats[group_id]['specialities'].add(matched_speciality['speciality'])
    group_stats[group_id]['specialities'].add(matched_speciality)

    stats = group_stats[group_id]
    stats['job_count'] += 1
    stats['total_applicants'] += job.get('totalApplicants') or 0

    if job.get('totalFeedback', 0) > 0:
        stats['reviews'].append(job['totalFeedback'])

    duration = (job.get('hourlyEngagementDuration') or {}).get('weeks', 0)
    if duration > 0:
        stats['duration_weeks'].append(duration)

    stats['total_spents'] += job.get('totalSpent') or 0

    min_budget = job.get('hourlyBudgetMin', 0)
    if min_budget > 0:
        stats['min_budget'].append(min_budget)

    max_budget = job.get('hourlyBudgetMax', 0)
    if max_budget > 0:
        stats['max_budget'].append(max_budget)

    print("Length", len(group_stats))

print("Starting Convert sets to lists for JSON")
# Convert sets to lists for JSON serializability
final_results = []
# for stats in group_stats.values():
#     stats['specialities'] = list(stats['specialities'])
#     if stats['reviews']:
#         stats['average_reviews'] = sum(stats['reviews']) / len(stats['reviews'])
#     else:
#         stats['average_reviews'] = 0

#     # Update stats['duration_weeks'] to average value
#     if stats['duration_weeks']:
#         stats['average_duration_weeks'] = sum(stats['duration_weeks']) / len(stats['duration_weeks'])
#     else:
#         stats['average_duration_weeks'] = 0

#     # Update stats['min_budget'] to average value
#     if stats['min_budget']:
#         stats['average_min_budget'] = sum(stats['min_budget']) / len(stats['min_budget'])
#     else:
#         stats['average_min_budget'] = 0

#     # Update stats['max_budget'] to average value
#     if stats['max_budget']:
#         stats['average_max_budget'] = sum(stats['max_budget']) / len(stats['max_budget'])
#     else:
#         stats['average_max_budget'] = 0

#     # Convert specialities set to list for JSON serializability
#     stats['specialities'] = list(stats['specialities'])
#     final_results.append(stats)

for stats in group_stats.values():
    stats['specialities'] = list(stats['specialities'])
    if stats['reviews']:
        stats['average_reviews'] = sum(stats['reviews']) / len(stats['reviews'])
    else:
        stats['average_reviews'] = 0

    del stats['reviews']

    # Update stats['duration_weeks'] to average value
    if stats['duration_weeks']:
        stats['average_duration_weeks'] = sum(stats['duration_weeks']) / len(stats['duration_weeks'])
    else:
        stats['average_duration_weeks'] = 0
    del stats['duration_weeks']
    # Update stats['min_budget'] to average value
    if stats['min_budget']:
        stats['average_min_budget'] = sum(stats['min_budget']) / len(stats['min_budget'])
    else:
        stats['average_min_budget'] = 0
    del stats['min_budget']
    # Update stats['max_budget'] to average value
    if stats['max_budget']:
        stats['average_max_budget'] = sum(stats['max_budget']) / len(stats['max_budget'])
    else:
        stats['average_max_budget'] = 0
    del stats['max_budget']
    # Convert specialities set to list for JSON serializability
    stats['specialities'] = list(stats['specialities'])
    final_results.append(stats)

# final_results[:2]  # Show sample output
print(json.dumps(final_results, indent=4))
df = pd.DataFrame(final_results)
df.to_csv("./csv/wed_lunch_5_all_clusters.csv", index=False)

