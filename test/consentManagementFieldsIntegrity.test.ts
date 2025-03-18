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
    console.error(`Unable to load file: "${filePath}"`);
    return null;
  }
};

const deepSearch = (obj: any, value: string, count = 0) => {
  // eslint-disable-next-line no-restricted-syntax, guard-for-in
  for (const k in obj) {
    if (typeof obj[k] === 'object') {
      // eslint-disable-next-line no-param-reassign
      count = deepSearch(obj[k], value, count);
    } else if (obj[k] === value) {
      // eslint-disable-next-line no-param-reassign
      count += 1;
    }
  }
  return count;
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
    const { destConfig, supportedSourceTypes, includeKeys } = dbConfig.config;

    it(`should have oneTrustCookieCategories and ketchConsentPurposes fields defined per source type instead of the defaultConfig for ${destName}`, () => {
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

      // Remove defaultConfig from the list of source types
      const destConfigSrcTypes = Object.keys(destConfig);
      destConfigSrcTypes.splice(destConfigSrcTypes.indexOf('defaultConfig'), 1);
      expect(destConfigSrcTypes.sort()).toEqual(supportedSourceTypes.sort());
    });

    it(`should have consentManagement field defined per source type for ${destName}`, () => {
      const { defaultConfig } = destConfig;

      expect(defaultConfig.includes('consentManagement')).toBe(false);

      let fail = false;
      supportedSourceTypes.forEach((srcType: string) => {
        if (!destConfig[srcType].includes('consentManagement')) {
          fail = true;
        }
      });

      expect(fail).toBe(false);

      // Remove defaultConfig from the list of source types
      const destConfigSrcTypes = Object.keys(destConfig);
      destConfigSrcTypes.splice(destConfigSrcTypes.indexOf('defaultConfig'), 1);
      expect(destConfigSrcTypes.sort()).toEqual(supportedSourceTypes.sort());
    });

    it(`should have oneTrustCookieCategories and ketchConsentPurposes fields defined in includeKeys for ${destName}`, () => {
      if (includeKeys) {
        expect(includeKeys.includes('oneTrustCookieCategories')).toBe(true);
        expect(includeKeys.includes('ketchConsentPurposes')).toBe(true);
      }
    });

    it(`should have consentManagement field defined in includeKeys for ${destName}`, () => {
      if (includeKeys) {
        expect(includeKeys.includes('consentManagement')).toBe(true);
      }
    });

    // Validate schema.json
    const schemaFilePath = path.resolve(`${destDir}/${destName}/schema.json`);
    const schema = getJSONDataFromFile(schemaFilePath);

    it(`should have oneTrustCookieCategories and ketchConsentPurposes fields properly defined in schema.json for ${destName}`, () => {
      expect(schema.configSchema.properties.oneTrustCookieCategories).toBeDefined();
      expect(schema.configSchema.properties.ketchConsentPurposes).toBeDefined();

      expect(schema.configSchema.properties.oneTrustCookieCategories.type).toBe('object');
      expect(schema.configSchema.properties.ketchConsentPurposes.type).toBe('object');

      expect(schema.configSchema.properties.oneTrustCookieCategories.properties).toBeDefined();
      expect(schema.configSchema.properties.ketchConsentPurposes.properties).toBeDefined();

      expect(
        Object.keys(schema.configSchema.properties.oneTrustCookieCategories.properties).sort(),
      ).toEqual(supportedSourceTypes.sort());
      expect(
        Object.keys(schema.configSchema.properties.ketchConsentPurposes.properties).sort(),
      ).toEqual(supportedSourceTypes.sort());
    });

    it(`should have consentManagement field properly defined in schema.json for ${destName}`, () => {
      expect(schema.configSchema.properties.consentManagement).toBeDefined();

      expect(schema.configSchema.properties.consentManagement.type).toBe('object');

      expect(schema.configSchema.properties.consentManagement.properties).toBeDefined();

      expect(
        Object.keys(schema.configSchema.properties.consentManagement.properties).sort(),
      ).toEqual(supportedSourceTypes.sort());
    });

    // it(`should have iubenda in consentManagement options in enum field properly defined in schema.json for ${destName}`, () => {
    //   const iubendaCount = deepSearch(schema, 'iubenda');
    //   const ketchCount = deepSearch(schema, 'ketch');
    //   expect(iubendaCount).toEqual(ketchCount);
    // });

    // // Validate ui-config.json
    // const uiConfigFilePath = path.resolve(`${destDir}/${destName}/ui-config.json`);
    // const uiConfig = getJSONDataFromFile(uiConfigFilePath);

    // it(`should not have oneTrustCookieCategories and ketchConsentPurposes fields defined in ui-config.json for ${destName}`, () => {
    //   const oneTrustUIElementCount = deepSearch(uiConfig, 'oneTrustCookieCategories');
    //   expect(oneTrustUIElementCount).toEqual(0);

    //   const ketchUIElementCount = deepSearch(uiConfig, 'ketchConsentPurposes');
    //   expect(ketchUIElementCount).toEqual(0);
    // });

    // it(`should have consentManagement field properly defined in ui-config.json for ${destName}`, () => {
    //   const consentManagementUIElementCount = deepSearch(uiConfig, 'consentManagement');
    //   expect(consentManagementUIElementCount).toEqual(1);
    // });

    // it(`should have iubenda in customFields field properly defined in ui-config.json for ${destName}`, () => {
    //   const consentManagementUIElementCount = deepSearch(uiConfig, 'iubenda');
    //   expect(consentManagementUIElementCount).toEqual(2);
    // });
  });
});
