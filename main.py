import subprocess
import argparse

from Discovery.src import definitions
from Formatting import formatter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', help='Whether to fetch brand new data from the NixOS search backend.', action="store_true")

    args = parser.parse_args()

    if args.clean:
        # Find all services by searching for all lowercase letters, assumes that there are no letters for which over 10,000 services begin with.
        subprocess.run(['sh', 'Discovery/service-finder.sh'])
        # Find all other options such as networking, boot or virtualization
        #subprocess.run(['sh', 'Discovery/other-options.sh']) # TODO: Use these for something

    #formatter.runall()



if __name__ == "__main__":
    main()