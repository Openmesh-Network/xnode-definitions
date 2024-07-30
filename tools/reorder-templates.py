import json
import sys
import os

args = sys.argv
def reorder(starting_templates = args[1], output_templates = args[2]):
    if os.path.exists(starting_templates):
        with open(starting_templates, 'r') as json_in:
            templates = json.loads(json_in.read())

    total_templates = len(templates)
    current_index = 0
    new_templates = []
    missing_indexes = []

    while current_index < total_templates:
        this_index = current_index
        for template in templates:
            if template['id'] == str(current_index):
                new_templates.append(template)
                current_index += 1
                break
        if this_index < current_index:
            continue
        #print("Index not found:",current_index)
        missing_indexes.append(current_index)
        current_index += 1

    print(missing_indexes)
    with open(output_templates, 'w') as json_out:
        json_out.write(json.dumps(new_templates, indent=4))

reorder()