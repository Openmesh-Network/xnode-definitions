import os
import argparse
import subprocess

from Formatting import formatter, definitions, options


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Whether to fetch brand new data from the NixOS search backend, this will find new options that were added since the last update.', action="store_true")
    args = parser.parse_args()

    # Check if data exists and if not download it
    if not data_exists():
        args.clean = True
    if args.clean:
        # Find all services by searching for all lowercase letters, assumes that there are no letters for which over 10,000 services begin with.
        subprocess.run(['sh', 'Discovery/service-finder.sh']) # TODO: Parameterize the paths
        # Find all other options such as networking, boot or virtualization
        subprocess.run(['sh', 'Discovery/other-options.sh']) # TODO: Use extra nix options in the studio

    # Use collected opensearch responses to create definitions
    if data_exists():
        # Get the list of services in an array
        service_definitions = definitions.make_service_definitions()['services']

        print(service_definitions)
    #formatter.runall()


def data_exists():
    # Find if the dependent data exists
    if os.path.exists('Discovery/data/services/a.json'): # and os.path.exists(...):
        return True
    else:
        return False 
    

if __name__ == "__main__":
    main()