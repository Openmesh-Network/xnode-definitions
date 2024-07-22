import json
from xnode_admin.utils import parse_nix_json

with open('inputs/option-overrides.json', 'r') as option_overrides:
    options=json.loads(option_overrides.read())

xnode_admin_output = parse_nix_json(options)
print(xnode_admin_output)