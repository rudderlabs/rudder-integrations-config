import fs from 'fs';
import path from 'path';
import Ajv, { ValidateFunction } from 'ajv';
import ajvErrors from 'ajv-errors';
import addKeywords from 'ajv-keywords';

interface CustomAudienceAccountSchema {
  optionsSchema: Record<string, unknown>;
  secretSchema: Record<string, unknown>;
  combinedSchema: Record<string, unknown>;
}

function compileWithConfigBackendOptions(schema: Record<string, unknown>): ValidateFunction {
  const ajv = new Ajv({
    allErrors: true,
    useDefaults: true,
    strict: false,
    strictSchema: false,
    strictRequired: false,
    strictNumbers: true,
    strictTypes: true,
    strictTuples: true,
  });
  addKeywords(ajv, ['uniqueItemProperties']);
  ajvErrors(ajv);
  return ajv.compile(schema);
}

const schemaPath = path.resolve(
  'src/configurations/destinations/custom_audience/accounts/custom_audience_static_auth/schema.json',
);
const accountSchema = JSON.parse(
  fs.readFileSync(schemaPath, 'utf-8'),
) as CustomAudienceAccountSchema;

describe('DESTINATION_CUSTOM_AUDIENCE_STATIC_AUTH account schema', () => {
  it('compiles every schema with config-backend strict-type options', () => {
    expect(() => compileWithConfigBackendOptions(accountSchema.optionsSchema)).not.toThrow();
    expect(() => compileWithConfigBackendOptions(accountSchema.secretSchema)).not.toThrow();
    expect(() => compileWithConfigBackendOptions(accountSchema.combinedSchema)).not.toThrow();
  });

  it('validates standalone option and secret field shapes', () => {
    const validateOptions = compileWithConfigBackendOptions(accountSchema.optionsSchema);
    const validateSecret = compileWithConfigBackendOptions(accountSchema.secretSchema);

    expect(validateOptions({ authenticationType: 'noAuth' })).toBe(true);
    expect(validateOptions({ authenticationType: 'apiKey', apiKeyName: 'X-API-Key' })).toBe(true);
    expect(validateOptions({ authenticationType: 'apiKey', apiKeyName: 'Invalid Header' })).toBe(
      false,
    );
    expect(validateOptions({ authenticationType: 'unknown' })).toBe(false);
    expect(validateSecret({ basicAuthPassword: '', bearerToken: '', apiKeyValue: '' })).toBe(true);
    expect(validateSecret({ bearerToken: 'x'.repeat(2001) })).toBe(false);
  });

  it.each([
    ['noAuth', { options: { authenticationType: 'noAuth' } }],
    [
      'basicAuth',
      {
        options: { authenticationType: 'basicAuth', basicAuthUserName: 'user' },
        secret: { basicAuthPassword: 'password' },
      },
    ],
    [
      'bearerToken',
      {
        options: { authenticationType: 'bearerToken' },
        secret: { bearerToken: 'token' },
      },
    ],
    [
      'apiKey',
      {
        options: { authenticationType: 'apiKey', apiKeyName: 'X-API-Key' },
        secret: { apiKeyValue: 'key' },
      },
    ],
  ])('accepts valid %s account payloads', (_authenticationType, payload) => {
    const validateCombined = compileWithConfigBackendOptions(accountSchema.combinedSchema);

    expect(validateCombined(payload)).toBe(true);
  });

  it.each([
    [
      'basicAuth',
      {
        options: { authenticationType: 'basicAuth', basicAuthUserName: '' },
        secret: { basicAuthPassword: '' },
      },
    ],
    [
      'bearerToken',
      {
        options: { authenticationType: 'bearerToken' },
        secret: { bearerToken: '' },
      },
    ],
    [
      'apiKey',
      {
        options: { authenticationType: 'apiKey', apiKeyName: '' },
        secret: { apiKeyValue: '' },
      },
    ],
  ])('rejects empty credentials for %s account payloads', (_authenticationType, payload) => {
    const validateCombined = compileWithConfigBackendOptions(accountSchema.combinedSchema);

    expect(validateCombined(payload)).toBe(false);
  });

  it.each([
    [
      'noAuth',
      {
        options: { authenticationType: 'noAuth' },
        secret: { bearerToken: 'x'.repeat(2001) },
      },
    ],
    ['basicAuth', { options: { authenticationType: 'basicAuth' } }],
    ['bearerToken', { options: { authenticationType: 'bearerToken' } }],
    ['apiKey', { options: { authenticationType: 'apiKey' } }],
    ['unknown', { options: { authenticationType: 'unknown' } }],
  ])('rejects invalid or incomplete %s account payloads', (_authenticationType, payload) => {
    const validateCombined = compileWithConfigBackendOptions(accountSchema.combinedSchema);

    expect(validateCombined(payload)).toBe(false);
  });

  it('allows inactive credential fields copied by the migration', () => {
    const validateCombined = compileWithConfigBackendOptions(accountSchema.combinedSchema);

    expect(
      validateCombined({
        options: {
          authenticationType: 'bearerToken',
          basicAuthUserName: 'stale-user',
          apiKeyName: 'X-Stale-Key',
        },
        secret: {
          basicAuthPassword: 'stale-password',
          bearerToken: 'active-token',
          apiKeyValue: 'stale-value',
        },
      }),
    ).toBe(true);
  });
});
