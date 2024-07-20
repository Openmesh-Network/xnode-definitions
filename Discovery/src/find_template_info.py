from Discovery.src.main import get_packages
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
        return []

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

            else:
                try:
                    with open(f'Discovery/data/package-info/{service["nixName"]}.json', 'r') as package_info:
                        package_info = json.loads(package_info.read())
                        if package_info:
                            new_service = self.extend_service_definition(package_info, service)
                            services.append(new_service)
                except Exception as e:
                    print("ERROR:", e)

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
            'desc': service_description,
            'nixName': nixName,
            'specs': self.find_spec_overrides(nixName),
            'tags': generate_tags_from_desc(service_description),
            'website': closest_match_response.get('package_homepage'),
            'options': service_definition['options']
        }

        return new_service_definition

def find_package_info(package_name):
    # Find info to populate template-definitions.json
    default_kwargs = {
        'package': package_name,
        'size': 1, 'begin': 0, 'channel': 'unstable', 'sort_by': '_score', 'sort_order': 'desc', 'package_set': None, 'license': None, 'maintainer': None, 
        'platform': None, 'info': False, 'options': False, 'output': '', 'debugging': False
    }
    # TODO: Increase size of query and compare responses for similarity with search_term (might be able to do this in the opensearch query)
    result = get_packages(**default_kwargs)['hits']['hits']
    if len(result) > 0:
        closest_match = result[0]
        return closest_match["_source"] # XXX: Not always getting a correct match
    else:
        return None

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

    return generated_tags
    
