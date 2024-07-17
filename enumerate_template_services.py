import json

def find_services_from_templates_without_definition(callback_function):
    with open('templates-16-7.json', 'r') as templates:
        template_defs = json.loads(templates.read())

    with open('service-definitions.json', 'r') as services:
        all_services = json.loads(services.read())

    for template in template_defs:
        found_service = False
        for template_service in template['serviceNames']:
            if len(template_service) > 0 and template_service != None:
                for service in all_services:
                    if template_service == service['nixName']:
                        found_service = True
                        break
        if not found_service:
            callback_function(template['serviceNames'])

