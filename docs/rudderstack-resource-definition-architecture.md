# RFC: Resource Definition Architecture Pattern for RudderStack Integration System

## Metadata

- **Title:** Resource Definition Architecture Spec
- **Date:** November 2025
- **Author:** Aris Plakias

---

## Executive Summary

This document formalizes how RudderStack services should consume and evolve shared resource definitions in the integrations-config repository.

It introduces a layered architecture pattern to reduce inconsistencies, improve maintainability, and enable predictable evolution of integration definitions across services.
Finally, it outlines the foundation for schema versioning, the next step in the maturation of RudderStack’s integration platform.

---

## 1. Architectural Context

The approach described in this RFC aligns conceptually with **Schema-Driven Design (SDD)** — an architectural pattern where system behavior, validation, and configuration are governed by shared machine-readable definitions rather than hardcoded logic.

In schema-driven systems, a **schema or metadata layer** defines the structure and semantics of resources.  
Individual services interpret these schemas according to their domain responsibilities, creating a loosely coupled but contractually consistent ecosystem.

This pattern is used in systems such as **Kubernetes (Custom Resource Definitions)**, **Salesforce (Metadata API)**, and **AWS CloudFormation** — all of which rely on versioned schemas as the source of truth for resource behavior.

RudderStack’s `integrations-config` repository already embodies these principles implicitly:  
each integration is defined through JSON-based metadata that determines how sources, destinations, and accounts are rendered, validated, and executed across multiple services.

This RFC aims to make that implicit schema-driven architecture **explicit, consistent, and governed**, ensuring sustainable growth as integrations evolve.

---

## 2. Problem Statement

### 2.1 Current Challenges

1. **Unmoderated Growth** – Resource definitions evolved without clear ownership or design intent.
2. **Missing Abstraction Boundaries** – Services depend on internal integration details they shouldn’t need to know.
3. **Governance Gap** – No explicit process defines how schemas evolve or are validated.
4. **Knowledge Silos** – Understanding of field semantics exists only in code, not documentation.

### 2.2 Impact

- Slower development and onboarding
- Tight coupling between services
- Difficult schema evolution
- Inconsistent integration behavior

---

## 3. Background: Current System Layout

Each RudderStack integration (Source, Destination, Account) is described by:

```text

src/configurations/{destinations|sources}/{integration-name}/
├── db-config.json
├── schema.json
└── ui-config.json

```

| File             | Purpose                    | Consumers     |
| ---------------- | -------------------------- | ------------- |
| `db-config.json` | Core behavior and metadata | All services  |
| `schema.json`    | API input validation       | Control plane |
| `ui-config.json` | UI rendering               | Web App       |

While structured, there are no clear **contracts** governing which services interpret which parts of these files — especially `db-config.json`.

---

## 4. Current State Interpretation

Although RudderStack’s integrations follow a de-facto schema-driven approach, this structure is **implicit and undocumented**.
Developers often need to read service code to understand how specific fields (e.g., `config.auth.type`, `options.hidden`) are interpreted.

This section classifies existing definitions to surface and document that institutionalized knowledge.

---

### 4.1 Example: Source Definition

```json
{
  "name": "facebook_lead_ads_native",
  "type": "cloud",
  "category": "webhook",
  "displayName": "Facebook Lead Ads",
  "config": {
    "supportedAccountDefinitions": {
      "rudderAccountId": ["SOURCE_FACEBOOK_LEAD_ADS_NATIVE_OAUTH"]
    }
  },
  "options": {
    "hydration": { "enabled": true },
    "isBeta": true,
    "hidden": {
      "featureFlagName": "AMP_enable-fbla-source",
      "featureFlagValue": false
    },
    "internalSecretKeys": ["pageAccessToken"]
  }
}
```

| Field Path                                              | Purpose                 | Layer                       | Notes                                 |
| ------------------------------------------------------- | ----------------------- | --------------------------- | ------------------------------------- |
| `name`, `displayName`, `type`, `category`               | Identification metadata | **Layer 3 – Schema-Aware**  | Used for discovery and classification |
| `config.supportedAccountDefinitions`                    | Relationship metadata   | **Layer 2 – Feature-Aware** | Defines orchestration constraints     |
| `options.hydration`, `options.isBeta`, `options.hidden` | Feature gating          | **Layer 2 – Feature-Aware** | Controls availability and rollout     |
| `options.internalSecretKeys`                            | Secret field metadata   | **Layer 2 – Feature-Aware** | Used by auth/UI for masking           |

---

### 4.2 Example: Destination Definition

```json
{
  "name": "GA",
  "displayName": "Google Analytics",
  "config": {
    "auth": { "type": "OAuth", "provider": "Google", "role": "google_analytics" },
    "supportsVisualMapper": true,
    "supportedSourceTypes": ["android", "ios", "web"],
    "supportedConnectionModes": { "web": ["cloud", "device"] },
    "destConfig": { "defaultConfig": ["trackingID"] },
    "secretKeys": []
  },
  "options": { "deprecated": true }
}
```

| Field Path                                                                        | Purpose                 | Layer                           | Notes                             |
| --------------------------------------------------------------------------------- | ----------------------- | ------------------------------- | --------------------------------- |
| `name`, `displayName`                                                             | Core metadata           | **Layer 3 – Schema-Aware**      | Common across systems             |
| `config.auth`                                                                     | Authentication metadata | **Layer 1 – Integration-Aware** | Used by `rudder-auth`             |
| `config.supportsVisualMapper`, `supportedSourceTypes`, `supportedConnectionModes` | Capability metadata     | **Layer 2 – Feature-Aware**     | Defines compatibility rules       |
| `config.destConfig`, `secretKeys`                                                 | Structural metadata     | **Layer 2 – Feature-Aware**     | Guides validation and rendering   |
| `options.deprecated`                                                              | Lifecycle metadata      | **Layer 2 – Feature-Aware**     | Used for visibility and migration |
| `transformAtV1`                                                                   | Implementation hint     | **Layer 1 – Integration-Aware** | Affects runtime transformations   |

---

### 4.3 Summary of Classification

| Classification                        | Description                             | Example Fields             | Typical Consumers        |
| ------------------------------------- | --------------------------------------- | -------------------------- | ------------------------ |
| **Metadata (Layer 3)**                | Identification info shared by all       | `name`, `displayName`      | Web-App, Rudder-Server   |
| **Structural Metadata (Layer 2)**     | Field shape, secrets, supported modes   | `destConfig`, `secretKeys` | Web-App, Rudder-Server   |
| **Behavioral Metadata (Layer 2)**     | Lifecycle, feature flags, orchestration | `isBeta`, `deprecated`     | Web-App, Rudder-Server   |
| **Implementation Metadata (Layer 1)** | Integration-specific execution          | `auth`, `transformAtV1`    | Rudder-Auth, Transformer |

**Key Insight:**
The current JSON definitions already encode multiple semantic layers.
By classifying them explicitly, RudderStack can **document institutional knowledge** without changing structure or behavior.

---

## 5. Proposed Solution A: Document the Existing Schema (Knowledge Formalization)

Rather than restructuring definitions, we first propose **formal documentation and classification** of existing fields.

### Objectives

1. Define each field’s **semantic layer**, ownership, and consumers.
2. Create a **reference catalog** in the `integrations-config` repo.
3. Introduce linting/validation rules to catch schema misuse.
4. Establish maintainers per layer:

   - Integration maintainers (Layer 1)
   - Platform maintainers (Layer 2)
   - Infra/data maintainers (Layer 3)

This approach preserves backward compatibility while making the implicit structure explicit.

---

## 6. Proposed Solution B: Layered Architecture Pattern

Once the current state is documented, a **formal layered architecture** can define how services interact with resource definitions.

### Layer Overview

```text
┌─────────────────────────────────────────────┐
│ Layer 3: Schema-Aware                       │
│ (Generic Resource Handling)                 │
├─────────────────────────────────────────────┤
│ Layer 2: Feature-Aware                      │
│ (Capability & Constraint Validation)        │
├─────────────────────────────────────────────┤
│ Layer 1: Integration-Aware                  │
│ (Platform-Specific Implementation)          │
└─────────────────────────────────────────────┘
```

| Service Type | Reads Credentials | Interprets Features | Calls External APIs | Example Services             |
| ------------ | ----------------- | ------------------- | ------------------- | ---------------------------- |
| **Layer 1**  | ✅                | ✅                  | ✅                  | `rudder-auth`, `transformer` |
| **Layer 2**  | ❌                | ✅                  | ❌                  | `rudder-server`, `web-app`   |
| **Layer 3**  | ❌                | ❌                  | ❌                  | audit, billing               |

This pattern establishes stable **abstraction boundaries** between schema consumers.

---

## 7. Schema Versioning and Resource Evolution

Integration definitions evolve (e.g., new account fields).
To maintain consistency, versioning should be explicit and traceable.

### Principles

1. **Immutable Versions:** each schema version (`v1`, `v2`) remains unchanged.
2. **Version Reference:** resources store the schema version they were validated against.
3. **Version-Aware Consumption:** services load the version declared in the resource.
4. **Compatibility:** additive changes are backward compatible; breaking ones require migration.
5. **Schema Registry:** `integrations-config` acts as a versioned registry per integration.

---

## 8. Expected Benefits

- **Consistency:** Shared interpretation of definitions
- **Decoupling:** Clear layer-specific access boundaries
- **Safe Evolution:** Versioned schemas prevent mismatches
- **Governance:** Explicit ownership and validation pipeline
- **Maintainability:** Reduced duplication, faster onboarding

---

## 9. Conclusion

RudderStack’s `integrations-config` already operates as a **schema source of truth**.
By documenting the existing implicit layers (Solution A) and introducing structured schema governance (Solution B),
we can transform it into a **governed, evolvable metadata platform** — ensuring scalable, consistent, and maintainable integration development.

---
