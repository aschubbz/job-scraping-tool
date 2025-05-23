import json
import os

def merge_json_files(file_list, output_file):
    merged_jobs = {}

    for file_name in file_list:
        with open(file_name, 'r') as file:
            data = json.load(file)
            print(f"Processing {file_name}: {len(data)} jobs found.")
            for job in data:
                job_id = job.get("id")
                if job_id in merged_jobs:
                    # Update existing job with new data
                    merged_jobs[job_id].update(job)
                else:
                    # Add new job
                    merged_jobs[job_id] = job

    # Convert merged_jobs dictionary back to a list
    merged_jobs_list = list(merged_jobs.values())

    # Save to output file
    with open(output_file, 'w') as outfile:
        json.dump(merged_jobs_list, outfile, indent=4)
    print(f"Total merged jobs: {len(merged_jobs_list)}")
# List of JSON files to merge
json_files = [
    "merged_wed_mor_summary.json",
    # "summary_mon_lunch.json",
    # "summary_mon_night.json",
    "upwork_wed_night_jobs.json",
    # Add more files as needed
]

# Output file name
output_file_name = "merged_wed_night_summary.json"

# Call the merge function
merge_json_files(json_files, output_file_name)

print(f"Merged JSON files into {output_file_name}")
