<p align="center">
  <a href="https://rudderstack.com/">
    <img src="https://user-images.githubusercontent.com/59817155/121357083-1c571300-c94f-11eb-8cc7-ce6df13855c9.png">
  </a>
</p>

<p align="center"><b>The Customer Data Platform for Developers</b></p>

<p align="center">
  <b>
    <a href="https://rudderstack.com">Website</a>
    ·
    <a href="">Documentation</a>
    ·
    <a href="https://rudderstack.com/join-rudderstack-slack-community">Community Slack</a>
  </b>
</p>

---

[![codecov](https://codecov.io/gh/rudderlabs/rudder-integrations-config/branch/develop/graph/badge.svg?token=K75QABOWUT)](https://codecov.io/gh/rudderlabs/rudder-integrations-config)

# \*\*rudder-config-schema\*\*

\*\*Repo description\*\*

## Overview

\*\*Describe what the software does.\*\*

## Features

\*\*Describe the key features, if necessary.\*\*

## Getting started

You need to install Python3.

And then, setup the project dependencies by running below command:

`npm run setup`

### Generated UI Configs For Destinations Supporting Custom Mappings

As there are significant default values for ui-config.json for destinations supporting custom mappings, we use templating mechanism to manage it. Make sure to run `npm run pre-process` to make sure you have the updated `generated ui-config.json` for such destinations the default values for these are maintained in `ui-default.json` under same dir.

`ui-config.jt` is the template file used to produce the `ui-config.json` we use the [rudder-json-template-engine
](https://github.com/rudderlabs/rudder-json-template-engine) for it.

The below command deploys integration definitions to the specified control-plane database:

```
python3 ./scripts/deployToDB.py --help

usage: deployToDB.py [-h] [control_plane_url] [username] [password]

Script to deploy config files to DB.

positional arguments:
  control_plane_url  Control plane URL
  username           Control plane admin username
  password           Control plane admin password

options:
  -h, --help         show this help message and exit
```

#### Positional argument environment variable fallback table

| Positional Argument | Fallback Environment Variable | Description           |
| ------------------- | ----------------------------- | --------------------- |
| ARG1                | CONTROL_PLANE_URL             | The control plane URL |
| ARG2                | API_USER                      | The cp admin          |
| ARG3                | API_PASSWORD                  | The cp admin password |

### Usage examples

```
# Just command line args
python3 ./scripts/deployToDB.py http://localhost:5050 foo bar

# Some command line some envs
API_USER=foo API_PASSWORD=bar python3 ./scripts/deployToDB.py http://localhost:5050

# Just envs
CONTROL_PLANE_URL=http://foo.bar API_USER=foo API_PASSWORD=bar python3 ./scripts/deployToDB.py
```

## Contribute

We would love to see you contribute to RudderStack. Get more information on how to contribute [**here**](CONTRIBUTING.md).
