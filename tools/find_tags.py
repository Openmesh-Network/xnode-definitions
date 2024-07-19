import json
with open('../service-definitions.json', 'r') as services:
    services = json.loads(services.read())

tags = []
for serv in services:
    if 'tags' in serv.keys():
        for tag in serv['tags']:
            if tag not in tags:
                tags.append(tag)

print(tags)