# Schema Consolidation Proposal

> This document proposes consolidating `db-config.json` + `schema.json` into a single `definition.json` per integration, while keeping `ui-config.json` separate as a rendering layer.
> See [versioning-design.md](./versioning-design.md) for the versioning design that this consolidation supports.

---

## Current State: Three Files Per Destination

Every destination (239 total) is defined by three files:

### db-config.json — Identity + metadata + field routing

```json
{
  "name": "BRAZE",
  "displayName": "Braze",
  "config": {
    "includeKeys": ["appKey", "dataCenter", "connectionMode", ...],
    "excludeKeys": [],
    "secretKeys": ["restApiKey"],
    "supportedSourceTypes": ["android", "web", "ios", ...],
    "supportedConnectionModes": {
      "android": ["cloud", "device", "hybrid"],
      "web": ["cloud", "device", "hybrid"],
      "unity": ["cloud"]
    },
    "supportedMessageTypes": {
      "cloud": ["group", "identify", "track", ...],
      "device": { "web": ["identify", "track", "page"] }
    },
    "destConfig": {
      "defaultConfig": ["appKey", "dataCenter", "restApiKey", ...],
      "web": ["useNativeSDK", "connectionMode", "trackAnonymousUser", ...],
      "android": ["useNativeSDK", "connectionMode", ...]
    },
    "transformAtV1": "router",
    "saveDestinationResponse": true,
    "auth": { "type": "OAuth", "role": "..." },
    "isAudienceSupported": true,
    "throttlingCost": { "eventType": { "identify": 2, "track": 1 } },
    "hybridModeCloudEventsFilter": { "web": { "messageType": ["identify"] } }
  }
}
```

### schema.json — JSON Schema for config validation

```json
{
  "configSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["dataCenter"],
    "properties": {
      "dataCenter": { "type": "string", "enum": ["US-01", ...], "default": "US-01" },
      "trackAnonymousUser": {
        "type": "object",
        "properties": { "web": { "type": "boolean" } }
      },
      "connectionMode": {
        "type": "object",
        "properties": {
          "web": { "type": "string", "enum": ["cloud", "device", "hybrid"] },
          "android": { "type": "string", "enum": ["cloud", "device", "hybrid"] }
        }
      }
    },
    "allOf": [...]
  }
}
```

### ui-config.json — UI rendering instructions

```json
{
  "uiConfig": {
    "baseTemplate": [
      {
        "title": "Initial setup",
        "sections": [{
          "groups": [{
            "title": "Connection settings",
            "fields": [
              {
                "type": "textInput",
                "label": "Rest API Key",
                "configKey": "restApiKey",
                "regex": "^(.{1,100})$",
                "placeholder": "e.g: 06c19c59-XXXX",
                "secret": true
              },
              {
                "type": "singleSelect",
                "label": "Data Center",
                "configKey": "dataCenter",
                "options": [{ "label": "US-01", "value": "US-01" }, ...],
                "default": "US-01"
              }
            ]
          }]
        }]
      }
    ],
    "sdkTemplate": { ... },
    "consentSettingsTemplate": { ... }
  }
}
```

### How these files reach the database

`scripts/deployToDB.py` merges all three files into a flat JSON blob and stores them in the `destination_definitions` table:

| DB Column      | Source                                                                     |
| -------------- | -------------------------------------------------------------------------- |
| `name`         | db-config.json `name`                                                      |
| `displayName`  | db-config.json `displayName`                                               |
| `config`       | db-config.json `config` object (includeKeys, destConfig, secretKeys, etc.) |
| `configSchema` | schema.json `configSchema` object                                          |
| `uiConfig`     | ui-config.json `uiConfig` object                                           |
| `options`      | db-config.json `options` (isBeta, hidden, etc.)                            |
| `category`     | (set separately)                                                           |

The `config` column is the metadata bag — it holds field routing arrays (`destConfig`, `includeKeys`), platform capabilities (`supportedSourceTypes`, `supportedConnectionModes`), and integration behavior flags (`transformAtV1`, `auth`). The `configSchema` column holds the JSON Schema for AJV validation.

### How the config backend uses these

When serving config to an SDK (e.g., web JavaScript SDK):

1. **Apply defaultConfig keys** — `destConfig.defaultConfig` fields are included for all source types
2. **Apply source-type-specific keys** — `destConfig.web` fields are included for web sources
3. **Unwrap source-type-keyed objects** — `config.trackAnonymousUser.web` → `true`
4. **Filter by includeKeys/excludeKeys** — only `includeKeys` fields are sent to the SDK
5. **Extract secrets** — `secretKeys` fields are stored separately in the secrets service

The critical unwrapping code in `sourceConfig.service.ts`:

```typescript
destConfig[sourceType].forEach((configKey) => {
  if (originalConfig[configKey]?.[sourceType] !== undefined) {
    set(filteredConfig, configKey, originalConfig[configKey][sourceType]);
  }
});
```

---

## Problems With The Current System

1. **Same field described in multiple places** — A field's name is in db-config (`destConfig`, `includeKeys`, `secretKeys`), its type and validation are in schema.json, and its rendering is in ui-config.json. Three files, three sources of "truth."
2. **Redundant declarations** — `enum` values appear in both schema.json and ui-config.json (`options` array). `default` values appear in both. `regex` patterns appear in both. `secret` status is in both db-config (`secretKeys`) and ui-config (`secret: true`).
3. **Top-level arrays drift from reality** — `includeKeys`, `secretKeys`, `excludeKeys` are manually maintained lists that can go out of sync with the actual properties in schema.json. Adding a field to the schema but forgetting `includeKeys` means the SDK never sees it.
4. `**destConfig` duplicates schema structure\*\* — `destConfig.web: ["trackAnonymousUser"]` is redundant information when the schema already has `trackAnonymousUser.properties.web`. The schemaGenerator.py generates the source-type-keyed schema from destConfig, but the reverse derivation is equally trivial.
5. `**schemaGenerator.py` bridges the gap\*\* — This 1200-line script exists solely because db-config and schema are separate files. It reads ui-config field types + db-config `destConfig` to generate schema.json. Consolidation eliminates it.
6. **Adding a field requires 2-3 file edits** — Add to schema.json properties, add to db-config `destConfig` (and possibly `includeKeys`, `secretKeys`), add to ui-config for rendering.

---

## Design Principles

1. **JSON Schema as the backbone** — The `config` block in definition.json IS a valid JSON Schema Draft-07 document. AJV validates config data against it directly. No separate schema.json generation.
2. `**x-` prefixed annotations replace top-level arrays\*\* — JSON Schema allows vendor extensions prefixed with `x-`. AJV ignores them by default. Field annotations like `x-secret`, `x-sdkVisible`, `x-sourceTypeKeyed` live on the field itself.
3. `**x-sourceTypeKeyed` replaces `destConfig`\*\* — A boolean annotation that tells consumers "this field's value is a source-type-keyed object; unwrap it per source type." The schema properties encode which source types.
4. **ui-config.json stays separate** — It is purely a rendering concern. The _shape_ of config it produces (field names, types, enums, defaults) must come from definition.json, not be independently declared.
5. **Config data schema unchanged** — Stored config payloads (`{ "restApiKey": "xxx", "trackAnonymousUser": { "web": true } }`) remain identical. This consolidation only changes how definitions are _authored and maintained_.

---

## definition.json Structure

### Top-Level Anatomy

```
definition.json
├── $schema                           ← meta-schema reference
├── name, displayName                 ← identity (DB columns)
├── configVersion                     ← version metadata
│
├── config                            ← JSON Schema Draft-07 (replaces schema.json)
│   ├── $schema, type, required
│   ├── properties                    ← field definitions with x- annotations
│   └── allOf                         ← conditional validation (if/then)
│
├── sourceTypes                       ← replaces config.supportedSourceTypes
├── connectionModes                   ← replaces config.supportedConnectionModes
├── messageTypes                      ← replaces config.supportedMessageTypes
│
├── transformAtV1                     ← integration behavior
├── saveDestinationResponse
├── auth
│
├── isAudienceSupported?              ← optional capabilities
├── supportsVisualMapper?
├── throttlingCost?
├── hybridModeCloudEventsFilter?
└── options?                          ← isBeta, hidden, etc.
```

### Complete Braze Example

```json
{
  "$schema": "https://rudderstack.com/schemas/destination-definition/v1",

  "name": "BRAZE",
  "displayName": "Braze",
  "configVersion": { "version": "1.0", "status": "current" },

  "config": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["dataCenter"],
    "additionalProperties": false,
    "properties": {
      "restApiKey": {
        "type": "string",
        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{1,100})$",
        "x-secret": true,
        "x-sdkVisible": false
      },

      "appKey": {
        "type": "string",
        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{1,100})$",
        "x-secret": true,
        "x-sdkVisible": true
      },

      "dataCenter": {
        "type": "string",
        "enum": [
          "US-01",
          "US-02",
          "US-03",
          "US-04",
          "US-05",
          "US-06",
          "US-07",
          "US-08",
          "EU-01",
          "EU-02",
          "EU-03",
          "AU-01"
        ],
        "default": "US-01",
        "x-sdkVisible": true
      },

      "usePlatformSpecificApiKeys": {
        "type": "boolean"
      },

      "androidApiKey": {
        "type": "string",
        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{1,100})$"
      },

      "iOSApiKey": {
        "type": "string",
        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{1,100})$"
      },

      "webApiKey": {
        "type": "string",
        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{1,100})$"
      },

      "enableSubscriptionGroupInGroupCall": {
        "type": "boolean",
        "default": false
      },

      "enableNestedArrayOperations": {
        "type": "boolean",
        "default": false
      },

      "sendPurchaseEventWithExtraProperties": {
        "type": "boolean",
        "default": false
      },

      "supportDedup": {
        "type": "boolean",
        "default": false
      },

      "eventFilteringOption": {
        "type": "string",
        "enum": ["disable", "whitelistedEvents", "blacklistedEvents"],
        "default": "disable",
        "x-sdkVisible": true
      },

      "whitelistedEvents": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "eventName": {
              "type": "string",
              "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
            }
          }
        },
        "x-sdkVisible": true
      },

      "blacklistedEvents": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "eventName": {
              "type": "string",
              "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
            }
          }
        },
        "x-sdkVisible": true
      },

      "trackAnonymousUser": {
        "type": "object",
        "properties": {
          "web": { "type": "boolean" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "enableBrazeLogging": {
        "type": "object",
        "properties": {
          "web": { "type": "boolean" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "enablePushNotification": {
        "type": "object",
        "properties": {
          "web": { "type": "boolean" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "allowUserSuppliedJavascript": {
        "type": "object",
        "properties": {
          "web": { "type": "boolean" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "useNativeSDK": {
        "type": "object",
        "properties": {
          "android": { "type": "boolean" },
          "androidKotlin": { "type": "boolean" },
          "ios": { "type": "boolean" },
          "iosSwift": { "type": "boolean" },
          "web": { "type": "boolean" },
          "reactnative": { "type": "boolean" },
          "flutter": { "type": "boolean" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "connectionMode": {
        "type": "object",
        "properties": {
          "android": { "type": "string", "enum": ["cloud", "device", "hybrid"] },
          "androidKotlin": { "type": "string", "enum": ["cloud", "device", "hybrid"] },
          "ios": { "type": "string", "enum": ["cloud", "device", "hybrid"] },
          "iosSwift": { "type": "string", "enum": ["cloud", "device", "hybrid"] },
          "web": { "type": "string", "enum": ["cloud", "device", "hybrid"] },
          "flutter": { "type": "string", "enum": ["cloud", "device"] },
          "reactnative": { "type": "string", "enum": ["cloud", "device"] },
          "unity": { "type": "string", "enum": ["cloud"] },
          "amp": { "type": "string", "enum": ["cloud"] },
          "cordova": { "type": "string", "enum": ["cloud"] },
          "shopify": { "type": "string", "enum": ["cloud"] },
          "cloud": { "type": "string", "enum": ["cloud"] },
          "warehouse": { "type": "string", "enum": ["cloud"] }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "consentManagement": {
        "type": "object",
        "properties": {
          "cloud": { "$ref": "#/$defs/consentArray" },
          "warehouse": { "$ref": "#/$defs/consentArray" },
          "android": { "$ref": "#/$defs/consentArray" },
          "androidKotlin": { "$ref": "#/$defs/consentArray" },
          "ios": { "$ref": "#/$defs/consentArray" },
          "iosSwift": { "$ref": "#/$defs/consentArray" },
          "web": { "$ref": "#/$defs/consentArray" },
          "unity": { "$ref": "#/$defs/consentArray" },
          "amp": { "$ref": "#/$defs/consentArray" },
          "reactnative": { "$ref": "#/$defs/consentArray" },
          "flutter": { "$ref": "#/$defs/consentArray" },
          "cordova": { "$ref": "#/$defs/consentArray" },
          "shopify": { "$ref": "#/$defs/consentArray" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "oneTrustCookieCategories": {
        "type": "object",
        "properties": {
          "android": { "$ref": "#/$defs/oneTrustArray" },
          "ios": { "$ref": "#/$defs/oneTrustArray" },
          "web": { "$ref": "#/$defs/oneTrustArray" },
          "unity": { "$ref": "#/$defs/oneTrustArray" },
          "amp": { "$ref": "#/$defs/oneTrustArray" },
          "cloud": { "$ref": "#/$defs/oneTrustArray" },
          "warehouse": { "$ref": "#/$defs/oneTrustArray" },
          "reactnative": { "$ref": "#/$defs/oneTrustArray" },
          "flutter": { "$ref": "#/$defs/oneTrustArray" },
          "cordova": { "$ref": "#/$defs/oneTrustArray" },
          "shopify": { "$ref": "#/$defs/oneTrustArray" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      },

      "ketchConsentPurposes": {
        "type": "object",
        "properties": {
          "android": { "$ref": "#/$defs/ketchArray" },
          "ios": { "$ref": "#/$defs/ketchArray" },
          "web": { "$ref": "#/$defs/ketchArray" },
          "unity": { "$ref": "#/$defs/ketchArray" },
          "amp": { "$ref": "#/$defs/ketchArray" },
          "cloud": { "$ref": "#/$defs/ketchArray" },
          "warehouse": { "$ref": "#/$defs/ketchArray" },
          "reactnative": { "$ref": "#/$defs/ketchArray" },
          "flutter": { "$ref": "#/$defs/ketchArray" },
          "cordova": { "$ref": "#/$defs/ketchArray" },
          "shopify": { "$ref": "#/$defs/ketchArray" }
        },
        "x-sourceTypeKeyed": true,
        "x-sdkVisible": true
      }
    },

    "$defs": {
      "consentArray": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "provider": {
              "type": "string",
              "enum": ["custom", "iubenda", "ketch", "oneTrust"],
              "default": "oneTrust"
            },
            "consents": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "consent": {
                    "type": "string",
                    "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
                  }
                }
              }
            }
          },
          "allOf": [
            {
              "if": {
                "properties": { "provider": { "const": "custom" } },
                "required": ["provider"]
              },
              "then": {
                "properties": { "resolutionStrategy": { "type": "string", "enum": ["and", "or"] } },
                "required": ["resolutionStrategy"]
              }
            }
          ]
        }
      },
      "oneTrustArray": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "oneTrustCookieCategory": {
              "type": "string",
              "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
            }
          }
        }
      },
      "ketchArray": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "purpose": {
              "type": "string",
              "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{0,100})$"
            }
          }
        }
      }
    },

    "allOf": [
      {
        "if": {
          "properties": {
            "connectionMode": {
              "type": "object",
              "anyOf": [
                { "required": ["web"], "properties": { "web": { "const": "cloud" } } },
                { "required": ["ios"], "properties": { "ios": { "const": "cloud" } } },
                { "required": ["android"], "properties": { "android": { "const": "cloud" } } }
              ]
            }
          },
          "required": ["connectionMode"]
        },
        "then": {
          "properties": {
            "restApiKey": {
              "type": "string",
              "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|^(.{1,100})$"
            }
          },
          "required": ["restApiKey"]
        }
      }
    ]
  },

  "sourceTypes": [
    "android",
    "androidKotlin",
    "ios",
    "iosSwift",
    "web",
    "unity",
    "amp",
    "cloud",
    "warehouse",
    "reactnative",
    "flutter",
    "cordova",
    "shopify"
  ],

  "connectionModes": {
    "android": ["cloud", "device", "hybrid"],
    "androidKotlin": ["cloud", "device", "hybrid"],
    "web": ["cloud", "device", "hybrid"],
    "ios": ["cloud", "device", "hybrid"],
    "iosSwift": ["cloud", "device", "hybrid"],
    "flutter": ["cloud", "device"],
    "reactnative": ["cloud", "device"],
    "unity": ["cloud"],
    "amp": ["cloud"],
    "cordova": ["cloud"],
    "shopify": ["cloud"],
    "cloud": ["cloud"],
    "warehouse": ["cloud"]
  },

  "messageTypes": {
    "cloud": ["group", "identify", "page", "screen", "track", "alias"],
    "device": {
      "web": ["identify", "track", "page"],
      "android": ["identify", "track"],
      "androidKotlin": ["identify", "track"],
      "ios": ["identify", "track"],
      "iosSwift": ["identify", "track"],
      "flutter": ["identify", "track"],
      "reactnative": ["identify", "track"]
    }
  },

  "transformAtV1": "router",
  "saveDestinationResponse": true,
  "isAudienceSupported": true,
  "supportsVisualMapper": true,
  "auth": { "type": "none" },
  "throttlingCost": {
    "eventType": { "identify": 2, "track": 1, "page": 1, "screen": 1, "group": 2, "alias": 1 }
  },
  "hybridModeCloudEventsFilter": {
    "web": { "messageType": ["identify", "track", "page"] }
  }
}
```

### Simple Webhook Example

For contrast, here's a cloud-only destination with no source-type-keyed fields:

```json
{
  "$schema": "https://rudderstack.com/schemas/destination-definition/v1",

  "name": "WEBHOOK",
  "displayName": "Webhook",
  "configVersion": { "version": "1.0", "status": "current" },

  "config": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["webhookUrl"],
    "additionalProperties": false,
    "properties": {
      "webhookUrl": {
        "type": "string",
        "pattern": "(^\\{\\{.*\\|\\|(.*)\\}\\}$)|(^env[.].+)|(?!.*\\.ngrok\\.io)^(?:http(s)?:\\/\\/)[\\w.-]+(?:\\.[\\w\\.-]+)+[\\w\\-\\._~:/?#\\[\\]@!\\$&'\\(\\)\\*\\+,;=.]+$",
        "x-sdkVisible": false
      },
      "webhookMethod": {
        "type": "string",
        "enum": ["POST", "PUT", "PATCH", "GET", "DELETE"],
        "default": "POST",
        "x-sdkVisible": false
      },
      "headers": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "from": { "type": "string" },
            "to": { "type": "string" }
          }
        },
        "x-secret": true,
        "x-sdkVisible": false
      }
    }
  },

  "sourceTypes": [
    "android",
    "androidKotlin",
    "ios",
    "iosSwift",
    "web",
    "unity",
    "amp",
    "cloud",
    "warehouse",
    "reactnative",
    "flutter",
    "cordova",
    "shopify"
  ],

  "connectionModes": {
    "android": ["cloud"],
    "web": ["cloud"],
    "ios": ["cloud"],
    "cloud": ["cloud"],
    "warehouse": ["cloud"]
  },

  "messageTypes": {
    "cloud": ["identify", "track", "page", "screen", "group", "alias"]
  },

  "transformAtV1": "router",
  "saveDestinationResponse": true,
  "auth": { "type": "none" }
}
```

Note: No `x-sourceTypeKeyed` annotations — all fields are global. The `headers` field is a genuine nested array, not a source-type-keyed object.

---

## Field Annotations: The `x-` Convention

JSON Schema Draft-07 allows unknown keywords — AJV ignores them by default. We use `x-` prefixed keywords (following OpenAPI convention) for field-level metadata:

| Annotation          | Type      | Replaces                             | Purpose                                                  |
| ------------------- | --------- | ------------------------------------ | -------------------------------------------------------- |
| `x-secret`          | `boolean` | `secretKeys` array                   | Field contains sensitive data; stored in secrets service |
| `x-sdkVisible`      | `boolean` | `includeKeys` / `excludeKeys` arrays | Whether field is sent to SDK in device mode              |
| `x-immutable`       | `boolean` | `rs-immutable` in schema             | Field cannot be changed after creation                   |
| `x-sourceTypeKeyed` | `boolean` | `destConfig` per-source-type arrays  | Value is a source-type-keyed object (see next section)   |

### How consumers derive legacy arrays from annotations

The config backend (or deploy script) computes the old arrays by scanning `config.properties`:

```python
def compute_field_routing(config_properties):
    include_keys = []
    secret_keys = []
    default_config = []
    source_type_fields = {}  # { "web": [...], "android": [...] }

    for field_name, field_schema in config_properties.items():
        # SDK visibility
        if field_schema.get("x-sdkVisible"):
            include_keys.append(field_name)

        # Secret extraction
        if field_schema.get("x-secret"):
            secret_keys.append(field_name)

        # Source-type routing
        if field_schema.get("x-sourceTypeKeyed"):
            for source_type in field_schema.get("properties", {}):
                source_type_fields.setdefault(source_type, []).append(field_name)
        else:
            default_config.append(field_name)

    dest_config = {"defaultConfig": default_config, **source_type_fields}
    return include_keys, secret_keys, dest_config
```

This is deterministic — the same definition.json always produces the same arrays. No manual sync needed.

---

## Source-Type-Keyed Fields: The Complete Picture

This is the most important design decision in the consolidation. Some config fields store per-source-type values as objects with source type keys:

```json
{
  "restApiKey": "xxx",
  "dataCenter": "US-01",
  "trackAnonymousUser": { "web": true },
  "connectionMode": { "web": "device", "android": "cloud" },
  "consentManagement": {
    "web": [{ "provider": "oneTrust", "consents": [...] }],
    "android": [{ "provider": "ketch", "consents": [...] }]
  }
}
```

This data shape is **unchanged** by consolidation. The question is how to represent it in definition.json's schema so that:

1. AJV validates the actual stored data correctly
2. Consumers can programmatically distinguish source-type-keyed objects from genuine nested objects
3. The config backend knows which fields to unwrap per source type

### The problem

An `{ "type": "object" }` field could be either:

- **Source-type-keyed**: `trackAnonymousUser: { web: true }` — unwrapped to `true` when serving to web SDK
- **Genuine nested object**: `headers: [{ from: "X-Custom", to: "value" }]` — passed through as-is

You cannot tell them apart from the JSON Schema alone.

### The solution: `x-sourceTypeKeyed: true`

A simple boolean annotation on source-type-keyed fields:

```json
"trackAnonymousUser": {
  "type": "object",
  "properties": { "web": { "type": "boolean" } },
  "x-sourceTypeKeyed": true,
  "x-sdkVisible": true
}
```

vs. a genuine nested object (no annotation):

```json
"headers": {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "from": { "type": "string" },
      "to": { "type": "string" }
    }
  }
}
```

### Why this works

Based on thorough codebase analysis:

1. **Clean separation exists today.** Across all 239 destinations, there are ZERO hybrid fields that mix source-type keys with non-source-type keys. Every field is either fully source-type-keyed or not at all.
2. **1:1 mapping with `destConfig`.** In the current system, every field in `destConfig.web`, `destConfig.android`, etc. (non-defaultConfig) is a source-type-keyed object. Every field in `destConfig.defaultConfig` is flat. `x-sourceTypeKeyed` preserves this exact distinction.
3. **Source types are encoded in schema properties.** If `connectionMode` has `properties.web` and `properties.android`, those are the source types it applies to. No need for a separate `x-sourceTypes: [...]` list — the schema itself is the list.
4. **AJV ignores it.** AJV validates against the actual `type: "object"` schema with source-type properties. The `x-sourceTypeKeyed` annotation is invisible to validation. The stored data shape is validated correctly.
5. **Config backend reads it.** The source config service checks `x-sourceTypeKeyed` to decide whether to unwrap:

```typescript
// New approach — reads annotation from definition.json
for (const [key, fieldSchema] of Object.entries(definition.config.properties)) {
  if (fieldSchema['x-sourceTypeKeyed']) {
    // Unwrap: config.connectionMode.web → "device"
    if (originalConfig[key]?.[sourceType] !== undefined) {
      set(filteredConfig, key, originalConfig[key][sourceType]);
    }
  } else {
    // Flat value: config.dataCenter → "US-01"
    set(filteredConfig, key, originalConfig[key]);
  }
}
```

### All known source type keys

The set of valid source type keys (13 values) is fixed and defined in `sourceTypes` at the top level:

```
android, androidKotlin, ios, iosSwift, web, unity, amp,
cloud, warehouse, reactnative, flutter, cordova, shopify
```

CI can validate that every property key inside an `x-sourceTypeKeyed` field is a member of this set.

### Commonly seen source-type-keyed fields

These fields appear as source-type-keyed objects across most destinations:

| Field                      | Typical inner type          | Purpose                                    |
| -------------------------- | --------------------------- | ------------------------------------------ |
| `connectionMode`           | `string` (enum)             | User's chosen connection mode per platform |
| `useNativeSDK`             | `boolean`                   | Whether to use native SDK on this platform |
| `consentManagement`        | `array` of consent objects  | Consent provider config per platform       |
| `oneTrustCookieCategories` | `array` of category objects | OneTrust cookie categories per platform    |
| `ketchConsentPurposes`     | `array` of purpose objects  | Ketch consent purposes per platform        |

Destination-specific source-type-keyed fields (e.g., `trackAnonymousUser`, `enableBrazeLogging` for Braze) are scoped to specific source types.

---

## ui-config.json (Separate, Rendering-Only)

ui-config.json continues to exist as a separate file. It provides rendering hints keyed by `configKey`, which must match a property name in definition.json's `config.properties`.

### What ui-config.json defines

- Component type (`textInput`, `checkbox`, `singleSelect`, `dynamicForm`, `dynamicCustomForm`, `tagInput`)
- Layout (sections, groups, ordering)
- Conditional visibility (`preRequisites`, `conditions`)
- Placeholders, notes, callouts
- Row field definitions for dynamic forms (`rowFields`)
- `sdkTemplate` — SDK-specific settings (source-type-keyed fields rendered as toggles)
- `consentSettingsTemplate` — consent management UI

### What ui-config.json does NOT define

- Field types, enums, defaults, patterns → definition.json
- Secret/immutable status → definition.json `x-secret`, `x-immutable`
- SDK visibility → definition.json `x-sdkVisible`
- Validation rules → definition.json JSON Schema
- Source type scope → definition.json `x-sourceTypeKeyed` + schema properties

### Enforcement

CI validates that every `configKey` in ui-config.json maps to a property in definition.json. Missing mappings are errors.

During transition, ui-config.json can still contain redundant `type`, `enum`, `default`, `regex`, and `secret` fields — they are ignored by the web app once it reads metadata from definition.json instead. These can be removed incrementally.

---

## How Consumers Read the Files

| Consumer           | definition.json                                                                                                                                      | ui-config.json                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **AJV validators** | `config` block directly (standard JSON Schema validation)                                                                                            | Not read                                  |
| **Web app**        | `config.properties` for field metadata (types, enums, defaults, `x-` annotations)                                                                    | Rendering: components, layout, conditions |
| **Config backend** | `config.properties.x-secret` for secret extraction; `x-sourceTypeKeyed` for per-source-type unwrapping; `x-sdkVisible` for include/exclude filtering | Not read                                  |
| **Data plane**     | Receives config instances, not definitions                                                                                                           | Not read                                  |
| **Terraform/CLI**  | `config` block for resource schema generation                                                                                                        | Not read                                  |
| **Deploy script**  | Computes legacy arrays from `x-` annotations (transition period)                                                                                     | Passes through as `uiConfig` DB column    |

---

## Database Column Mapping

### During transition

The deploy script reads definition.json and computes the old column values:

| DB Column      | Computed From                                                                                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`         | `definition.name`                                                                                                                                                                      |
| `displayName`  | `definition.displayName`                                                                                                                                                               |
| `config`       | Top-level fields (`sourceTypes`, `connectionModes`, `messageTypes`, `transformAtV1`, `auth`, etc.) + computed arrays (`includeKeys`, `secretKeys`, `destConfig` from `x-` annotations) |
| `configSchema` | `definition.config` block (the JSON Schema, verbatim)                                                                                                                                  |
| `uiConfig`     | ui-config.json contents                                                                                                                                                                |
| `options`      | `definition.options`                                                                                                                                                                   |

This means existing consumers (config backend, web app) continue working with the same DB column shapes while they're migrated to read `x-` annotations directly.

### After full migration

The `config` DB column can be simplified — `destConfig`, `includeKeys`, `excludeKeys`, `secretKeys` arrays are no longer stored since consumers derive them from `configSchema` annotations. The `config` column holds only platform metadata (`sourceTypes`, `connectionModes`, etc.) and behavior flags (`transformAtV1`, `auth`, etc.).

---

## What Changes When This Is Done

| Before                                                                          | After                                                                |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Edit db-config + schema for one field change                                    | Edit definition.json (1 file for config definition)                  |
| `schemaGenerator.py` generates schema.json from ui-config + db-config           | Schema IS definition.json's `config` block; no generation            |
| `destConfig`, `includeKeys`, `secretKeys` as manually maintained arrays         | `x-sourceTypeKeyed`, `x-sdkVisible`, `x-secret` as field annotations |
| Source of truth split between db-config and schema                              | definition.json is the single source of truth                        |
| Same field info in 3 places (db-config arrays, schema types, ui-config options) | Field defined once in schema; ui-config only adds rendering          |
| Version directory has 3 files                                                   | Version directory has 2 files (definition.json + ui-config.json)     |
| Adding a field: edit db-config arrays + schema properties + ui-config           | Adding a field: edit schema properties + ui-config                   |
| `consentManagement` schema repeated 13x (one per source type, ~600 lines)       | Uses `$ref` to `$defs` — defined once, referenced per source type    |

---

## Migration Path

### Phase 1: Build tooling

1. Build `merge-to-definition.py`: reads db-config.json + schema.json → produces definition.json

- Maps `secretKeys` → `x-secret: true` on each field
- Maps `includeKeys` → `x-sdkVisible: true` on each field
- Maps non-defaultConfig `destConfig` fields → `x-sourceTypeKeyed: true`
- Moves `supportedSourceTypes` → `sourceTypes`, `supportedConnectionModes` → `connectionModes`, etc.
- Deduplicates consent/oneTrust schemas using `$defs` + `$ref`

2. Build meta-schema for definition.json (validates the structure itself)
3. Build `definition-to-legacy.py`: reads definition.json → produces old db-config.json + schema.json (backward compat)

### Phase 2: Generate and validate

1. Run `merge-to-definition.py` for all 239 destinations
2. Validate each definition.json against the meta-schema
3. Validate each definition.json's `config` block validates the same config data as the existing schema.json (round-trip test)
4. Run `definition-to-legacy.py` and diff against originals — must be identical

### Phase 3: Deploy with backward compatibility

1. Update `deployToDB.py` to read definition.json (primary) with fallback to old files
2. Deploy script computes legacy arrays from `x-` annotations and writes to same DB columns
3. All consumers continue working unchanged — they read the same DB column shapes

### Phase 4: Migrate consumers

1. Config backend reads `x-sourceTypeKeyed` from `configSchema` instead of `destConfig` from `config`
2. Config backend reads `x-secret` from `configSchema` instead of `secretKeys` from `config`
3. Config backend reads `x-sdkVisible` from `configSchema` instead of `includeKeys` from `config`
4. Web app reads field metadata (type, enum, default) from `configSchema.properties` instead of ui-config.json

### Phase 5: Cleanup

1. Remove `schemaGenerator.py`
2. Remove db-config.json and schema.json files (definition.json is the source of truth)
3. Remove legacy array computation from deploy script
4. Simplify `config` DB column (drop `destConfig`, `includeKeys`, `secretKeys`)

---

## Open Design Questions

1. `**sdkTemplate` and `consentSettingsTemplate`\*\* — These are hidden UI sections in ui-config.json. They define source-type-keyed fields (like `enableBrazeLogging`) and consent forms. Do they stay in ui-config.json as rendering concerns, or move to definition.json since they define config structure? Recommendation: they stay in ui-config.json for rendering, but their `configKey` references must map to fields in definition.json.
2. `**ui-config.jt` templates\*\* — Complex destinations like GA4 use Jsonnet templates (`ui-config.jt` + `ui-default.json`) that generate ui-config.json. These continue to work — they generate rendering instructions, and the configKey references are validated against definition.json.
3. `**connectionConfigSchema` and `connectionUIConfig`\*\* — These are newer DB columns for connection-level config (separate from destination config). They follow the same pattern and should get the same `x-` annotation treatment in a follow-up.
4. `**$defs` and `$ref` support\*\* — Current schema.json files don't use `$ref`. The consolidated definition.json uses `$ref` to eliminate the 600+ lines of duplicated consent schema. Need to verify AJV supports this with our configuration (it does with Draft-07, but need to confirm with `useDefaults: true`).
5. **Pre-computing vs. on-demand** — Should the config backend pre-compute `destConfig`-equivalent field lists at definition load time (once) and cache them, or compute per request? Recommendation: pre-compute at load time — it's a simple scan of properties, and definitions change rarely.
