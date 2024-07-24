import os
import argparse
import subprocess
import json

from Formatting import formatter, definitions
from Discovery.src.find_template_info import make_templates, xnode_definer, override_options, override_tags
from Discovery.src.NixPackageMetaData import NixMetaScraper

def program_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Whether to fetch brand new data from the NixOS search backend, this will find new options that were added since the last update.', action="store_true")
    parser.add_argument('-p', '--packages', help='Whether to generate service descriptions and info from package info.', action="store_true")
    parser.add_argument('-t','--templates',help='Whether to generate templates instead of service definitions.',action='store_true')
    parser.add_argument('-ow', '--overwrite', help='Whether to overwrite existing definitions in the definitions directory.', action="store_true")
    parser.add_argument('-es', '--backend', help='The elastic search host on the NixOS search backend as a url.', type=str, default="https://search.nixos.org/backend/")
    parser.add_argument('-k','--key',help="The backend api key for NixOS Search", type=str, default="YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g=")
    return parser.parse_args()
    
def main():
    args = program_args()
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
            print("Making template definitions using package data.")

            templates = make_templates(service_definitions)
            with open('sample-template-output.json', 'w') as output:
                output.write(json.dumps(templates, indent=4))
                
        else:
            print("Making service definitions using package data.")

            definition_factory = xnode_definer('inputs/manual-spec-overrides.json')
            # Make service definitions using package information on NixOS Search
            if args.clean or args.packages or not package_info_data_exists():
                services = definition_factory.make_services(service_definitions, fetch_package_info=True)
            else:
                services = definition_factory.make_services(service_definitions)

            # Use nix scraper to find metadata
            scraper = NixMetaScraper(args.backend)
            services_with_metadata = scraper.find_metadata(services)
            
            # Apply manual field overrides such as specs and tag retention
            final_services = apply_overrides(services_with_metadata)

            # Write output to definitions directory and sample-services
            if args.overwrite:
                write_definitions(final_services, overwrite=True)
            else:
                write_definitions(final_services)
    else:
        print("Unable to find service data.")


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
    # XXX: Doesn't check for existence of package-info directory and data inside.
    if os.path.exists('Discovery/data/package-info.json'):
        return True
    else:
        return False

def write_definitions(services, overwrite=False, template_defs='inputs/manual-templates.json'):
    # Write output to definitions directory and the sample file.
    with open('sample-service-output.json', 'w') as output:
        output.write(json.dumps(services, indent=4))

    if overwrite:
        # Find what services to include
        services_in_templates = []
        with open(template_defs, 'r') as template_definitions:
            # Only include what is in the templates
            templates = json.load(template_definitions)
            for template in templates:
                services_in_templates.extend(template['serviceNames'])
        # Write only those that are included in existing templates
        for service in services:
            if service["nixName"] in services_in_templates:
                formatter.write_to_definition_file(service)

            elif os.path.exists(f'definitions/{service["nixName"]}.json'):
                # Otherwise delete the definition file
                os.remove(f'definitions/{service["nixName"]}.json')
    else:
        # Write all to definitions directory
        for service in services:
            formatter.write_to_definition_file(service)

def apply_overrides(services):
    # Add option overrides
    with open('inputs/option-overrides.json', 'r') as option_overrides:
        extra_options=json.loads(option_overrides.read())
    options_applied = override_options(services, extra_options)

    # Add tag overrides (from remnant servicesWithOptions)
    # TODO: Integrate scraping module to regain this functionality in a more general way
    with open('inputs/servicesWithOptions.json', 'r') as servicesWithOptions:
        scraped_services = json.loads(servicesWithOptions.read())['services']
    final_services = override_tags(options_applied, scraped_services)
    return final_services

if __name__ == "__main__":
    main()