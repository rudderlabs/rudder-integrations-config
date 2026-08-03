type UnknownRecord = Record<string, unknown>;

export interface DestinationClientConfigMetadataAuditInput {
  destinationDefinition: UnknownRecord;
  schema?: UnknownRecord;
  uiConfig?: unknown;
}

export interface DestinationClientConfigMetadataAuditResult {
  destConfigKeysNotInSchema: string[];
  schemaKeysNotInDestConfig: string[];
  uiConfigKeysNotInDestConfig: string[];
  includeKeysNotInDestConfig: string[];
  destConfigKeysNotInIncludeKeys: string[];
}

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function getStringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === 'string')
    : [];
}

function getDestConfig(destinationDefinition: UnknownRecord): UnknownRecord | undefined {
  const { config } = destinationDefinition;
  if (!isRecord(config) || !isRecord(config.destConfig)) {
    return undefined;
  }

  return config.destConfig;
}

function getAllDestinationClientConfigKeys(destinationDefinition: UnknownRecord): string[] {
  const destConfig = getDestConfig(destinationDefinition);
  if (!destConfig) {
    return [];
  }

  const keys = new Set<string>();
  Object.values(destConfig).forEach((configKeys) => {
    getStringArray(configKeys).forEach((key) => keys.add(key));
  });

  return [...keys].sort();
}

/**
 * Returns the destination config keys that web app and Public API clients may see.
 *
 * `config.destConfig` is the metadata allowlist for dashboard/Public API destination
 * configuration fields. Do not use `includeKeys` for this contract; `includeKeys`
 * controls SDK/source-configuration exposure and may intentionally differ.
 */
export function getDestinationClientVisibleConfigKeys(
  destinationDefinition: UnknownRecord,
  sourceType?: string,
): string[] {
  const destConfig = getDestConfig(destinationDefinition);
  if (!destConfig) {
    return [];
  }

  if (!sourceType) {
    return getStringArray(destConfig.defaultConfig).sort();
  }

  const keys = new Set<string>();
  getStringArray(destConfig.defaultConfig).forEach((key) => keys.add(key));
  getStringArray(destConfig[sourceType]).forEach((key) => keys.add(key));

  return [...keys].sort();
}

/**
 * Filters a persisted destination config to the web app/Public API-visible fields
 * declared in `config.destConfig`.
 */
export function filterDestinationClientVisibleConfig<T extends UnknownRecord>(
  destinationDefinition: UnknownRecord,
  config: T,
  sourceType?: string,
): Partial<T> {
  const allowedKeys = new Set(
    getDestinationClientVisibleConfigKeys(destinationDefinition, sourceType),
  );

  return Object.entries(config).reduce<Partial<T>>((filteredConfig, [key, value]) => {
    if (allowedKeys.has(key)) {
      return {
        ...filteredConfig,
        [key]: value,
      };
    }

    return filteredConfig;
  }, {});
}

function getDestinationSchemaConfigProperties(schema?: UnknownRecord): string[] {
  if (!schema) {
    return [];
  }

  const configSchema = isRecord(schema.configSchema) ? schema.configSchema : schema;
  const properties = isRecord(configSchema.properties) ? configSchema.properties : undefined;

  return properties ? Object.keys(properties).sort() : [];
}

function collectUiConfigKeys(uiConfig: unknown): string[] {
  const keys = new Set<string>();

  function collect(value: unknown): void {
    if (Array.isArray(value)) {
      value.forEach(collect);
      return;
    }

    if (!isRecord(value)) {
      return;
    }

    if (typeof value.type === 'string') {
      const configKey = typeof value.configKey === 'string' ? value.configKey : value.value;
      if (typeof configKey === 'string') {
        keys.add(configKey);
      }
    }

    Object.entries(value).forEach(([key, nestedValue]) => {
      if (key !== 'customFields') {
        collect(nestedValue);
      }
    });
  }

  collect(uiConfig);

  return [...keys].sort();
}

function difference(left: string[], right: string[]): string[] {
  const rightSet = new Set(right);
  return left.filter((key) => !rightSet.has(key)).sort();
}

/**
 * Produces an audit-only metadata drift report. The result is intentionally not
 * used by `validateDestinationDefinitions` because existing definitions contain
 * known drift and `schema.json`/`includeKeys` have backward-compatibility and
 * data-plane responsibilities outside the web app/Public API allowlist.
 */
export function auditDestinationClientConfigMetadata({
  destinationDefinition,
  schema,
  uiConfig,
}: DestinationClientConfigMetadataAuditInput): DestinationClientConfigMetadataAuditResult {
  const destConfigKeys = getAllDestinationClientConfigKeys(destinationDefinition);
  const schemaKeys = getDestinationSchemaConfigProperties(schema);
  const uiConfigKeys = collectUiConfigKeys(uiConfig);
  const config = isRecord(destinationDefinition.config) ? destinationDefinition.config : {};
  const includeKeys = getStringArray(config.includeKeys).sort();

  return {
    destConfigKeysNotInSchema: difference(destConfigKeys, schemaKeys),
    schemaKeysNotInDestConfig: difference(schemaKeys, destConfigKeys),
    uiConfigKeysNotInDestConfig: difference(uiConfigKeys, destConfigKeys),
    includeKeysNotInDestConfig: difference(includeKeys, destConfigKeys),
    destConfigKeysNotInIncludeKeys: difference(destConfigKeys, includeKeys),
  };
}
