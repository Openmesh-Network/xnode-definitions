import json

def main():
    make_definitions()
    reduce_spec_overrides()

def make_definitions():
    # This function creates the required definitions for the frontend to push to the backend to be read by the xnode
    new_services = []
    with open('nix-scraper/outputs/servicesWithOptions.json', 'r') as metadata:
        services_with_metadata = json.loads(metadata.read())['services']

    with open('Nix-Searcher/data/service-definitions.json', 'r') as nixdata:
        nix_option_data = json.loads(nixdata.read())['services']

    with open('manual-spec-overrides.json', 'r') as specs:
        spec_overrides = json.loads(specs.read())

    accum = 0
    for service in services_with_metadata:
        scraper_service = services_with_metadata[service]
        new_service = {}
        new_service = scraper_service
        # Add nix option data
        for svc in nix_option_data:
            if svc['nixName'] == scraper_service['nixName']:
                new_service['options'] = svc['options']
                new_service['show'] = False # show: service and options have been checked and are supported in the frontend
                new_service['tested'] = False # tested: service and options have been tested and are supported on Xnode
                new_service.pop('implmented', None) # Removed old, mispelt field

        # Add manual spec overrides   
        for svc in spec_overrides:
            if svc['nixName'] == scraper_service['nixName']:
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
        
        # Write services to individual files
        with open(f'definitions/{new_service["nixName"]}.json', 'w') as output:
            output.write(json.dumps(new_service, indent=4))      

    print("Total services:",accum)
    print("Total potential services:", len(nix_option_data))

    with open('service-definitions.json', 'w') as output:
        output.write(json.dumps(new_services, indent=4))

def reduce_spec_overrides():
    with open('manual-spec-overrides.json', 'r') as specs:
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

if __name__ == "__main__":
    main()