#!/usr/bin/env python3

import requests
import argparse
import json
from Discovery.src.request_builder import build_packages_request, build_options_request
from rich.tree import Tree
from rich.console import Console
from rich.spinner import Spinner

headers = {
    'Authorization': 'Basic YVdWU0FMWHBadjpYOGdQSG56TDUyd0ZFZWt1eHNmUTljU2g=',
    'Content-Type': 'application/json',
    'Referer': 'https://search.nixos.org/packages?',
}

def get_packages(**kwargs) -> dict:
    package_json_data = build_packages_request(**kwargs)
                
    response = requests.post(f'https://search.nixos.org/backend/latest-42-nixos-{kwargs["channel"]}/_search', headers=headers, json=package_json_data)

    return response.json()

def get_options(**kwargs) -> dict:
    option_json_data = build_options_request(**kwargs)

    response = requests.post(f'https://search.nixos.org/backend/latest-42-nixos-{kwargs["channel"]}/_search', headers=headers, json=option_json_data)

    return response.json()

def get_flakes() -> dict:
    # Placeholder for flakes feature
    pass

def check_sort_order(value):
    if value.lower() not in ['asc', 'desc']:
        raise argparse.ArgumentTypeError("Sort order must be 'asc' or 'desc'")
    return value.lower()

def start_up():
    sort_by_help_msg = """Field to sort by:
        _score - Rating of match between the query and the result.
        package_pname - Package name.
        package_pversion - Package version.
        package_attr_name - Attribute name of the package.
        package_maintainers - Package maintainers.
        package_license - Package license.
        package_description - Description of the package.
        package_homepage - Home page of the package.
        package_system - Target system (for example, x86_64-linux).
        package_platforms - Supported platforms.
        package_position - The position of the package in the repository.
        package_longDescription - Long description of the package.
        package_outputs - Package outputs (eg bin, lib).
        package_broken - The status of the package (for example, broken or not).
        package_insecure - Security status of the package.
        package_unfree - License status (for example, free or non-free).
    """

    parser = argparse.ArgumentParser(description="NixOS packages search", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("package", help="The package to search", type=str)
    parser.add_argument("--size", help="Number of results to return", type=int, default=50)
    parser.add_argument("--begin", help="Starting position of results", type=int, default=0)
    parser.add_argument("--channel", help="NixOS channel to search in", type=str, default="24.05")
    parser.add_argument("--sort-by", help=sort_by_help_msg, type=str, default="_score")
    parser.add_argument("--sort-order", help="Sort order (asc/desc)", type=check_sort_order, default="desc")
    parser.add_argument("--package-set", help="Filter by package set", type=str, default=None)
    parser.add_argument("--license", help="Filter by package license", type=str, default=None)
    parser.add_argument("--maintainer", help="Filter by package maintainer", type=str, default=None)
    parser.add_argument("--platform", help="Filter by platform", type=str, default=None)
    parser.add_argument("--info", help="Show detailed info about the package", action="store_true")
    parser.add_argument("--options", help="Show options of the package", action="store_true")
    parser.add_argument("--output", help="Output the hits to a file.", default='')
    parser.add_argument("--debugging", help="Write the api response to a response.json file for debugging.", action="store_true")
    args = parser.parse_args()
    
    return sort_by_help_msg, args

def main():
    sort_by_help_msg, args = start_up()
    
    console = Console()

    if args.options:
        kwargs = vars(args)

        with console.status("[bold green]Making request for options...", spinner="clock"):
            json_response = get_options(**kwargs)

        # If it hits any, write the response to json for debugging
        if args.debugging:
            with open('response.json', 'w') as f:
                f.write(json.dumps(json_response, indent=4))

        if (len(json_response.get('hits', {}).get('hits', [])) == 0):
            print(f"Error: Package \"{args.package}\" not found!")
            print(json_response)    

        # The output option will write the response's hits to a file
        hits = json_response['hits']
        if args.output != "":
            with open(args.output, 'w') as f:
                f.write(json.dumps(hits, indent=4))

        for package in json_response.get('hits', {}).get('hits', []):
            package_info = package.get('_source')

            tree = Tree(f"[green]Package name[/]: {package_info.get('option_name')}")
            tree.add(f"[blue]Description[/]: {package_info.get('option_description')}")
            tree.add(f"[blue]Type[/]: {package_info.get('option_type')}")
            tree.add(f"[blue]Default[/]: {package_info.get('option_default')}")
            #console.print(tree)
    else:

        if args.info:
            kwargs = {"package": args.package, "channel": args.channel}
            kwargs["begin"] = 0
            kwargs["size"] = 50
            kwargs["sort_by"] = "_score"
            kwargs["sort_order"] = "desc"

            with console.status("[bold green]Making request...", spinner="clock"):
                packages_response = get_packages(**kwargs) 
        
            if (len(packages_response.get('hits', {}).get('hits', [])) == 0):
                print(f"Error: Package \"{args.package}\" not found!")

            for package in packages_response.get('hits', {}).get('hits', []):
                package_info = package.get('_source', {})
                if package_info.get("package_pname") == args.package:
                    tree = Tree(f"[green]Package name[/]: {package_info.get('package_pname')}", guide_style="underline2")
                    tree.add(f"[blue]Description[/]: {package_info.get('package_description')}")
                    tree.add(f"[blue]Version[/]: {package_info.get('package_pversion')}")
                    mainteiners = ', '.join([f"{entry['name']}" for entry in package_info.get('package_maintainers')])
                    tree.add(f"[blue]Maintainers[/]: {mainteiners}")
                    licenses = '; '.join(f"{entry['fullName']}" for entry in package_info.get('package_license'))
                    tree.add(f"[blue]License[/]: {licenses}")
                    homepages = " ".join(package_info.get('package_homepage'))
                    tree.add(f"[blue]Homepage[/]: [steel_blue1 u]{homepages}")
                    tree.add(f"[blue]Supported Platforms[/]: {', '.join(package_info.get('package_platforms', []))}")
                    tree.add(f"[blue]Status[/]: {'[bright_red]Broken' if package_info.get('package_broken') else '[bright_green]OK'}")
                    tree.add(f"[blue]Security Status[/]: {'[bright_red]Insecure' if package_info.get('package_insecure') else '[bright_green]Secure'}")
                    programs = ', '.join(package_info.get('package_programs', []))
                    tree.add(f"[blue]Package programs[/]: {None if len(programs) == 0 else programs}")
                    tree.add(f"[blue]License Status[/]: {'[bright_yellow]Unfree' if package_info.get('package_unfree') else '[yellow3]Free'}")
                    tree.add(f"[blue]Long Description[/]: {package_info.get('package_longDescription')}")
                    tree.add(f"[blue]Outputs[/]: [bright_cyan]{', '.join(package_info.get('package_outputs'))}")
                    console.print(tree)
            if not tree:
                print(f"Error: Package \"{args.package}\" not found!")
        else:
            kwargs = vars(args)

            with console.status("[bold green]Making request...", spinner="clock"):
                json_response = get_packages(**kwargs)

            if args.debugging:
                with open('response.json', 'w') as f:
                    f.write(json.dumps(json_response, indent=4))

            if (len(json_response.get('hits', {}).get('hits', [])) == 0):
                print(f"Error: Package \"{args.package}\" not found!")    

            for package in json_response.get('hits', {}).get('hits', []):
                package_info = package.get('_source')

                tree = Tree(f"[green]Package name[/]: {package_info.get('package_pname')}")
                tree.add(f"[blue]Description[/]: {package_info.get('package_description')}")
                tree.add(f"[blue]Version[/]: {package_info.get('package_pversion')}")
                console.print(tree)
        
if __name__ == "__main__":
    main()