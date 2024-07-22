import json

with open('inputs/raw-minecraft-source.txt', 'r') as raw_minecraft_source:
    minecraft_source = raw_minecraft_source.read()

minecraft_output = minecraft_source.replace("| ", "").strip().replace("|-", "")
minecraft_output = minecraft_output.splitlines()

current_option = {}
options = []
for line in minecraft_output:
    if 'id="' in line:
        if 'nixName' in current_option.keys():
            options.append(current_option)
            current_option = {}
        current_option['nixName'] = line.split('id="')[1].split('"')[0]
    elif "'''" in line:
        print("continuing", line)
    
    elif ('boolean' in line) or 'integer' in line or 'string' in line:
        current_option['type'] = line
        print(current_option.keys())
    elif ('nixName' in current_option.keys()) and ('type' in current_option.keys()) and not ('value' in current_option.keys()):
        current_option['value'] = line

    elif ('nixName' in current_option.keys()) and ('type' in current_option.keys()) and ('value' in current_option.keys()):
        if 'desc' in current_option.keys():
            current_option['desc'] += line
        else:
            current_option['desc'] = line

    elif "{{more info needed}}" in line:
        current_option['type'] = 'undetermined'

final_options = []
for opt in options:
    if "undetermined" in opt['type']:
        print("REMOVED",opt)
    else:
        final_options.append(opt)
        
types = []
for opt in final_options:
    types.append(opt['type'])

with open('inputs/option-overrides.json', 'r') as option_overrides:
    overrides_json = json.loads(option_overrides.read())
    for override in overrides_json:
        if override['nixName'] == 'minecraft-server':
            for server_option in override['options']:
                if server_option['nixName'] == 'serverProperties':
                    server_option['options'] = final_options

with open('inputs/option-overrides.json', 'w') as option_overrides:
    option_overrides.write(json.dumps(overrides_json, indent=4))