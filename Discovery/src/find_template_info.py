from Discovery.src.main import get_packages

def find_package_info(package_name):
    # Find info to populate template-definitions.json
    default_kwargs = {
        'package': package_name,
        'size': 1, 'begin': 0, 'channel': 'unstable', 'sort_by': '_score', 'sort_order': 'desc', 'package_set': None, 'license': None, 'maintainer': None, 
        'platform': None, 'info': False, 'options': False, 'output': '', 'debugging': False
    }
    result = get_packages(**default_kwargs)['hits']['hits']
    if len(result) > 0:
        closest_match = result[0]
        return closest_match["_source"]
    else:
        return None

def make_template_definition(closest_match_response):
    # Make template definition from closest_match_response
    template = {}
    nixName = closest_match_response.get('package_pname')
    template['name'] = nixName
    template['serviceNames'] = [nixName]
    if closest_match_response.get('package_longDescription'):
        template['desc'] = closest_match_response.get('package_longDescription')
    else:
        template['desc'] = closest_match_response.get('package_description')
    
    template['homepage'] = closest_match_response.get('package_homepage')
    return template

def make_templates(service_definitions):
    templates = []
    for service in service_definitions:
        package_info = find_package_info(service['nixName'])
        if package_info:
            template = make_template_definition(package_info)
            templates.append(template)
        else:
            print("Unable to find package info for", service["nixName"])

    return templates
