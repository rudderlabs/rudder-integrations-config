/*
THIS IS A TEMPORARY TEST FILE TO VALIDATE THE INTEGRITY OF THE CONSENT MANAGEMENT FIELDS
IN THE DESTINATIONS' CONFIGURATION FILES
*/

import fs from 'fs';
import path from 'path';

const getJSONDataFromFile = (filePath: string) => {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (e) {
    console.error(e);
    console.error(`Unable to load test data for: "${filePath}"`);
    return null;
  }
};

const deepSearch = (obj: any, value: string) => {
  // eslint-disable-next-line no-restricted-syntax, guard-for-in
  for (const k in obj) {
    if (typeof obj[k] === 'object') {
      const result = deepSearch(obj[k], value);
      if (result) {
        return result;
      }
    } else if (obj[k] === value) {
      return obj;
    }
  }
  return null;
};

describe('Consent Management Fields Integrity tests', () => {
  // Read db-config.json, ui-config.json, and schema.json files in each of the directories
  // under src/configuration/destinations
  // and ensure the fields oneTrustCookieCategories and ketchConsentPurposes are present

  const destDir = path.resolve('src/configurations/destinations');
  const dests = fs
    .readdirSync(destDir)
    .filter((f) => fs.statSync(path.join(destDir, f)).isDirectory());
  dests.forEach((destName) => {
    // Validate db-config.json
    const dbConfigFilePath = path.resolve(`${destDir}/${destName}/db-config.json`);
    const dbConfig = getJSONDataFromFile(dbConfigFilePath);
    const { destConfig, supportedSourceTypes } = dbConfig.config;

    it(`should have oneTrustCookieCategories and ketchConsentPurposes defined per source type instead of the defaultConfig in ${destName}`, () => {
      const { defaultConfig } = destConfig;

      expect(
        defaultConfig.includes('oneTrustCookieCategories') ||
          defaultConfig.includes('ketchConsentPurposes'),
      ).toBe(false);

      let fail = false;
      supportedSourceTypes.forEach((srcType: string) => {
        if (
          !(
            destConfig[srcType].includes('oneTrustCookieCategories') &&
            destConfig[srcType].includes('ketchConsentPurposes')
          )
        ) {
          fail = true;
        }
      });

      expect(fail).toBe(false);
    });

    // Validate schema.json
    const schemaFilePath = path.resolve(`${destDir}/${destName}/schema.json`);
    const schema = getJSONDataFromFile(schemaFilePath);

    it(`should have oneTrustCookieCategories and ketchConsentPurposes properly defined in schema.json in ${destName}`, () => {
      expect(schema.configSchema.properties.oneTrustCookieCategories).toBeDefined();
      expect(schema.configSchema.properties.ketchConsentPurposes).toBeDefined();

      expect(schema.configSchema.properties.oneTrustCookieCategories.type).toBe('object');
      expect(schema.configSchema.properties.ketchConsentPurposes.type).toBe('object');

      expect(schema.configSchema.properties.oneTrustCookieCategories.properties).toBeDefined();
      expect(schema.configSchema.properties.ketchConsentPurposes.properties).toBeDefined();

      expect(
        Object.keys(schema.configSchema.properties.oneTrustCookieCategories.properties),
      ).toEqual(supportedSourceTypes);
      expect(Object.keys(schema.configSchema.properties.ketchConsentPurposes.properties)).toEqual(
        supportedSourceTypes,
      );
    });

    // Validate ui-config.json
    const uiConfigFilePath = path.resolve(`${destDir}/${destName}/ui-config.json`);
    const uiConfig = getJSONDataFromFile(uiConfigFilePath);

    it(`should have oneTrustCookieCategories and ketchConsentPurposes properly defined in ui-config.json in ${destName}`, () => {
      const oneTrustUIElement = deepSearch(uiConfig, 'oneTrustCookieCategories');
      expect(oneTrustUIElement).toBeDefined();

      const ketchUIElement = deepSearch(uiConfig, 'ketchConsentPurposes');
      expect(ketchUIElement).toBeDefined();
    });
  });
});
