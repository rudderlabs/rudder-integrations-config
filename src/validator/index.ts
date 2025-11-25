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
  description: string;
  ignore?: boolean;
  validate: (destDefConfig: Record<string, unknown>) => { isValid: boolean; errorMessage?: string };
}

// Destination definition validation rules
const destinationDefinitionRules: ValidationRule[] = [
  {
    description: 'Secret keys must not be in includeKeys unless also in excludeKeys',
    validate: (destDefConfig) => {
      const { secretKeys, includeKeys, excludeKeys } = destDefConfig.config as Record<
        string,
        unknown
      >;

      if (
        Array.isArray(includeKeys) &&
        Array.isArray(secretKeys) &&
        includeKeys.length > 0 &&
        secretKeys.length > 0
      ) {
        // Find secrets in includeKeys that are NOT in excludeKeys
        // (excludeKeys wins when a key is in both)
        const secretsInIncludeKeys = secretKeys.filter(
          (key: string) =>
            includeKeys.includes(key) && !(Array.isArray(excludeKeys) && excludeKeys.includes(key)),
        );

        if (secretsInIncludeKeys.length > 0) {
          return {
            isValid: false,
            errorMessage: `Secret keys must not be exposed to client-side. Found in config.includeKeys but not in config.excludeKeys: ${secretsInIncludeKeys.join(
              ', ',
            )}. Add these to config.excludeKeys to prevent exposure.`,
          };
        }
      }

      return { isValid: true };
    },
  },
  {
    description:
      'includeKeys must be defined when at least one source type supports device/hybrid mode',
    validate: (destDefConfig) => {
      const { supportedConnectionModes, includeKeys } = destDefConfig.config as Record<
        string,
        unknown
      >;

      const isDeviceModeSupported =
        supportedConnectionModes &&
        Object.values(supportedConnectionModes).some(
          (modes: unknown) =>
            Array.isArray(modes) && (modes.includes('device') || modes.includes('hybrid')),
        );

      if (isDeviceModeSupported && (!Array.isArray(includeKeys) || includeKeys.length === 0)) {
        return {
          isValid: false,
          errorMessage:
            'config.includeKeys must be defined and non-empty when at least one source type supports device/hybrid mode',
        };
      }

      return { isValid: true };
    },
  },
  {
    description: 'includeKeys must not be defined when the destination only supports cloud mode',
    // TODO: Remove the ignore flag once we have cleaned up all the destination definitions
    ignore: true,
    validate: (destDefConfig) => {
      const { supportedConnectionModes, includeKeys } = destDefConfig.config as Record<
        string,
        unknown
      >;

      if (
        supportedConnectionModes &&
        Object.values(supportedConnectionModes).every((modes: string[]) => modes.includes('cloud'))
       && Array.isArray(includeKeys) && includeKeys.length > 0) {
          return {
            isValid: false,
            errorMessage:
              'config.includeKeys must not be defined when the destination only supports cloud mode',
          };
        }

      return { isValid: true };
    },
  },
  {
    description:
      'includeKeys and excludeKeys must not be defined when the destination only supports cloud mode',
    // TODO: Remove the ignore flag once we have cleaned up all the destination definitions
    ignore: true,
    validate: (destDefConfig) => {
      const { supportedConnectionModes, includeKeys, excludeKeys } = destDefConfig.config as Record<
        string,
        unknown
      >;

      if (
        supportedConnectionModes &&
        Object.values(supportedConnectionModes).every((modes: string[]) => modes.includes('cloud'))
       && (
          (Array.isArray(includeKeys) && includeKeys.length > 0) ||
          (Array.isArray(excludeKeys) && excludeKeys.length > 0)
        )) {
          return {
            isValid: false,
            errorMessage:
              'config.includeKeys and config.excludeKeys must not be defined when the destination only supports cloud mode',
          };
        }

      return { isValid: true };
    },
  },
];

function applyAdditionalRulesValidation(destDefConfig: Record<string, unknown>): void {
  const errors: string[] = [];

  destinationDefinitionRules.forEach((rule) => {
    if (rule.ignore) {
      return;
    }
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
