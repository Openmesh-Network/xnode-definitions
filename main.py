import os
import argparse
import subprocess
import json

from Formatting import formatter, definitions, options
from Discovery.src.find_template_info import make_templates, xnode_definer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Whether to fetch brand new data from the NixOS search backend, this will find new options that were added since the last update.', action="store_true")
    parser.add_argument('-t','--templates',help='Whether to generate templates instead of service definitions.',action='store_true')
    args = parser.parse_args()

    services_directory = 'Discovery/data/services' # Directory with raw service responses from NixOS opensearch backend.

    # Check if data exists and if not download it
    if not raw_service_data_exists(services_directory):
        args.clean = True
        print("Data not found, clean fetch flag set to true")
    if args.clean:
        print("Fetching new data")
        # Find all services by searching for all lowercase letters, assumes that there are no letters for which over 10,000 services begin with.
        subprocess.run(['sh', 'Discovery/service-finder.sh']) # TODO: Parameterize all paths
        # Find all other options such as networking, boot or virtualization
        subprocess.run(['sh', 'Discovery/other-options.sh']) # TODO: Use extra nix options in the studio

    # Use collected opensearch responses to create definitions
    if raw_service_data_exists(services_directory):
        print("Making service definitions with nix data.")
        # Get the list of services in an array, nix options only.
        service_definitions = definitions.make_service_definitions()['services']
        if args.templates:
            templates = make_templates(service_definitions)
            with open('sample-template-output.json', 'w') as output:
                output.write(json.dumps(templates, indent=4))
        else:
            definition_factory = xnode_definer('inputs/manual-spec-overrides.json')
            # Make service definitions
            if args.clean or not package_info_data_exists():
                services = definition_factory.make_services(service_definitions, fetch_package_info=True)
            else:
                services = definition_factory.make_services(service_definitions)

            with open('sample-service-output.json', 'w') as output:
                output.write(json.dumps(services, indent=4))


def raw_service_data_exists(raw_services_responses):
    # Find if the dependent data exists
    all_data_exists = True
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        # TODO: Parameterize the path by services directory
        if not os.path.exists(f'{raw_services_responses}/{letter}.json'):
            all_data_exists = False

    if all_data_exists:
        return True
    else:
        return False 
    
def package_info_data_exists():
    return False
    if os.path.exists('Discovery/data/package-info.json'):
        return True
    else:
        return False

if __name__ == "__main__":
    main()