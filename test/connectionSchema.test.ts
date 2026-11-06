/* eslint-disable max-len */
import fs from 'fs';
import path from 'path';
import Ajv from 'ajv';

// connection-schema.json files describe what `destinationConfig` may carry on
// POST /v2/retl-connections. Nothing deployed reads them yet, so without these
// tests a draft-07 typo would ship silently and the rudder-iac CLI would copy
// it. allErrors so an error count is meaningful; strict off because the files
// are written for Ajv as config-backend runs it, not for Ajv's own lint rules.
const ajv = new Ajv({ allErrors: true, strict: false });

const destinationsDir = path.resolve('src/configurations/destinations');

function connectionSchemaDestinations(): string[] {
  return fs
    .readdirSync(destinationsDir)
    .filter((name) => fs.existsSync(path.join(destinationsDir, name, 'connection-schema.json')));
}

function readJson(...segments: string[]) {
  return JSON.parse(fs.readFileSync(path.join(destinationsDir, ...segments), 'utf-8'));
}

function enumsByProperty(properties: Record<string, any>): Record<string, string[]> {
  return Object.fromEntries(
    Object.entries(properties ?? {})
      .filter(([, value]) => Array.isArray(value?.enum))
      .map(([key, value]) => [key, value.enum]),
  );
}

const destinations = connectionSchemaDestinations();

test('at least one destination declares a connection schema', () => {
  expect(destinations.length).toBeGreaterThan(0);
});

describe.each(destinations)('%s connection schema', (destination) => {
  const file = readJson(destination, 'connection-schema.json');
  const schema = file.connectionConfigSchema;

  it('holds connectionConfigSchema and nothing else', () => {
    expect(Object.keys(file)).toEqual(['connectionConfigSchema']);
  });

  it('compiles', () => {
    expect(() => ajv.compile(schema)).not.toThrow();
  });

  // The schema is the whole contract, so a key it does not name is a caller
  // mistake rather than something to forward to the transformer.
  it('refuses unknown keys', () => {
    expect(schema.additionalProperties).toBe(false);
  });

  // config-backend applies no defaults, and rudder-iac's destination
  // onboarding turns a default into a written-out spec field, which then reads
  // as a permanent diff against a connection that never carried the value.
  it('declares no default', () => {
    expect(JSON.stringify(schema)).not.toContain('"default"');
  });

  // An enum repeated from the destination's own configSchema is a second copy;
  // this is what keeps it from drifting.
  it('repeats the destination configSchema enums exactly', () => {
    const own = enumsByProperty(readJson(destination, 'schema.json').configSchema?.properties);
    const here = enumsByProperty(schema.properties);
    Object.entries(here).forEach(([property, values]) => {
      if (own[property]) expect(values).toEqual(own[property]);
    });
  });
});

describe('accepted and refused payloads', () => {
  const validator = (destination: string) =>
    ajv.compile(readJson(destination, 'connection-schema.json').connectionConfigSchema);

  // Every key here is one the webapp writes on connections that exist in
  // production today and that no transformer reads. They are refused on
  // purpose: config-backend has to strip them on read, or an import writes a
  // spec that cannot pass validation.
  it.each([
    ['fb_custom_audience', { audienceId: '23851234567890123', isHashRequired: true, subtype: 'MULTI_HASHES' }, 'subtype'],
    ['iterable_audience', { audienceId: '12345', audienceListType: 'Standard' }, 'audienceListType'],
    ['google_adwords_remarketing_lists', { audienceId: '12345', isHashRequired: true, typeOfList: 'General', appId: 'com.example' }, 'appId'],
  ])('%s refuses the dashboard-written %s', (destination, payload, key) => {
    const validate = validator(destination);
    expect(validate(payload)).toBe(false);
    expect(JSON.stringify(validate.errors)).toContain(key);
  });

  it.each([
    ['fb_custom_audience', { audienceId: '23851234567890123', isHashRequired: true, type: 'FILE_IMPORTED', subType: 'MULTI_HASHES' }],
    ['google_adwords_remarketing_lists', { audienceId: '987654321', isHashRequired: true, typeOfList: 'userID' }],
    ['iterable_audience', { audienceId: '12345', updateExistingUsersOnly: false }],
  ])('%s accepts a minimal valid config', (destination, payload) => {
    expect(validator(destination)(payload)).toBe(true);
  });

  // A name or a blank where a numeric id belongs used to pass create and then
  // fail every record at the first sync, which is the failure mode these
  // schemas exist to move to create time.
  it.each([
    ['fb_custom_audience', { audienceId: ' ', isHashRequired: true }],
    ['fb_custom_audience', { audienceId: 'my-audience', isHashRequired: true }],
    ['google_adwords_remarketing_lists', { audienceId: '', isHashRequired: true, typeOfList: 'General' }],
    ['google_adwords_remarketing_lists', { audienceId: 'my-list', isHashRequired: true, typeOfList: 'General' }],
  ])('%s refuses a non-numeric audienceId', (destination, payload) => {
    expect(validator(destination)(payload)).toBe(false);
  });

  it('google_adwords_remarketing_lists requires typeOfList', () => {
    expect(validator('google_adwords_remarketing_lists')({ audienceId: '12345', isHashRequired: true })).toBe(false);
  });

  it('fb_custom_audience refuses a subType value Meta does not know', () => {
    expect(validator('fb_custom_audience')({ audienceId: '12345', isHashRequired: true, subType: 'MULTI_HASH' })).toBe(false);
  });

  // The integer and string forms are one schema rather than a oneOf, so a bad
  // value reads as one error instead of three.
  it('iterable_audience reports one error for one bad audienceId', () => {
    const validate = validator('iterable_audience');
    expect(validate({ audienceId: 'abc' })).toBe(false);
    expect(validate.errors).toHaveLength(1);
  });

  it('iterable_audience accepts the integer form', () => {
    expect(validator('iterable_audience')({ audienceId: 42 })).toBe(true);
  });
});
