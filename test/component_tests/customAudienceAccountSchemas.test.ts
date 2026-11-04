import fs from 'fs';
import path from 'path';
import Ajv from 'ajv';

const accountRoot = 'src/configurations/destinations/custom_audience/accounts';
const uiSchema = JSON.parse(
  fs.readFileSync(path.resolve('src/schemas/account/account-ui-config-schema.json'), 'utf-8'),
);
const validateUiConfig = new Ajv({ strict: false }).compile(uiSchema);
const accounts = [
  {
    directory: 'custom_audience_machine_oauth_client_credentials',
    requiredOptions: {
      tokenUrl: 'https://api.example.com/oauth/token',
      clientId: 'client-id',
    },
  },
  {
    directory: 'custom_audience_oauth_auth_code',
    requiredOptions: {
      authorizationUrl: 'https://api.example.com/authorize',
      tokenUrl: 'https://api.example.com/oauth/token',
      clientId: 'client-id',
    },
  },
];

describe.each(accounts)('$directory account schema', ({ directory, requiredOptions }) => {
  const schema = JSON.parse(
    fs.readFileSync(path.resolve(accountRoot, directory, 'schema.json'), 'utf-8'),
  );
  const ajv = new Ajv({ strict: false });
  const validateOptions = ajv.compile(schema.optionsSchema);
  const options = (patch: Record<string, unknown> = {}) => ({ ...requiredOptions, ...patch });

  it('accepts its account UI config against the shared schema', () => {
    const uiConfig = JSON.parse(
      fs.readFileSync(path.resolve(accountRoot, directory, 'ui-config.json'), 'utf-8'),
    );
    expect(validateUiConfig(uiConfig)).toBe(true);
  });

  it('accepts public HTTPS token URLs and rejects unsafe or malformed URLs', () => {
    for (const tokenUrl of [
      'https://api.example.com/x.localhost',
      'https://api.example.com:10/token',
      'https://api.example.com:65535/token',
    ]) {
      expect(validateOptions(options({ tokenUrl }))).toBe(true);
    }
    for (const tokenUrl of [
      'https://x.ngrok.io/token',
      'https://a.b.ngrok.io/token',
      'http://api.example.com/token',
      'https://localhost/token',
      'https://x.localhost/token',
      'https://api.example.com/token?code=1',
      'https://api.example.com/token#fragment',
      'https://api.example.com:9/token',
      'https://api.example.com:65536/token',
      'https://api.example.c/token',
    ]) {
      expect({ tokenUrl, valid: validateOptions(options({ tokenUrl })) }).toEqual({
        tokenUrl,
        valid: false,
      });
    }
  });

  if (directory === 'custom_audience_oauth_auth_code') {
    it('accepts an HTTPS authorization URL with query and rejects invalid URLs', () => {
      expect(
        validateOptions(
          options({ authorizationUrl: 'https://api.example.com/authorize?prompt=consent' }),
        ),
      ).toBe(true);
      for (const authorizationUrl of [
        'http://api.example.com/authorize',
        'https://',
        'https://?prompt=consent',
        'https://user:pass@example.com/authorize',
      ]) {
        expect(validateOptions(options({ authorizationUrl }))).toBe(false);
      }
    });
  }
});
