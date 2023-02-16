import json

# from jinja2 import Environment, PackageLoader, select_autoescape
# env = Environment(
#     loader=PackageLoader("templates"),
#     autoescape=select_autoescape()
# )

with open('ui-config.json', 'r') as uiconfig: 
    uiconfig = json.load(uiconfig)

from field import registerField

configKeyMap = dict()
baseTemplate = uiconfig['uiConfig']['baseTemplate']
for baseTempObj in baseTemplate: 
    for section in baseTempObj['sections']:
        for group in section['groups']:
            for field in group['fields']:
                registerField(field, configKeyMap)

sdkFields = uiconfig['uiConfig']['sdkTemplate']['fields']
for field in sdkFields:
   registerField(field, configKeyMap)

#===============================================================================#

with open('schema.json', 'r') as schema:
    schema = json.load(schema)

schemaProps = schema['configSchema']['properties']
for property in schemaProps: 
    if property in configKeyMap:
        if schemaProps[property]['type'] != "array": 
            # print(configKeyMap[property])
            schemaProps[property]['regex'] = configKeyMap[property].regex
            schemaProps[property]['label'] = configKeyMap[property].label
            schemaProps[property]['regexErrorMessage'] = configKeyMap[property].regexErrorMessage
            schemaProps[property]['placeholder'] = configKeyMap[property].placeholder
            schemaProps[property]['secret'] = configKeyMap[property].secret
        else: 
            try: 
                schemaProps[property]['items']['properties']['traits']['label'] = configKeyMap[property].label
            except KeyError:    
                schemaProps[property]['items']['properties']['eventName']['label'] = configKeyMap[property].label
            try:
                schemaProps[property]['items']['properties']['traits']['placeholder'] = configKeyMap[property].placeholder
            except KeyError: 
                schemaProps[property]['items']['properties']['eventName']['placeholder'] = configKeyMap[property].placeholder


schema['configSchema']['properties'] = schemaProps
with open('schema_modified.json', 'w') as schema_modified:
    schema = json.dump(schema, schema_modified, indent=2)
print(json.dumps(schema, indent=2))
