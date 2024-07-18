import json
import re
import html

def remove_html_tags(text):
    # Function needs to be improved
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    # Convert HTML entities to characters
    clean_text = html.unescape(clean_text)
    clean_text = clean_text.replace('\n', '')
    return clean_text.strip(' ')


def parse_option(hit):
    option = {
        "name": hit["_source"]["option_source"],
        "desc": remove_html_tags(hit["_source"]["option_description"]),
        "nixName": hit["_source"]["option_name"],
        "type": hit["_source"]["option_type"],
        "value": hit["_source"]["option_default"]
    }
    return option

def get_service_options():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    service_options_list = []
    # Collect all service options
    for letter in letters:
        path = f'data/services/{letter}.json'
        options_for_letter = get_options(path)
        service_options_list.append(options_for_letter)
    # List of lists for each letter, transform into single list
    service_options_list = [item for sublist in service_options_list for item in sublist]
    write_svc_opts(service_options_list)

    return service_options_list

def get_options(search_data_path):
    options_list = []
    with open(search_data_path, 'r') as file:
            data = json.load(file)
    if data['hits']:
        for hit in data['hits']['hits']:
            option = parse_option(hit)
            options_list.append(option)
    return options_list

def write_svc_opts(svc_opts_list):
    with open('data/service-options.json', 'w') as file:
        file.write(json.dumps(svc_opts_list, indent=4))