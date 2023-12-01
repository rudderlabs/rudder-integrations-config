import fs from 'fs';
import path from 'path';
import glob from 'glob';
import Ajv, { ValidateFunction } from 'ajv';

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

let validators: Record<string, ValidateFunction> = {};

async function importJsonFromFile(file: string) {
  const content = await fs.promises.readFile(file, { encoding: 'utf-8' });
  return JSON.parse(content);
}

async function initAjvValidators() {
  const files = await glob(path.join(__dirname, '../configurations/**/schema.json'));
  const filePromises = files.map(importJsonFromFile);
  const contents = await Promise.all(filePromises);

  files.forEach((file, i) => {
    const intgDir = path.dirname(file);
    const intgName = path.basename(intgDir);
    const intgType = path.basename(path.dirname(intgDir));
    validators[`${intgType}___${intgName}`] = ajv.compile(contents[i].configSchema || {});
  });
}

export function validateConfig(
  definitionName: string,
  config: Record<string, unknown>,
  intgType: string,
  throwErrorOnMissingValidations = false,
) {
  if (!definitionName) {
    throw new Error('Missing definitionName');
  }

  const validationMethod = validators[`${intgType}___${definitionName}`];
  if (!validationMethod && throwErrorOnMissingValidations) {
    throw new Error(`No validation method found for definition ${definitionName}`);
  }

  if (validationMethod && !validationMethod(config) && validationMethod.errors) {
    const errorMessages = validationMethod.errors.map((e) => {
      const propertyName = e.instancePath.slice(1).replace(/\//g, '.');
      return `${propertyName} ${e.message}`;
    });

    throw new Error(JSON.stringify(errorMessages));
  }
}

export function validateHybridModeCloudConfig(destinationDefinition: any): boolean {
  const isObject = (val: any): boolean => {
    // invalid types condition check
    if (!val || typeof val !== 'object' || Array.isArray(val)) {
      return false;
    }
    return true;
  };

  const checkForValidObjectAndValidateWithMasterList = (
    inputValues: any,
    masterList: string[],
    logKeys: { location: string; subsetName: string; masterName: string },
  ): { isValid: boolean; valList: string[] } => {
    if (!isObject(inputValues)) {
      return { isValid: false, valList: [] };
    }
    const subsetValues = Object.keys(inputValues);
    // no subset defined
    if (subsetValues.length === 0) {
      return { isValid: false, valList: [] };
    }

    const isSubsetOfMasterList = subsetValues.every((child) => masterList.includes(child));
    if (!isSubsetOfMasterList) {
      console.error(
        `The ${logKeys.subsetName} mentioned in ${logKeys.location} does not exist in ${logKeys.masterName}`,
      );
      return { isValid: false, valList: [] };
    }
    return { isValid: true, valList: subsetValues };
  };
  if (destinationDefinition?.config?.hybridModeCloudEventsFilter) {
    const { hybridModeCloudEventsFilter, supportedSourceTypes } = destinationDefinition.config;

    const { isValid: isSourceTypeValid, valList: sourceTypes } =
      checkForValidObjectAndValidateWithMasterList(
        hybridModeCloudEventsFilter,
        supportedSourceTypes,
        {
          masterName: 'supportedSourceTypes',
          location: 'hybridModeCloudEventsFilter.[sourceType]',
          subsetName: 'source type',
        },
      );
    // no source-types defined
    if (!isSourceTypeValid) {
      console.error(
        'The supported source type mentioned in hybridModeCloudEventsFilter does not exist in supportedSourceTypes',
      );
      return false;
    }
    const supportedEventProperties = ['messageType'];

    return sourceTypes.some((srcType: string) => {
      const sourceTypeFilterMap = hybridModeCloudEventsFilter[srcType];
      const { isValid: isValidEventProperties, valList: eventProperties } =
        checkForValidObjectAndValidateWithMasterList(
          sourceTypeFilterMap,
          supportedEventProperties,
          {
            masterName: `${supportedEventProperties}`,
            location: '',
            subsetName: `${Object.keys(hybridModeCloudEventsFilter[srcType])}`,
          },
        );
      if (!isValidEventProperties) {
        return false;
      }

      // basic-check
      return eventProperties.some((eventProperty) =>
        Array.isArray(sourceTypeFilterMap[eventProperty]),
      );
    });
  }
  return true;
}

export async function validateDestinationDefinitions(destDefConfig: any): Promise<boolean> {
  const validator = ajv.compile(
    await importJsonFromFile(path.join(__dirname, '../schemas/db-config-schema.json')),
  );

  if (validator && !validator(destDefConfig) && validator.errors) {
    const errorMessages: string[] = validator.errors.map((e) => {
      const propertyName = e.instancePath.slice(1).replace(/\//g, '.');
      return `${propertyName} ${e.message}`;
    });

    throw new Error(JSON.stringify(errorMessages));
  }

  // hybridModeCloudEventsFilter check -- STARTS
  const isValidHybridModeCloudConfig = validateHybridModeCloudConfig(destDefConfig);
  // hybridModeCloudEventsFilter check -- ENDS
  return isValidHybridModeCloudConfig;
}

export function validateSourceType(sourceDefinition: any) {
  // currently these are the valid source-types according to the ServiceUtil.getSourceType logic in config-backend
  const validSourceTypes = [
    'cloud',
    'cloudSource',
    'warehouse',
    'web',
    'android',
    'ios',
    'unity',
    'reactnative',
    'amp',
    'flutter',
    'cordova',
    'shopify',
  ];
  return validSourceTypes.includes(sourceDefinition?.type);
}

export async function validateSourceDefinitions(srcName: string): Promise<boolean> {
  const sourceDefinition = await import(`../configurations/sources/${srcName}/db-config.json`);
  // SourceDefinition.type validation -- STARTS
  const isValidSourceType = validateSourceType(sourceDefinition);
  // SourceDefinition.type validation -- ENDS
  return isValidSourceType;
}

export async function init() {
  validators = {};
  await initAjvValidators();
}
