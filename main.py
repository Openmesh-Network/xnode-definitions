import json

def main():
    new_services = []
    with open('nix-scraper/outputs/servicesWithOptions.json', 'r') as metadata:
        with open('Nix-Searcher/data/service-definitions.json', 'r') as nixdata:
            #print(metadata)
            accum =0
            services_with_metadata = json.loads(metadata.read())['services']
            nix_option_data = json.loads(nixdata.read())['services']
            for service in services_with_metadata:
                scraper_service = services_with_metadata[service]
                new_service = {}
                new_service = scraper_service
                for svc in nix_option_data:
                    if svc['nixName'] == scraper_service['nixName']:
                        new_service['options'] = svc['options']
                        new_services.append(new_service)
                        accum += 1

            print(accum)

    with open('output.json', 'w') as output:
        output.write(json.dumps(new_services, indent=4))

if __name__ == "__main__":
    main()