import json

def alter_opts_manually(opt):
    if opt['nixName'] == 'motd':
        opt['value'] = "Minecraft Server running on \u00A7dXnode"
        opt['type'] = "string"
    return opt

with open('inputs/raw-minecraft-source.txt', 'r') as raw_minecraft_source:
    minecraft_source = raw_minecraft_source.read()

minecraft_output = minecraft_source.replace("|", " ").strip().replace("|-", "")
minecraft_output = minecraft_output.splitlines()

current_option = {}
options = []
for line in minecraft_output:
    line.strip()
    if 'id="' in line:
        if 'nixName' in current_option.keys():
            options.append(current_option)
            current_option = {}
        name = line.split('id="')[1].split('"')[0]
        current_option['name'] = name
        if "." in name:
            name = '"' + name + '"'
        current_option['nixName'] = name
    #elif "'''" in line:
    #    continue
        #print("continuing", line)
    
    elif ('boolean' in line) or 'integer' in line or 'string' in line:
        current_option['type'] = line
        #print(current_option.keys())
    elif ('nixName' in current_option.keys()) and ('type' in current_option.keys()) and not ('value' in current_option.keys()):
        current_option['value'] = line
        if "''blank''" in current_option["value"]:
            current_option['value'] = ""

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
    elif opt["desc"] == "":
        print("NO DESC",opt)  
    else:
        for val in opt:
            opt[val] = opt[val].strip()
        opt = alter_opts_manually(opt)
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