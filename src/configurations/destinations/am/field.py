# moving repeated fields from uiConfig.json to schema.json 
# uiConfig = baseTemplate arr + sdkTemplate obj 
# sdkTemplate.fields has arr
# baseTemplate has objects with a title
# Each baseTemplate object  -> sections arr -> groupsArr  -> fields arr
# and fields array has regex, regexErrorMessage, placeHolder, secret
# field types: 
#   textInput
#   tagInput
#   checkbox
#   singleSelect

# Class to represent repeated keys
class Field:
    def __init__(self, type , label, configKey, regex, regexErrorMessage, placeholder, secret):
        # data members (instance variables)
        self.type = type
        self.label = label
        self.configKey = configKey
        self.regex = regex
        self.regexErrorMessage = regexErrorMessage
        self.placeholder = placeholder
        self.secret = secret
    def __str__(self):
        return "type: " + self.type + ", label: " + self.label + ", configKey: " + self.configKey + " regex: " + self.regex + ", regexErrorMessage: " + self.regexErrorMessage + ", placeholder: " + self.placeholder + ", secret: " + str(self.secret)
def registerField(field, configKeyMap):
    if field['type'] == "textInput": 
        #print(json.dumps(field, indent=2))
        typeF,  labelF, configKeyF, regexF, regexErrorMessageF, placeholderF, secretF = "", "", "", "", "", "", False
        try: 
            typeF = field['type']
        except KeyError:
            pass
        try: 
            labelF = field['label']
        except KeyError: 
            pass
        try: 
            configKeyF = field['configKey']
        except KeyError: 
            pass
        try: 
            regexF = field['regex']
        except KeyError:
            pass
        try: 
            regexErrorMessageF = field['regexErrorMessage']
            # print("debug: ", regexErrorMessageF)
        except KeyError: 
            pass
        try: 
            placeholderF = field['placeholder']
        except KeyError: 
            pass
        try: 
            secretF = field['secret']
            if secretF == "": 
                secretF = False
        except KeyError:
            pass
        configKeyMap[configKeyF] = Field(typeF, labelF, configKeyF, regexF, regexErrorMessageF, placeholderF, secretF)
    elif field['type'] == "tagInput":
        #print(json.dumps(field, indent=2))
        labelF, configKeyF, placeholderF = "", "", ""
        try: 
            labelF = field['label']
        except KeyError:
            pass
        try:
            configKeyF = field['configKey'] 
        except KeyError:
            pass
        try: 
            placeholderF = field['placeholder']
        except KeyError:
            pass
        configKeyMap[configKeyF] = Field(field['type'], labelF, configKeyF, "", "", placeholderF, False)
        #print(configKeyMap[configKeyF].type)
    elif field['type'] == "checkbox":
        #print(json.dumps(field, indent=2))
        labelF, configKeyF, placeholderF = "", "", ""
        try: 
            labelF = field['label']
        except KeyError:
            pass
        try:
            configKeyF = field['configKey'] 
        except KeyError:
            pass
        try: 
            placeholderF = field['placeholder']
        except KeyError:
            pass
        configKeyMap[configKeyF] = Field(field['type'], labelF, configKeyF, "", "", placeholderF, False)
        #print(configKeyMap[configKeyF].type)
    elif field['type'] == "singleSelect":
        #print(json.dumps(field, indent=2))
        labelF, configKeyF, placeholderF = "", "", ""
        try: 
            labelF = field['label']
        except KeyError:
            pass
        try:
            configKeyF = field['configKey'] 
        except KeyError:
            pass
        try: 
            placeholderF = field['placeholder']
        except KeyError:
            pass
        configKeyMap[configKeyF] = Field(field['type'], labelF, configKeyF, "", "", placeholderF, False)
        #print(configKeyMap[configKeyF].type)
    elif field['type'] == "connectionMode":
       #print(json.dumps(field, indent=2))
        labelF, configKeyF, placeholderF = "", "", ""
        try: 
            labelF = field['label']
        except KeyError:
            pass
        try:
            configKeyF = field['configKey'] 
        except KeyError:
            pass
        try: 
            placeholderF = field['placeholder']
        except KeyError:
            pass
        configKeyMap[configKeyF] = Field(field['type'], labelF, configKeyF, "", "", placeholderF, False)
        #print(configKeyMap[configKeyF].type)
    else: 
        print("typeF", field['type'])
        print("field type not found")
