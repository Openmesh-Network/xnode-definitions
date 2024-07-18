import json
from Formatting.enumerate_template_services import find_services_from_templates_without_definition

def runall(service_definitions_array):

    reduce_spec_overrides()
    service_definitions = make_definitions_from_scraper(service_definitions_array)
    #extra_services = find_services_from_templates_without_definition(make_definition_from_service)
    final_services = make_definition_from_templates(service_definitions, service_definitions_array)
    #print("Potential final services:", final_services)

    with open('service-definitions.json', 'w') as output:
        output.write(json.dumps(service_definitions, indent=4))


def make_definitions_from_scraper(nix_option_data):
    # Create the required definitions for the frontend to push to the backend to be read by the xnode
    with open('inputs/servicesWithOptions.json', 'r') as metadata:
        services_with_metadata = json.loads(metadata.read())['services']

    services_with_scraperdata = make_definitions(services_with_metadata, nix_option_data)
    return services_with_scraperdata

def make_definition_from_templates(starting_services, nix_option_data):
    # Create definitions for services which are in the templates
    with open('templates-16-7.json', 'r') as templatedata:
        services_from_templates = json.loads(templatedata.read())

    # Filter by existing service defs and add basic nix options for any existing in templates
    print("Total templates:", len(services_from_templates))
    extra_services = add_extra_definitions(starting_services, services_from_templates, nix_option_data)

    # need to fill in metadata for these extra services, such as specs, desc and tags
    return extra_services


def make_definition_from_service(service_names):
   print(service_names)

def populate_options(service, nix_option_data):
    new_service = {}
    new_service = service
    # Add nix option data
    for svc in nix_option_data:
        if svc['nixName'] == new_service['nixName']:
            new_service['options'] = svc['options']
            new_service['show'] = False # show: service and options have been checked and are supported in the frontend
            new_service['tested'] = False # tested: service and options have been tested and are supported on Xnode
            new_service.pop('implmented', None) # Removed old, mispelt field

    return new_service

def make_definitions(starting_services, nix_option_data):
    # Expects the weird format found in servicesWithOptions.json
    new_services = []

    with open('manual-spec-overrides.json', 'r') as specs:
        spec_overrides = json.loads(specs.read())

    accum = 0
    for service in starting_services:
        use_service = starting_services[service] # Start from services with options that are in the nix-scraper
        new_service = populate_options(use_service, nix_option_data)        

        # Add manual spec overrides   
        for svc in spec_overrides:
            if svc['nixName'] == use_service['nixName']:
                new_service['specs'] = svc['specs']

        # Manually check for undesired formatting
        backslash_in_name = False
        if '/' in new_service['name']:
            print(new_service['name'])
            backslash_in_name = True

        for option in new_service['options']:
            if '/' in option['name']:
                print(option['name'])
                backslash_in_name = True
        if not backslash_in_name:
            new_services.append(new_service)
            accum += 1
        else:
            continue
        
        # Write services to individual files
        write_to_definition_file(new_service)  

    print("Total services:",accum)
    print("Total potential services:", len(nix_option_data))
    return new_services

def write_to_definition_file(service):
    with open(f'definitions/{service["nixName"]}.json', 'w') as output:
            output.write(json.dumps(service, indent=4))    

def reduce_spec_overrides():
    with open('inputs/manual-spec-overrides.json', 'r') as specs:
        spec_overrides = json.loads(specs.read())

    reduced_spec_overrides = []
    for override in spec_overrides:
        new_override = {}
        new_override['nixName'] = override['nixName']
        new_override['specs'] = override['specs']
        if new_override not in reduced_spec_overrides:
            reduced_spec_overrides.append(new_override)

    with open('manual-spec-overrides.json', 'w') as output:
        output.write(json.dumps(reduced_spec_overrides, indent=4))

def add_extra_definitions(starting_services, extra_services, nix_data):
    # Find service data from nix option data, we can run 
    #print(starting_services)
    missing_services = []
    still_missing = []
    final_services_with_templates = 0

    for template in extra_services:
        # All templates
        for template_service in template['serviceNames']:
            # Services in template
            service_scraped = False
            for service in starting_services:
                if service['nixName'] == template_service:
                    service_scraped = True
                    final_services_with_templates += 1
                    break

            if template_service and not service_scraped:
                # Service was missing from starting services but existed in extra services
                found_missing = False
                for nix_service in nix_data:
                    if nix_service["nixName"] == template_service: #in template_service:
                        missing_services.append(nix_service)
                        write_to_definition_file(nix_service)
                        found_missing = True
                        final_services_with_templates += 1
                        
                    elif nix_service["nixName"] in template_service:
                        print("Found", nix_service["nixName"], "in", template_service)

                if not found_missing:
                    still_missing.append(template_service)

    print("Included extra services: ", len(missing_services))
    print("Unable to include services: ", len(still_missing), still_missing)
    
    final_services = starting_services.extend(missing_services)
    print("Total services which have templates: ", final_services_with_templates)

    return final_services