import fs from 'fs';
import path from 'path';
import Ajv from 'ajv';

const schema = JSON.parse(
  fs.readFileSync(path.resolve('src/schemas/account/account-ui-config-schema.json'), 'utf-8'),
);
const validate = new Ajv({ allErrors: true, strict: false }).compile(schema);

const accountUiConfig = (fields: Record<string, unknown>[]) => ({
  uiConfig: {
    name: 'OAuth',
    icon: 'key',
    description: 'Connect an account',
    recommended: false,
    isOAuth: true,
    form: { title: 'Connect', fields },
  },
});

const nameField = { component: 'textField', label: 'Account name', key: 'name' };
const secretField = {
  component: 'textField',
  label: 'Client secret',
  key: ['options', 'clientSecret'],
  secret: true,
};
const tagField = { component: 'tagField', label: 'Scopes', key: ['options', 'scopes'] };
const copyField = { component: 'copyField', label: 'Redirect URI', value: '{{oauthRedirectUri}}' };

describe('Account UI form field schema', () => {
  it('accepts scope tags, an OAuth client secret, and a keyless Redirect URI copy field', () => {
    expect(validate(accountUiConfig([nameField, secretField, tagField, copyField]))).toBe(true);
  });

  it('requires a value and forbids a key on copy fields', () => {
    expect(
      validate(accountUiConfig([nameField, { ...copyField, key: ['options', 'redirectUri'] }])),
    ).toBe(false);
    expect(
      validate(accountUiConfig([nameField, { component: 'copyField', label: 'Redirect URI' }])),
    ).toBe(false);
  });

  it('requires a key on input fields and rejects unknown properties', () => {
    expect(validate(accountUiConfig([{ component: 'textField', label: 'Account name' }]))).toBe(
      false,
    );
    expect(validate(accountUiConfig([nameField, { ...copyField, unexpected: true }]))).toBe(false);
  });
});
