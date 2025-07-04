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

The below commands deploy integration definitions and account configurations to the specified control-plane database:

## Deploy Integration Definitions

```
python3 ./scripts/deployToDB.py --help

usage: deployToDB.py [-h] [--dry-run] [--verbose] [control_plane_url] [username] [password] [selector] [item_name]

Script to deploy config files to DB.

positional arguments:
  control_plane_url  Control plane URL
  username           Control plane admin username
  password           Control plane admin password
  selector           Specify (destination or source) to deploy corresponding definitions.
  item_name          Specific item name to update.

options:
  -h, --help         show this help message and exit
  --dry-run          Show what would be changed without making actual changes to the database
  --verbose          Show detailed JSON reports in addition to summary
```

## Deploy Account Configurations

```
python3 ./scripts/deployAccountsToDB.py --help

usage: deployAccountsToDB.py [-h] [--dry-run] [--verbose] [control_plane_url] [username] [password] [definition_name]

Script to deploy account configurations to DB.

positional arguments:
  control_plane_url  Control plane URL
  username           Control plane admin username
  password           Control plane admin password
  definition_name    Specific item name to update.

options:
  -h, --help         show this help message and exit
  --dry-run          Show what would be changed without making actual changes to the database
  --verbose          Show detailed JSON reports in addition to summary
```

#### Positional argument environment variable fallback table

| Positional Argument | Fallback Environment Variable | Description           |
| ------------------- | ----------------------------- | --------------------- |
| ARG1                | CONTROL_PLANE_URL             | The control plane URL |
| ARG2                | API_USER                      | The cp admin          |
| ARG3                | API_PASSWORD                  | The cp admin password |

### Usage examples

#### Integration Definitions (deployToDB.py)

```bash
# Just command line args
python3 ./scripts/deployToDB.py http://localhost:5050 foo bar

# Some command line some envs
API_USER=foo API_PASSWORD=bar python3 ./scripts/deployToDB.py http://localhost:5050

# Just envs
CONTROL_PLANE_URL=http://foo.bar API_USER=foo API_PASSWORD=bar python3 ./scripts/deployToDB.py
```

#### Account Configurations (deployAccountsToDB.py)

```bash
# Deploy all account configurations
python3 ./scripts/deployAccountsToDB.py http://localhost:5050 admin password123

# Deploy specific account configuration
python3 ./scripts/deployAccountsToDB.py http://localhost:5050 admin password123 AMPLITUDE_ACCOUNT

# Using environment variables
CONTROL_PLANE_URL=http://localhost:5050 API_USER=admin API_PASSWORD=password123 python3 ./scripts/deployAccountsToDB.py

# Dry run for all accounts
python3 ./scripts/deployAccountsToDB.py http://localhost:5050 admin password123 --dry-run

# Dry run with verbose output
python3 ./scripts/deployAccountsToDB.py http://localhost:5050 admin password123 --dry-run --verbose
```

### Dry Run Mode

Both `deployToDB.py` and `deployAccountsToDB.py` scripts support a dry run mode that allows you to preview what changes would be made to the database without actually performing any modifications.

#### Dry Run Usage Examples

**Integration Definitions (deployToDB.py):**
```bash
# Dry run for all destinations (summary only)
python3 ./scripts/deployToDB.py https://api.example.com admin password123 destination --dry-run

# Dry run with detailed JSON reports
python3 ./scripts/deployToDB.py https://api.example.com admin password123 destination --dry-run --verbose

# Dry run for a specific item
python3 ./scripts/deployToDB.py https://api.example.com admin password123 source AMPLITUDE --dry-run

# Using environment variables with dry run and verbose output
export CONTROL_PLANE_URL="https://api.example.com"
export API_USER="admin"
export API_PASSWORD="password123"
python3 ./scripts/deployToDB.py --dry-run --verbose
```

**Account Configurations (deployAccountsToDB.py):**
```bash
# Dry run for all account configurations (summary only)
python3 ./scripts/deployAccountsToDB.py https://api.example.com admin password123 --dry-run

# Dry run with detailed JSON reports
python3 ./scripts/deployAccountsToDB.py https://api.example.com admin password123 --dry-run --verbose

# Dry run for a specific account
python3 ./scripts/deployAccountsToDB.py https://api.example.com admin password123 AMPLITUDE_ACCOUNT --dry-run

# Using environment variables with dry run
export CONTROL_PLANE_URL="https://api.example.com"
export API_USER="admin"
export API_PASSWORD="password123"
python3 ./scripts/deployAccountsToDB.py --dry-run --verbose
```

#### What Dry Run Does

**✅ Actions Performed in Dry Run Mode:**

**For Integration Definitions (deployToDB.py):**
- Reads configuration files from the local filesystem
- Shows execution plan with all parameters
- Calculates what changes would be made (without database access)
- Generates user-friendly summary reports
- Shows detailed JSON reports when `--verbose` flag is used

**For Account Configurations (deployAccountsToDB.py):**
- Reads account configuration files from local directories
- Shows execution plan with all parameters
- Analyzes local account configurations without database comparison
- Generates user-friendly summary reports
- Shows detailed JSON reports when `--verbose` flag is used

**❌ Actions NOT Performed in Dry Run Mode:**

**For Integration Definitions (deployToDB.py):**
- No actual HTTP POST/PUT requests to create or update configurations
- No modifications to the database
- No database connections for fetching existing data
- No changes to existing configurations

**For Account Configurations (deployAccountsToDB.py):**
- No actual HTTP POST/PUT requests to create or update accounts
- No modifications to the database
- No database connections for fetching existing account data (in dry run mode)
- No changes to existing account configurations

#### Verbose Mode

The `--verbose` flag controls the level of detail in the output:

**Default Mode (without --verbose):**
- Shows execution plan
- Shows user-friendly summary with counts and lists
- Clean, concise output focused on actionable information

**Verbose Mode (with --verbose):**
- Shows execution plan
- Shows user-friendly summary
- **Additionally shows detailed JSON reports:**
  - Complete configuration data for each item
  - Full API endpoint information
  - Detailed status and action information
  - Stale data reports

#### Output Examples

**Integration Definitions - Default Mode Output (Clean & Concise):**
```
======================================================================
EXECUTION PLAN
======================================================================
Control Plane URL: https://api.example.com
Username: admin
Password: ***********
Selectors to process: destination
Specific item: am
...

##################################################
Destination Summary - What Would Happen
##################################################
📊 Total configurations processed: 1
🆕 Would CREATE: 1 new records
🔄 Would UPDATE: 0 existing records
✅ No changes needed: 0 records

🆕 New records that would be CREATED:
   - AM (37536 chars)

⚠️  In normal mode, these changes would be PERMANENT!
🌐 Database: https://api.example.com
👤 User: admin
##################################################
```

**Account Configurations - Default Mode Output (Clean & Concise):**
```
======================================================================
EXECUTION PLAN
======================================================================
Control Plane URL: https://api.example.com
Username: admin
Password: ***********
Processing: ALL account configurations
...

##################################################
Account Summary - What Would Happen
##################################################
📊 Total account configurations processed: 2
🆕 Would CREATE: 2 new accounts
🔄 Would UPDATE: 0 existing accounts
✅ No changes needed: 0 accounts

🆕 New accounts that would be CREATED:
   - AMPLITUDE_ACCOUNT
   - FACEBOOK_PIXEL_ACCOUNT

⚠️  In normal mode, these changes would be PERMANENT!
🌐 Database: https://api.example.com
👤 User: admin
##################################################
```

**Verbose Mode Output (Includes Detailed JSON):**
Shows everything above PLUS:

**For Integration Definitions:**
```
##################################################
Destination Definition Update Report (DRY RUN)
[
  {
    "name": "AM",
    "action": "create (dry run)",
    "status": "DRY RUN - Would create",
    "data": {
      "name": "AM",
      "displayName": "Amplitude",
      "config": { ... full configuration ... }
    },
    "directory": "./src/configurations/destinations/am",
    "api_endpoint": "https://api.example.com/destination-definitions/",
    "config_size": 37536
  }
]

##################################################
Stale Destinations Report
[
  "DRY RUN - Cannot determine stale data without database access"
]
```

**For Account Configurations:**
```
##################################################
Account Definition Update Report (DRY RUN)
[
  {
    "name": "AMPLITUDE_ACCOUNT",
    "action": "create (dry run)",
    "status": "DRY RUN - Would create",
    "data": {
      "name": "AMPLITUDE_ACCOUNT",
      "displayName": "Amplitude Account",
      "config": { ... full account configuration ... }
    },
    "directory": "./src/configurations/destinations/amplitude/accounts/oauth",
    "api_endpoint": "https://api.example.com/account-definitions/",
    "config_size": 2048
  }
]
```

**Normal Mode Output:**
```json
{
  "name": "AMPLITUDE",
  "action": "update",
  "status": 200
}
```

**Dry Run Mode Output:**
```json
{
  "name": "AMPLITUDE",
  "action": "update (dry run)",
  "status": "DRY RUN - Would update",
  "diff": {
    "displayName": "Updated Display Name",
    "config": {...}
  },
  "directory": "./src/configurations/destinations/amplitude",
  "api_endpoint": "https://api.example.com/destination-definitions/",
  "config_size": 37536
}
```

#### Use Cases

**Default Mode (Summary Only):**
- **Quick Validation:** Fast overview of what would change
- **CI/CD Pipelines:** Clean output for automated systems
- **Daily Operations:** Quick checks before deployment
- **Team Updates:** Share concise status reports

**Verbose Mode (Detailed Reports):**
- **Debugging:** Inspect full configuration data and API details
- **Configuration Review:** Deep dive into specific changes
- **Troubleshooting:** Understand why configurations might not be updating
- **Documentation:** Generate detailed reports for compliance
- **Development:** Verify exact JSON structure and API endpoints

**Combined Use Cases:**
- **Pre-deployment Validation:** Verify changes before applying them
- **Team Collaboration:** Share proposed changes for review
- **Configuration Management:** Track and audit configuration changes

#### Quick Reference

**Integration Definitions (deployToDB.py):**

| Command | Output | Use Case |
|---------|--------|----------|
| `deployToDB.py` | Full execution with database changes | Production deployment |
| `deployToDB.py --dry-run` | Summary only, no database changes | Quick validation |
| `deployToDB.py --dry-run --verbose` | Summary + detailed JSON, no database changes | Debugging & detailed review |
| `deployToDB.py --verbose` | Full execution + detailed JSON | Production with detailed logging |

**Account Configurations (deployAccountsToDB.py):**

| Command | Output | Use Case |
|---------|--------|----------|
| `deployAccountsToDB.py` | Full execution with database changes | Production account deployment |
| `deployAccountsToDB.py --dry-run` | Summary only, no database changes | Quick account validation |
| `deployAccountsToDB.py --dry-run --verbose` | Summary + detailed JSON, no database changes | Account debugging & detailed review |
| `deployAccountsToDB.py --verbose` | Full execution + detailed JSON | Production account deployment with detailed logging |

## Contribute

We would love to see you contribute to RudderStack. Get more information on how to contribute [**here**](CONTRIBUTING.md).
