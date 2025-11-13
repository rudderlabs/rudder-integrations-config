## Metadata

- **Title:** Resource Definition Spec
- **Date:** November 2025
- **Author:** Aris Plakias

# RudderStack Resource Definition

A **RudderStack Resource Definition** is a standardized three-file pattern for defining integration resources (Sources, Destinations, and Accounts).

Each resource consists of three files with distinct, non-overlapping purposes:

1. **db-config.json** - Service behavior and metadata
2. **schema.json** - Input validation rules
3. **ui-config.json** - UI rendering configuration

This pattern applies identically to Sources (data ingestion), Destinations (data delivery), and Accounts (authentication).

---

## The Three Files of a RudderStack Resource Definition

### 1. db-config.json - Service Behavior

**Purpose**: Controls how RudderStack services behave and make decisions

- ATTENTION: Has **weak coupling** to the persistence layer
- Referenced by all services (web-app, control-plane, data-plane)
- Defines metadata and capability declarations

### 2. schema.json - Input Validation

**Purpose**: public API input validation

- ATTENTION: Has **weak coupling** to the persistence layer
- Only validates **creation request format** (currently POST; TODO: extend to PUT, PATCH, DELETE)
- Uses JSON Schema Draft-07, compiled by AJV at runtime

### 3. ui-config.json - UI Rendering

**Purpose**: Drives web-app component rendering (create flows, form fields)

- Client-specific (web-app only)
- Not used by back-end services

---

## Key Principles

### Separation of Concerns

| File               | Concern          | Consumer      |
| ------------------ | ---------------- | ------------- |
| **db-config.json** | Service behavior | All services  |
| **schema.json**    | Input validation | Control-plane |
| **ui-config.json** | UI rendering     | Web-app       |

### Benefits

- **Universal pattern** - Same structure for Sources, Destinations, and Accounts
- **Predictable** - Know where to find configuration
- **Clear ownership** - Configuration, validation, and UI concerns are separated
- **Maintainable** - Same pattern across 100+ integrations
- **Simple onboarding** - Learn once, apply everywhere
