import fs from 'fs';
import path from 'path';
import Ajv from 'ajv';

type DefinitionCase = {
  directory: string;
  name: string;
  authenticationType: string;
  gate: string;
  refreshOAuthToken: boolean;
  secretFields: string[];
  isOAuth: boolean;
  optionFields: string[];
  fieldOrder: string[];
  validOptions: Record<string, unknown>;
};

const readJson = (file: string) => JSON.parse(fs.readFileSync(path.resolve(file), 'utf-8'));
const destinationRoot = 'src/configurations/destinations/custom_audience';
const fixture = readJson('test/data/validation/destinations/custom_audience.json') as Array<{
  accountDefinitions?: DefinitionCase[];
}>;
const definitions = fixture.flatMap(({ accountDefinitions = [] }) => accountDefinitions);
const destination = readJson(`${destinationRoot}/db-config.json`);

describe.each(definitions)('$name account definition', (definition) => {
  const accountRoot = `${destinationRoot}/accounts/${definition.directory}`;
  const dbConfig = readJson(`${accountRoot}/db-config.json`);
  const uiConfig = readJson(`${accountRoot}/ui-config.json`).uiConfig;
  const schema = readJson(`${accountRoot}/schema.json`);
  const ajv = new Ajv({ allErrors: true, useDefaults: true, strict: false });
  const validateOptions = ajv.compile(schema.optionsSchema);
  const validateSecret = ajv.compile(schema.secretSchema);
  const options = (patch: Record<string, unknown> = {}) => ({
    ...definition.validOptions,
    ...patch,
  });

  it('matches the fixture definition shape and form order', () => {
    expect(dbConfig.name).toBe(definition.name);
    expect(dbConfig.authenticationType).toBe(definition.authenticationType);
    expect(dbConfig.config.refreshOAuthToken).toBe(definition.refreshOAuthToken);
    expect(dbConfig.config.secretFields).toEqual(definition.secretFields);
    expect(dbConfig.config.optionFields).toEqual(definition.optionFields);
    expect(dbConfig.displayOptions.hidden.gate.flags).toEqual([
      { name: definition.gate, value: false },
    ]);
    expect(uiConfig.isOAuth).toBe(definition.isOAuth ? true : undefined);
    expect(uiConfig.form.fields.map((field: { label: string }) => field.label)).toEqual(
      definition.fieldOrder,
    );
    expect(destination.config.supportedAccountDefinitions.rudderAccountId).toContain(
      definition.name,
    );
    expect(Object.keys(schema.optionsSchema.properties)).toEqual(definition.optionFields);
    expect(Object.keys(schema.secretSchema.properties)).toEqual(definition.secretFields);
  });

  it('requires provider URLs, client ID, and client secret', () => {
    for (const field of Object.keys(definition.validOptions)) {
      const missing = options();
      delete missing[field];
      expect(validateOptions(missing)).toBe(false);
    }
    expect(validateSecret({})).toBe(false);
    expect(validateSecret({ clientSecret: 's' })).toBe(true);
  });

  it('accepts a provider token URL and rejects ngrok subdomains and invalid URLs', () => {
    expect(validateOptions(options({ tokenUrl: 'https://api.example.com/oauth/token' }))).toBe(
      true,
    );
    expect(validateOptions(options({ tokenUrl: 'https://api.example.com/x.localhost' }))).toBe(
      true,
    );
    for (const tokenUrl of [
      'https://x.ngrok.io/token',
      'https://a.b.ngrok.io/token',
      'https://A.B.NGROK.IO/token',
      'http://api.example.com/token',
      'https://localhost/token',
      'https://x.localhost/token',
      'https://X.LOCALHOST/token',
      'https://api.example.com/token?code=1',
      'https://api.example.com/token#fragment',
    ]) {
      expect({ tokenUrl, valid: validateOptions(options({ tokenUrl })) }).toEqual({
        tokenUrl,
        valid: false,
      });
    }
  });

  if (definition.authenticationType === 'oauth') {
    it('accepts an HTTPS authorization URL with query and rejects invalid URLs', () => {
      expect(
        validateOptions(
          options({ authorizationUrl: 'https://api.example.com/authorize?prompt=consent' }),
        ),
      ).toBe(true);
      expect(
        validateOptions(options({ authorizationUrl: 'http://api.example.com/authorize' })),
      ).toBe(false);
      expect(validateOptions(options({ authorizationUrl: 'https://' }))).toBe(false);
    });
  }

  it('enforces client ID and secret lengths', () => {
    expect(validateOptions(options({ clientId: 'a'.repeat(200) }))).toBe(true);
    for (const clientId of ['', ' ', 'a'.repeat(201)]) {
      expect(validateOptions(options({ clientId }))).toBe(false);
    }
    expect(validateSecret({ clientSecret: 's'.repeat(500) })).toBe(true);
    expect(validateSecret({ clientSecret: '' })).toBe(false);
    expect(validateSecret({ clientSecret: 's'.repeat(501) })).toBe(false);
  });

  it('accepts optional empty scopes and enforces tag count and length', () => {
    expect(validateOptions(options({ scopes: [] }))).toBe(true);
    expect(validateOptions(options({ scopes: Array(50).fill('read') }))).toBe(true);
    expect(validateOptions(options({ scopes: ['s'.repeat(200)] }))).toBe(true);
    for (const scopes of [
      Array(51).fill('read'),
      [''],
      ['read write'],
      ['read,write'],
      ['s'.repeat(201)],
      'read write',
    ]) {
      expect(validateOptions(options({ scopes }))).toBe(false);
    }
  });

  it('defaults the separator and auth method and rejects unsupported choices', () => {
    const defaulted = options();
    expect(validateOptions(defaulted)).toBe(true);
    expect(defaulted.scopeSeparator).toBe('space');
    expect(defaulted.tokenAuthMethod).toBe('client_secret_basic');
    expect(validateOptions(options({ scopeSeparator: 'comma' }))).toBe(true);
    expect(validateOptions(options({ tokenAuthMethod: 'client_secret_post' }))).toBe(true);
    expect(validateOptions(options({ scopeSeparator: 'pipe' }))).toBe(false);
    expect(validateOptions(options({ tokenAuthMethod: 'none' }))).toBe(false);
  });

  it('accepts optional empty token parameters and enforces the 2,000 character limit', () => {
    expect(validateOptions(options({ extraTokenParams: '' }))).toBe(true);
    expect(validateOptions(options({ extraTokenParams: 'x'.repeat(2000) }))).toBe(true);
    expect(validateOptions(options({ extraTokenParams: 'x'.repeat(2001) }))).toBe(false);
  });
});
