import json

def reformat_data(data):
    # Initialize an empty list for the final output
    final_output = []

    for item in data:
        occupation = item['ontologyAttributeGroupsForOccupation']['occupation']
        specialities = occupation['preferredLabel']

        # Prepare the attributeGroups list
        attribute_groups = []

        for group in item['ontologyAttributeGroupsForOccupation']['attributeGroups']:
            group_name = group['preferredLabel']
            group_id = group['id']

            # Find matching skills for this group
            attributes = []
            for attribute in item['ontologyAttributeGroupsForOccupation']['attributes']:
                if attribute['attribute'] == group_id:
                    attributes = [skill['preferredLabel'] for skill in attribute['skills']]
                    break

            # Append the group information to the attribute_groups list
            attribute_groups.append({
                'GroupName': group_name,
                'attributes': attributes
            })

        # Construct the final object for this occupation
        final_object = {
            'specialities': specialities,
            'attributeGroups': attribute_groups
        }

        # Add the final object to the output list
        final_output.append(final_object)

    return final_output

# Load the JSON data
with open('skills.json', 'r') as file:
    data = json.load(file)

# Reformat the data
formatted_data = reformat_data(data)

# Print the result
with open('upwork_skills.json', 'w') as json_file:
    json.dump(formatted_data, json_file, indent=4)
# print(json.dumps(formatted_data, indent=4))