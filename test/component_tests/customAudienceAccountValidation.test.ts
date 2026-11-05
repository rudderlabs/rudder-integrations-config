import fs from 'fs';
import path from 'path';
import Ajv from 'ajv';
import ajvErrors from 'ajv-errors';

const accountNames = ['custom_audience_client_credentials', 'custom_audience_oauth_auth_code'];
const reservedKeys = [
  'client_id',
  'client_secret',
  'code',
  'code_challenge',
  'code_challenge_method',
  'code_verifier',
  'grant_type',
  'redirect_uri',
  'refresh_token',
  'response_type',
  'scope',
  'state',
];

const loadAccount = (name: string, file: string) =>
  JSON.parse(
    fs.readFileSync(
      path.resolve(`src/configurations/destinations/custom_audience/accounts/${name}/${file}`),
      'utf-8',
    ),
  );

const compile = (schema: Record<string, unknown>) => {
  const ajv = new Ajv({ allErrors: true, useDefaults: true, strict: false });
  ajvErrors(ajv);
  return ajv.compile(schema);
};

describe.each(accountNames)('%s account validation', (accountName) => {
  const { optionsSchema, secretSchema } = loadAccount(accountName, 'schema.json');
  const baseOptions = {
    ...(accountName === 'custom_audience_oauth_auth_code' && {
      authorizationUrl: 'https://auth.example.com/authorize',
    }),
    tokenUrl: 'https://auth.example.com/token',
    clientId: 'client-id',
  };

  it('does not add defaults to an options PATCH', () => {
    const options = { ...baseOptions };
    expect(compile(optionsSchema)(options)).toBe(true);
    expect(options).toEqual(baseOptions);
  });

  it('rejects every reserved extra token parameter name, regardless of case', () => {
    const validate = compile(optionsSchema);
    reservedKeys.forEach((key) => {
      [`${key}=x`, `audience=x&${key.toUpperCase()}=y`].forEach((params) => {
        expect(validate({ ...baseOptions, extraTokenParams: params })).toBe(false);
        expect(validate.errors?.[0]?.message).toBe(
          'Extra token parameters cannot use reserved OAuth parameter names (for example, scope or client_id)',
        );
      });
    });
    expect(validate({ ...baseOptions, extraTokenParams: 'audience=x&client%5Fid=y' })).toBe(false);
    expect(validate.errors?.[0]?.message).toBe(
      'Extra token parameters cannot use reserved OAuth parameter names (for example, scope or client_id)',
    );
    expect(validate({ ...baseOptions, extraTokenParams: '?scope=x' })).toBe(false);
  });

  it('accepts reserved words in values and enforces the 2,000-character limit', () => {
    const validate = compile(optionsSchema);
    expect(
      validate({ ...baseOptions, extraTokenParams: 'audience=scope&resource=client_secret' }),
    ).toBe(true);
    expect(validate({ ...baseOptions, extraTokenParams: 'audience=%73cope' })).toBe(true);
    expect(validate({ ...baseOptions, extraTokenParams: 'x'.repeat(2000) })).toBe(true);
    expect(validate({ ...baseOptions, extraTokenParams: 'x'.repeat(2001) })).toBe(false);
    expect(validate.errors?.[0]?.message).toBe('Enter token parameters up to 2000 characters');
  });

  it('rejects a whitespace-only client secret', () => {
    const validate = compile(secretSchema);
    expect(validate({ clientSecret: 'secret value' })).toBe(true);
    expect(validate({ clientSecret: ' \t ' })).toBe(false);
    expect(validate.errors?.[0]?.message).toBe(
      'Enter a client secret between 1 and 500 characters that is not only whitespace',
    );
  });
});
