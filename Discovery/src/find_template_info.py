from Discovery.src.main import get_packages
from Discovery.src.metadata_scraper import build_query
from Formatting.formatter import remove_html_tags
import json

class xnode_definer:
    def __init__(self, path_to_spec_overrides):
        with open(path_to_spec_overrides, 'r') as specs:
            self.spec_overrides = json.loads(specs.read())

    def find_spec_overrides(self, nixName):
        # Add manual spec overrides
        for svc in self.spec_overrides:
            if svc['nixName'] == nixName and svc['specs']:
                return svc['specs']
        return {
            "ram":0,
            "storage":0
        }

    def make_services(self, service_definitions, fetch_package_info=False):
        services = []
        for service in service_definitions:
            # Fetch_package_info indicates that we want to call find_package_info, otherwise we look for local data
            if fetch_package_info:
                package_info = find_package_info(service['nixName'])
                if package_info:
                    new_service = self.extend_service_definition(package_info, service)
                    services.append(new_service)

                    # Write the response package-info directory
                    with open(f'Discovery/data/package-info/{service["nixName"]}.json', 'w') as output:
                        output.write(json.dumps(package_info, indent=4))
                else:
                    print("Unable to find package info for", service["nixName"])
                    
            # Load the package info from local data.
            else:
                try:
                    with open(f'Discovery/data/package-info/{service["nixName"]}.json', 'r') as package_info:
                        package_info = json.loads(package_info.read())

                        if package_info:
                            new_service = self.extend_service_definition(package_info, service)
                            services.append(new_service)

                except Exception as e:
                    # Plenty of these
                    print("Exception:", e)

        if fetch_package_info:
            with open('Discovery/data/package-info.json', 'w') as output:
                output.write(json.dumps(services, indent=4))

        return services

    def extend_service_definition(self, closest_match_response, service_definition):
        # Make template definition from closest_match_response
        package_name = closest_match_response.get('package_pname')
        if closest_match_response.get('package_longDescription'):
            service_description = closest_match_response.get('package_longDescription')
        else:
            service_description = closest_match_response.get('package_description')

        nixName = service_definition['nixName']

        new_service_definition = {
            'name': package_name,
            'desc': filter_desc(service_description),
            'nixName': nixName,
            'specs': self.find_spec_overrides(nixName),
            'tags': generate_tags_from_desc(service_description),
            'website': closest_match_response.get('package_homepage')[0],
            'logo': '',
            'options': service_definition['options']
        }

        return new_service_definition

def find_package_info(package_name):
    # Find info to populate template-definitions.json
    default_kwargs = {
        'package': package_name,
        'size': 50, 'begin': 0, 'channel': 'unstable', 'sort_by': '_score', 'sort_order': 'desc', 'package_set': None, 'license': None, 'maintainer': None, 
        'platform': None, 'info': False, 'options': False, 'output': '', 'debugging': False
    }
    # TODO: Increase size of query and compare responses for similarity with search_term (might be able to do this in the opensearch query)
    result = get_packages(**default_kwargs)['hits']['hits']
    if len(result) > 0 and package_name in result[0]['_source']['package_pname']:
        print(package_name, len(result))
        for hit in result:
            #print(hit["_source"].get("package_pname"))
            outputs = hit["_source"].get("package_outputs")
            for output in outputs:
                if package_name in output:
                    print("Found", output, "in program outputs")
                    return hit["_source"]
                
        closest_match = result[0]
        return closest_match["_source"] # XXX: Not always getting a correct match
    else:
        return None

def find_package_info_scraper(service_name):
    request = build_query(service_name)

def make_template_definition(closest_match_response):
    # Make template definition from closest_match_response
    template = {}
    package_name = closest_match_response.get('package_pname')
    template['name'] = package_name
    if closest_match_response.get('package_longDescription'):
        template['desc'] = closest_match_response.get('package_longDescription')
    else:
        template['desc'] = closest_match_response.get('package_description')
    
    return template


def make_templates(service_definitions):
    templates = []
    for service in service_definitions:
        package_info = find_package_info(service['nixName'])
        if package_info:
            template = make_template_definition(package_info)
            template['serviceNames'] = [service['nixName']]
            templates.append(template)
        else:
            print("Unable to find package info for", service["nixName"])

    return templates

def generate_tags_from_desc(desc) -> list:
    # Find tags that are in the description
    if desc is None:
        return []

    # Hardcoded selection of keywords
    possible_tags = ['Communication - Custom Communication Systems', 'Analytics', 'Automation', 'Monitoring', 'File Transfer & Synchronization', 'Communication - Email - Mail Delivery Agents', 'Communication - Social Networks and Forums', 'Communication - Video Conferencing', 'Backup', 'File Transfer - Distributed Filesystems', 'File Transfer - Object Storage & File Servers', 'File Transfer - Peer-to-peer Filesharing', 'Media Streaming - Audio Streaming\r', 'Media Streaming - Multimedia Streaming', 'Media Streaming - Video Streaming', 'Proxy', 'Remote Access\r', 'Search Engines\r', 'Software Development - Continuous Integration & Continuous Deployment', 'Software Development - IDE & Tools\r', 'Software Development - Project Management\r', 'Ticketing\r', 'Video Surveillance\r', 'VPN', 'Web Servers', 'Game', 'Server', 'Proprietary', 'Administration', 'Access-control', 'AI', 'LLM', 'GPU', 'Open-source', 'Web Application']
    generated_tags = []

    for tag in possible_tags:
        if tag in desc:
            generated_tags.append(tag)

    # with open('inputs/tag-keywords.json', 'r') as tag_keywords:
    #     keywords = json.loads(tag_keywords.read())
    # XXX: This might be a good application of LLMs, to fill in the tags.

    return generated_tags
    
def override_options(services, overrides):
    new_services = []
    for service in services:
        found_override = False
        for override in overrides:
            # Find service corresponding to the override
            if service['nixName'] == override['nixName']:
                found_override = True
                override_service = update_options(override, service)               

        # Append all services back to the output
        if found_override:
            new_services.append(override_service)
        else:
            new_services.append(service)

    return new_services

def update_options(override, service):
    # Find options already in the service (should be all possible options)
    for option in override['options']:
        found_in_service = False
        for existing_option in service['options']:
            if option['nixName'] == existing_option['nixName']:
                found_in_service = True
                if 'value' in option.keys():
                    existing_option['value'] = option['value']
                elif 'options' in option.keys():
                    existing_option['options'] = option['options']
        if not found_in_service:
            # Append to array if the option isn't found in the service
            service['options'].append(option)
            
    return service

def override_tags(options_applied, scraped_services):
    new_services = []
    for service in options_applied:
        nix_name = service['nixName']
        if nix_name in scraped_services.keys():
            scraped_service = scraped_services[nix_name]
            if service['name'] != scraped_service['name']:
                print("Changing name from", service['name'], "to", scraped_service['name'])
            service['name'] = scraped_service['name']
            service['tags'].extend(scraped_service['tags'])
            service['logo'] = scraped_service['logo']
        new_services.append(service)

    return new_services

def filter_desc(desc):
    if desc is None:
        return ''
    else:
        return remove_html_tags(desc)