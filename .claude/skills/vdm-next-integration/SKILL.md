---
name: vdm-next-integration
description: Create the configuration definition for a new VDM Next (Visual Data Mapper) destination. Registers the destination, defines capabilities, and sets up authentication.
argument-hint: <destination-name> <auth-type:oauth|apikey>
---

# VDM Next — Configuration Definition

**Objective:** Create the configuration files that register a new VDM Next destination in the RudderStack system.

## Inputs

- **Destination name**: `$ARGUMENTS[0]` (lowercase, e.g., `zoho`, `salesforce`)
- **Auth type**: `$ARGUMENTS[1]` — `oauth` or `apikey`

## Context

This is Step 1 in building a VDM Next integration.

## File Structure

```
src/configurations/destinations/<dest_name>/
├── db-config.json
├── ui-config.json
├── schema.json
└── accounts/<dest_name>_<auth_type>/
    ├── db-config.json
    ├── ui-config.json
    └── schema.json
```
Refer src/schemas/destinations/, src/schemas/account for adding any additional needed fields in the definition. 

## Reference

Find existing VDM destinations by searching for `supportsVisualMapper: true` in `src/configurations/destinations/*/db-config.json`. Read their complete config (db-config, ui-config, schema, and accounts/) for patterns.

Also read the account definition schemas for structural rules:

- `src/schemas/account/account-db-config-schema.json`
- `src/schemas/account/account-schema-schema.json`
- `src/schemas/account/account-ui-config-schema.json`

## VDM Mandatory Fields in db-config.json

Every VDM Next destination **must** include:

```json
{
  "name": "<DEST_NAME_UPPER>",
  "displayName": "<Display Name>",
  "config": {
    "supportsVisualMapper": true,
    "disableJsonMapper": true,
    "supportedSourceTypes": ["warehouse"],
    "supportedMessageTypes": { "cloud": ["record"] },
    "transformAtV1": "router",
    "syncBehaviours": ["mirror"],
    "supportedConnectionModes": { "warehouse": ["cloud"] },
    "destConfig": {
      "defaultConfig": [""]
    }
  }
}
```

**For API Key auth:** change `auth.type` to `"custom"` and remove `rudderScopes`.

## Account Definition (Optional)

### OAuth pattern:

- `authenticationType: "oauth"`, `refreshOAuthToken: true`
- `optionFields`: non-secret config (e.g., `["region"]`)
- Name format: `DESTINATION_<DEST_NAME_UPPER>_OAUTH`
- **Requires** corresponding implementation in `rudder-auth` repo

### API Key pattern:

- `authenticationType: "custom"`
- `secretFields`: encrypted credentials (e.g., `["apiKey"]`)
- `optionFields`: non-secret config
- Name format: `DESTINATION_<DEST_NAME_UPPER>_APIKEY`

## Steps

1. Create `src/configurations/destinations/<dest_name>/`
2. Create `db-config.json` using the VDM template above — update name, displayName, auth, account definitions
3. Create `accounts/<dest_name>_<auth_type>/` with db-config.json, ui-config.json, schema.json (use existing VDM destination as template)
4. Create root `ui-config.json` — must include `accountManagementInput` field, connection mode, consent settings
5. Create root `schema.json` — must validate `rudderAccountId` and consent management
6. Run validation: `npm test -- --testPathPattern="<dest_name>"`

## Critical Rules

- `disableJsonMapper: true` is mandatory — without it, JSON mapper UI shows instead of visual mapper
- `transformAtV1: "router"` is required — VDM always uses router path
- `supportedSourceTypes` must include `"warehouse"`
- `supportedMessageTypes` must be `{ cloud: ["record"] }`
- Account definition name format: `DESTINATION_{DEST_NAME_UPPER}_{AUTH_TYPE_UPPER}`
- For OAuth: the `rudder-auth` repo must have a matching passport strategy and refresh token implementation
