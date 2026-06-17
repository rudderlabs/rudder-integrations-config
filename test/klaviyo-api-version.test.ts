import fs from 'fs';
import path from 'path';

const UI_CONFIG_PATH = path.resolve(
  __dirname,
  '../src/configurations/destinations/klaviyo/ui-config.json',
);

const SCHEMA_PATH = path.resolve(
  __dirname,
  '../src/configurations/destinations/klaviyo/schema.json',
);

describe('Klaviyo — apiVersion removal of v1', () => {
  let uiConfig: Record<string, unknown>;
  let schema: Record<string, unknown>;

  beforeAll(() => {
    uiConfig = JSON.parse(fs.readFileSync(UI_CONFIG_PATH, 'utf-8'));
    schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf-8'));
  });

  // ── ui-config.json assertions ──────────────────────────────────────────────

  describe('ui-config.json singleSelect for apiVersion', () => {
    function findApiVersionField(obj: unknown): Record<string, unknown> | null {
      if (Array.isArray(obj)) {
        for (const item of obj) {
          const found = findApiVersionField(item);
          if (found) return found;
        }
        return null;
      }
      if (obj && typeof obj === 'object') {
        const rec = obj as Record<string, unknown>;
        if (rec.type === 'singleSelect' && rec.configKey === 'apiVersion') {
          return rec;
        }
        for (const val of Object.values(rec)) {
          const found = findApiVersionField(val);
          if (found) return found;
        }
      }
      return null;
    }

    it('contains a singleSelect field for apiVersion', () => {
      const field = findApiVersionField(uiConfig);
      expect(field).not.toBeNull();
    });

    it('has exactly one option in the singleSelect', () => {
      const field = findApiVersionField(uiConfig) as Record<string, unknown>;
      const options = field.options as unknown[];
      expect(options).toHaveLength(1);
    });

    it('the single option has value "v2"', () => {
      const field = findApiVersionField(uiConfig) as Record<string, unknown>;
      const options = field.options as Array<Record<string, unknown>>;
      expect(options[0].value).toBe('v2');
    });

    it('does not contain an option with value "v1"', () => {
      const field = findApiVersionField(uiConfig) as Record<string, unknown>;
      const options = field.options as Array<Record<string, unknown>>;
      const v1Option = options.find((opt) => opt.value === 'v1');
      expect(v1Option).toBeUndefined();
    });

    it('has default set to "v2"', () => {
      const field = findApiVersionField(uiConfig) as Record<string, unknown>;
      expect(field.default).toBe('v2');
    });
  });

  // ── schema.json assertions ─────────────────────────────────────────────────

  describe('schema.json apiVersion enum', () => {
    function getApiVersionSchema(s: Record<string, unknown>): Record<string, unknown> | null {
      const configSchema = s.configSchema as Record<string, unknown> | undefined;
      if (!configSchema) return null;
      const properties = configSchema.properties as Record<string, unknown> | undefined;
      if (!properties) return null;
      return (properties.apiVersion as Record<string, unknown>) ?? null;
    }

    it('apiVersion property exists in schema', () => {
      expect(getApiVersionSchema(schema)).not.toBeNull();
    });

    it('enum contains exactly one value', () => {
      const apiVersionSchema = getApiVersionSchema(schema) as Record<string, unknown>;
      const enumValues = apiVersionSchema.enum as unknown[];
      expect(enumValues).toHaveLength(1);
    });

    it('enum contains "v2"', () => {
      const apiVersionSchema = getApiVersionSchema(schema) as Record<string, unknown>;
      const enumValues = apiVersionSchema.enum as unknown[];
      expect(enumValues).toContain('v2');
    });

    it('enum does not contain "v1"', () => {
      const apiVersionSchema = getApiVersionSchema(schema) as Record<string, unknown>;
      const enumValues = apiVersionSchema.enum as unknown[];
      expect(enumValues).not.toContain('v1');
    });

    it('apiVersion is listed in required fields', () => {
      const configSchema = schema.configSchema as Record<string, unknown>;
      const required = configSchema.required as string[];
      expect(required).toContain('apiVersion');
    });
  });
});
