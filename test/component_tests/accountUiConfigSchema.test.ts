import fs from 'fs';
import path from 'path';
import Ajv from 'ajv';

const accountRoot = 'src/configurations/destinations/custom_audience/accounts';
const accountNames = ['custom_audience_client_credentials', 'custom_audience_oauth_auth_code'];

it('validates the new tag and copy fields in Custom Activation account forms', () => {
  const schema = JSON.parse(
    fs.readFileSync(path.resolve('src/schemas/account/account-ui-config-schema.json'), 'utf-8'),
  );
  const validate = new Ajv({ allErrors: true, strict: false }).compile(schema);

  for (const accountName of accountNames) {
    const uiConfig = JSON.parse(
      fs.readFileSync(path.resolve(accountRoot, accountName, 'ui-config.json'), 'utf-8'),
    );
    const fields = uiConfig.uiConfig.form.fields;
    expect(fields.some((field: { component: string }) => field.component === 'tagField')).toBe(
      true,
    );
    if (accountName === 'custom_audience_oauth_auth_code') {
      expect(fields.some((field: { component: string }) => field.component === 'copyField')).toBe(
        true,
      );
    }
    expect(validate(uiConfig)).toBe(true);
  }
});
