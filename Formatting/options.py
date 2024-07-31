import json
import re
import html
from Formatting.formatter import remove_html_tags

def parse_option(hit):
    option = {
        "name": hit["_source"]["option_source"],
        "desc": remove_html_tags(hit["_source"]["option_description"]),
        "nixName": hit["_source"]["option_name"],
        "type": hit["_source"]["option_type"],
        "value": hit["_source"]["option_default"]
    }
    return option

def get_service_options(services_directory):
    # Assumes the services directory will contain json files for each letter.
    letters = 'abcdefghijklmnopqrstuvwxyz'
    service_options_list = []
    # Collect all service options
    for letter in letters:
        path = f'{services_directory}/{letter}.json'
        options_for_letter = get_options(path)
        if options_for_letter is not None:
            service_options_list.append(options_for_letter)
        else:
            print("Unable to find services for letter", letter)
    # List of lists for each letter, transform into single list
    service_options = [item for sublist in service_options_list for item in sublist]
    write_svc_opts(service_options)

    return service_options

def get_options(search_data_path):
    # Takes in search data, ie the raw response to a NixOS search query (opensearch response)
    options_list = []
    try:
        with open(search_data_path, 'r') as file:
                data = json.load(file)
    except Exception as e:
        print("Exeception:",e)
        return None
    if data['hits']:
        for hit in data['hits']:
            option = parse_option(hit)
            options_list.append(option)
    return options_list

def write_svc_opts(svc_opts_list, write_path='Discovery/data/service-options.json'):
    with open(write_path, 'w') as file:
        file.write(json.dumps(svc_opts_list, indent=4))