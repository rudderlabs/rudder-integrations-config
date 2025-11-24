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

// Custom validation rule interface
interface ValidationRule {
  name: string;
  description: string;
  validate: (destDefConfig: Record<string, unknown>) => { isValid: boolean; errorMessage?: string };
}

// Destination definition validation rules
const destinationDefinitionRules: ValidationRule[] = [
  {
    name: 'includeKeys-excludeKeys-mutual-exclusion',
    description: 'includeKeys and excludeKeys cannot be defined at the same time',
    validate: (destDefConfig) => {
      const { includeKeys, excludeKeys } = destDefConfig.config as Record<string, unknown>;

      if (
        Array.isArray(includeKeys) &&
        Array.isArray(excludeKeys) &&
        includeKeys.length > 0 &&
        excludeKeys.length > 0
      ) {
        return {
          isValid: false,
          errorMessage:
            'config.includeKeys and config.excludeKeys cannot be defined at the same time',
        };
      }

      return { isValid: true };
    },
  },
  {
    name: 'secretKeys-not-in-includeKeys',
    description: 'Secret keys must not be in includeKeys to prevent client-side exposure',
    validate: (destDefConfig) => {
      const { secretKeys, includeKeys } = destDefConfig.config as Record<string, unknown>;

      if (
        Array.isArray(includeKeys) &&
        Array.isArray(secretKeys) &&
        includeKeys.length > 0 &&
        secretKeys.length > 0
      ) {
        const secretsInIncludeKeys = secretKeys.filter((key: string) => includeKeys.includes(key));
        if (secretsInIncludeKeys.length > 0) {
          return {
            isValid: false,
            errorMessage: `All fields in config.secretKeys must NOT be in config.includeKeys. Found: ${secretsInIncludeKeys.join(
              ', ',
            )}`,
          };
        }
      }

      return { isValid: true };
    },
  },
  {
    name: 'secretKeys-must-be-in-excludeKeys',
    description: 'When excludeKeys is defined, all secrets must be in excludeKeys',
    validate: (destDefConfig) => {
      const { secretKeys, excludeKeys } = destDefConfig.config as Record<string, unknown>;

      if (
        Array.isArray(excludeKeys) &&
        Array.isArray(secretKeys) &&
        excludeKeys.length > 0 &&
        secretKeys.length > 0
      ) {
        const secretsNotInExcludeKeys = secretKeys.filter(
          (key: string) => !excludeKeys.includes(key),
        );
        if (secretsNotInExcludeKeys.length > 0) {
          return {
            isValid: false,
            errorMessage: `All fields in config.secretKeys must be in config.excludeKeys. Missing: ${secretsNotInExcludeKeys.join(
              ', ',
            )}`,
          };
        }
      }

      return { isValid: true };
    },
  },
  {
    name: 'includeKeys-must-be-defined-when-device-hybrid-mode-is-supported',
    description: 'includeKeys must be defined when device/hybrid mode is supported',
    validate: (destDefConfig) => {
      const { supportedConnectionModes, includeKeys } = destDefConfig.config as Record<
        string,
        unknown
      >;

      const isDeviceModeSupported =
        supportedConnectionModes &&
        Object.values(supportedConnectionModes).some(
          (modes: string[]) => modes.includes('device') || modes.includes('hybrid'),
        );

      if (isDeviceModeSupported && !includeKeys) {
        return {
          isValid: false,
          errorMessage: 'config.includeKeys must be defined when device/hybrid mode is supported',
        };
      }

      return { isValid: true };
    },
  },
];

function applyAdditionalRulesValidation(destDefConfig: Record<string, unknown>): void {
  const errors: string[] = [];

  destinationDefinitionRules.forEach((rule) => {
    const result = rule.validate(destDefConfig);
    if (!result.isValid && result.errorMessage) {
      errors.push(result.errorMessage);
    }
  });

  if (errors.length > 0) {
    throw new Error(JSON.stringify(errors));
  }
}

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

export async function validateDestinationDefinitions(
  destDefConfig: Record<string, unknown>,
): Promise<boolean> {
  const ddAjv = new Ajv({
    allErrors: true,
    useDefaults: true,
    strict: true,
    strictSchema: true,
    strictRequired: true,
    strictNumbers: true,
    strictTypes: true,
    strictTuples: true,
  });

  const validator = ddAjv.compile(
    await importJsonFromFile(path.join(__dirname, '../schemas/destinations/db-config-schema.json')),
  );

  if (validator && !validator(destDefConfig) && validator.errors) {
    const errorMessages: string[] = validator.errors.map((e) => {
      const propertyName = e.instancePath.slice(1).replace(/\//g, '.');
      return `${propertyName} ${e.message}`;
    });

    throw new Error(JSON.stringify(errorMessages));
  }

  // Apply custom validation rules
  applyAdditionalRulesValidation(destDefConfig);

  return true;
}

export async function validateSourceDefinitions(
  srcDefConfig: Record<string, unknown>,
): Promise<boolean> {
  const ddAjv = new Ajv({
    allErrors: true,
    useDefaults: true,
    strict: true,
    strictSchema: true,
    strictRequired: true,
    strictNumbers: true,
    strictTypes: true,
    strictTuples: true,
  });

  const validator = ddAjv.compile(
    await importJsonFromFile(path.join(__dirname, '../schemas/sources/db-config-schema.json')),
  );

  if (validator && !validator(srcDefConfig) && validator.errors) {
    const errorMessages: string[] = validator.errors.map((e) => {
      const propertyName = e.instancePath.slice(1).replace(/\//g, '.');
      return `${propertyName} ${e.message}`;
    });

    throw new Error(JSON.stringify(errorMessages));
  }
  return true;
}

export async function validateAccountDefinitions(
  accDefConfig: Record<string, unknown>,
): Promise<boolean> {
  const ddAjv = new Ajv({
    allErrors: true,
    useDefaults: true,
    strict: true,
    strictSchema: true,
    strictRequired: true,
    strictNumbers: true,
    strictTypes: true,
    strictTuples: true,
  });

  const validator = ddAjv.compile(
    await importJsonFromFile(
      path.join(__dirname, '../schemas/account/account-db-config-schema.json'),
    ),
  );

  if (validator && !validator(accDefConfig) && validator.errors) {
    const errorMessages: string[] = validator.errors.map((e) => {
      const propertyName = e.instancePath.slice(1).replace(/\//g, '.');
      return `${propertyName} ${e.message}`;
    });

    throw new Error(JSON.stringify(errorMessages));
  }
  return true;
}

export async function init() {
  validators = {};
  await initAjvValidators();
}

export default {
  validateConfig,
  validateSourceDefinitions,
  validateDestinationDefinitions,
  validateAccountDefinitions,
  init,
};
