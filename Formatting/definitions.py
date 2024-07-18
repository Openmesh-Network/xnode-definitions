import json
from Formatting.options import get_options, get_service_options


def create_module_definitions(option_list):
    # For a list of options, return a list of modules with the same common top and second level name (eg. networking and firewall)
    # TODO: Add docstring ''' to show the data transformation that this is doing.
    modules = []
    module_definitions = []
    for option in option_list:
        option_split = option["nixName"].split('.')
        if len(option_split) <= 2:
            print(option_split)
            continue
        module_type = option_split[0]
        module_name = option_split[1]
        option_name = option["nixName"].replace(module_type + '.' + module_name + '.', '')
        option["nixName"] = option_name
        option["name"] = option_name

        if option['nixName'] == 'enable':
            option['value'] = 'true'

        if module_name in modules:
            for mod_def in module_definitions:
                if type(mod_def) is dict:
                    if mod_def["name"] == module_name:
                        mod_def["options"].append(option)
                else:
                    print(mod_def) # Unaccounted for, print pending options
            
        else:
            # Create new module with options list containing the option
            modules.append(module_name)
            mod_def = {
                "name": module_name,
                "nixName": module_name,
                "options":[option]
            }
            module_definitions.append(mod_def)
            
    return module_definitions

def make_service_definitions(write=True, write_path='Discovery/data/service-definitions.json'):
    # The goal for config_definitions is to create a list of modules with a good description typically pulled from the package info and an accurate options list.
    svc = get_service_options('Discovery/data/services')
    print(type(svc), len(svc))
    config_definitions = {
        "services": create_module_definitions(svc)
    }
    if write:
        write_json(config_definitions, write_path)

    return config_definitions

def write_json(config_definitions, path):
    try:
        with open(path, 'w') as file:
            file.write(json.dumps(config_definitions, indent=4))
    except Exception as e:
        print("Exeception:",e)


def make_other_definitions():
    module_types = ['boot', 'hardware', 'networking', 'programs', 'system', 'virtualisation', 'security', 'users.users']
    config_definitions = {}
    for m in module_types:
        module_path = f'data/other-modules/{m}.json'
        config_definitions[m] = create_module_definitions(get_options(module_path)) 

    # write_svc_defs(config_definitions, 'data/other-definitions.json')
    return config_definitions

#make_service_definitions()