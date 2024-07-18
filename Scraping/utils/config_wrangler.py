import json

services = {}
with open("outputs/output.json", "r") as file:
    services = json.load(file)

withOptions = 0
noOptions = []
servicesWithOptions = {"services":{}}
for service in services:
    if service["options"]:
        withOptions += 1
        for opt in service["options"]:
            unexpectedName, unexpectedOption = None, None

            # Fix nixName to be the correct syntax (originally was a nixpkgs path)
            expectedPrefix = "services." + service["nixName"] + "."
            nixpkgsPath = opt["nixName"]
            if opt["name"].startswith(expectedPrefix):
                opt["nixName"] = opt["name"].split(expectedPrefix)[1]
            elif opt["name"].startswith("services."):
                opt["nixName"] = "relatedOption." + opt["name"].split("services.")[1]
            else:
                opt["nixName"] = opt["name"]
                unexpectedOption = opt["name"]

            # Fix name to be category/serviceName (originally was the nixName)
            if nixpkgsPath.startswith("nixos/modules/services/"):
                opt["name"] = nixpkgsPath.split("nixos/modules/services/")[1]
            else:
                unexpectedName = nixpkgsPath
            
            if unexpectedName or unexpectedOption:
                print("Unresolved option not expected for", service["nixName"])
                print(unexpectedName, unexpectedOption)

        servicesWithOptions["services"][service["nixName"]] = service
    else:
        noOptions.append(service["nixName"])

print(len(services), "total services in input")
print(withOptions, "services with options")

# Add curated services
with open("data/curated_services.json", "r") as file:
    curated_services = json.load(file)
    for service in curated_services:
        servicesWithOptions["services"][service["name"]] = service

# Format json
formatted_json = json.dumps(servicesWithOptions, indent=4)

# Write to output
with open("outputs/servicesWithOptions.json", "w") as file:
   file.write(formatted_json)

# Record services from output.json that do not have any options (investigation required)
noOpts = ''
for i in noOptions:
    noOpts += i + '\n'

with open("outputs/noOptions.txt", "w") as file:
    file.write(noOpts)