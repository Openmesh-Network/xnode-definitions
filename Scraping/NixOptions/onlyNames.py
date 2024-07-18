import json

with open('output.json', 'r') as file:
    data = file.read()
    jsondata = json.loads(data)

optionsTypes = []

for service in jsondata:
    
    optionsTypes.append(service["nixName"])

print(optionsTypes)
with open('onlyNames.txt', 'w') as file:
    file.write('\n'.join(optionsTypes))
