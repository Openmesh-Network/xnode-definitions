import json

def main():
    new_services = []
    with open('nix-scraper/outputs/servicesWithOptions.json', 'r') as metadata:
        with open('Nix-Searcher/data/service-definitions.json', 'r') as nixdata:
            accum = 0
            services_with_metadata = json.loads(metadata.read())['services']
            nix_option_data = json.loads(nixdata.read())['services']


            for service in services_with_metadata:
                scraper_service = services_with_metadata[service]
                new_service = {}
                new_service = scraper_service
                accum += 1
                for svc in nix_option_data:
                    if svc['nixName'] == scraper_service['nixName']:
                        new_service['options'] = svc['options']
                        new_service['show'] = False # show: service and options have been checked and are supported in the frontend
                        new_service['tested'] = False # tested: service and options have been tested and are supported on Xnode
                        new_service.pop('implmented', None) # Removed old, mispelt field
                        new_services.append(new_service)
                        

            print("Total services:",accum)
            print("Total potential services:", len(nix_option_data))

    with open('service-definitions.json', 'w') as output:
        output.write(json.dumps(new_services, indent=4))

if __name__ == "__main__":
    main()