import json

with open('outputs/output.json', 'r') as file:
    data = file.read()
    jsondata = json.loads(data)

optionsTypes = []

for service in jsondata:
    for opts in service["options"]:
        if opts["type"] not in optionsTypes:
            optionsTypes.append(opts["type"])

# print(optionsTypes)
with open('outputs/optionTypes.txt', 'w') as file:
    file.write('\n'.join(optionsTypes))
print("Wrote output to outputs/optionTypes.txt")
