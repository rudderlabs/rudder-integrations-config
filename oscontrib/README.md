# Contributing to RudderStack

Thanks for taking the time for contributing to this project!

## How you can contribute a destination to this project

To contribute a destination, you need to provide all the required data for all the fields you want as the settings to configure the destination.

## How you can provide your destination connection setting details

You can checkout the sample input file [**here**](https://github.com/rudderlabs/rudder-integrations-config/blob/config-generator-script/test/configData/inputData.json):

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
