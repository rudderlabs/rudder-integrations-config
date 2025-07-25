# Contributing to Rudder-Integrations-Config

Thanks for taking the time and for your help in improving this project!

## Table of contents

- [**RudderStack Contributor Agreement**](#rudderstack-contributor-agreement)
- [**UI Configuration Development Requirements**](#ui-configuration-development-requirements)
- [**How you can contribute to RudderStack**](#how-you-can-contribute-to-rudderstack)
- [**Committing**](#committing)
- [**Getting help**](#getting-help)

## RudderStack Contributor Agreement

To contribute to this project, we need you to sign the [**Contributor License Agreement ("CLA")**][CLA] for the first commit you make. By agreeing to the [**CLA**][CLA], we can add you to list of approved contributors and review the changes proposed by you.

## UI Configuration Development Requirements

### **UI Configuration Structure**

**Important**: All new `ui-config.json` files must follow the required structure.

#### **What Each Element Means**

- **`baseTemplate`**: The main configuration sections that users will see and interact with
- **`sections`**: Groups of related settings (like connection settings, configuration settings)
- **`groups`**: Visual containers that organize fields within a section
- **`fields`**: Individual form inputs that users fill out
- **`sdkTemplate`**: Settings specific to web SDK integration (hidden from UI)
- **`consentSettingsTemplate`**: Consent management configuration (hidden from UI)

#### **Required Structure**

```json
{
  "uiConfig": {
    "baseTemplate": [
      {
        "title": "Initial setup",
        "note": "Review how this destination is set up",
        "sections": [
          {
            "groups": [
              {
                "title": "Connection settings",
                "icon": "settings",
                "fields": [
                  // Your form fields here
                ]
              }
            ]
          }
        ]
      }
    ],
    "sdkTemplate": {
      "title": "Web SDK settings",
      "note": "not visible in the ui",
      "fields": []
    },
    "consentSettingsTemplate": {
      "title": "Consent settings",
      "note": "not visible in the ui",
      "fields": []
    }
  }
}
```

#### **Field Properties Explained**

- **`type`**: Determines the input field type (textInput, checkbox, singleSelect, etc.)
- **`label`**: The text displayed above the field
- **`configKey`**: The key used to store the field value in the database
- **`required`**: Whether the field must be filled out
- **`secret`**: Whether the field value should be hidden (like passwords)
- **`placeholder`**: Hint text shown inside the field
- **`regex`**: Validation pattern for the field value
- **`options`**: Available choices for select fields

#### **Field Type Examples**

```json
{
  "type": "textInput",
  "label": "API Key",
  "configKey": "apiKey",
  "required": true,
  "secret": true
}
```

#### **Examples**

See `src/configurations/destinations/http/ui-config.json` for a complete example.

**Reference**: For a comprehensive example, see `src/configurations/destinations/fullstory/ui-config.json`.

## How you can contribute a destination to this project

To contribute a destination, you need to provide all the required data for all the fields you want as the settings to configure the destination.

## How you can provide your destination connection setting details

You can checkout the sample input file [**here**](/test/configData/inputData.json):

For the above input data, the UI will look like as shown below:

<img width="1303" alt="connectionSettings" src="https://github.com/rudderlabs/rudder-integrations-config/assets/63387036/ee28b3fe-5a81-4289-9f6a-54cf5abe0f4c">
<img width="1292" alt="configurationSettings" src="https://github.com/rudderlabs/rudder-integrations-config/assets/63387036/ce765f0f-b680-46ca-b46d-ed58e39a7667">

In the input file, you need to provide the destination name you want to display in the UI in the displayName field.

Each json object inside the formFields represents a field you want to add as a connection/configuration settings to the destination.

Description of Keys inside each JSON object:

| Property      | Description                                                                            |
| ------------- | -------------------------------------------------------------------------------------- |
| type          | This is the input field type you want to add                                           |
| label         | This is the display name for your field                                                |
| configKey     | This is the key to which the value for this field will be stored in the db             |
| required      | You can provide true as a value to make this field as required or false                |
| placeholder   | This is the the placeholder for this field                                             |
| secret        | You can provide true as a value to make this field as secret or false                  |
| preRequisites | You can add the configKey and value if you there is a preRequiste field for this field |

The input field types that you can add are:

| type         | Description                                                               |
| ------------ | ------------------------------------------------------------------------- |
| textInput    | This is a simple field for adding text inputs                             |
| checkbox     | This is used for boolean values (true or false)                           |
| singleSelect | This is used for choosing one of the option from a set of defined options |
| multiSelect  | This is used for choosing multiple options from a set of defined options  |
| tagInput     | This can be used to add multiple text inputs for a field                  |

You can also contribute to any open-source RudderStack project. View our [**GitHub page**](https://github.com/rudderlabs) to see all the different projects.

## Getting help

For any questions, concerns, or queries, you can start by asking a question in our [**Slack**](https://rudderstack.com/join-rudderstack-slack-community/) community.


<!----variables---->

[issue]: https://github.com/rudderlabs/rudder-config-schema/issues/new
[CLA]: https://forms.gle/845JRGVZaC6kPZy68
