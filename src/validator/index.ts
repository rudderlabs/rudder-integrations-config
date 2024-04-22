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

const addCommonSchema = async () => {
  if (!ajv.getSchema('commonSourcesSchema.json')) {
    const commonSourcesSchema = await importJsonFromFile(
     path.join(__dirname, '../configurations/sources/commonSchema.json'),
    );
    ajv.addSchema(commonSourcesSchema);
  }
  

  if (!ajv.getSchema('commonDestinationsSchema.json')) {
    const commonDestinationsSchema = await importJsonFromFile(
      path.join(__dirname, '../configurations/destinations/commonSchema.json'),
    );
    ajv.addSchema(commonDestinationsSchema);
  }
};

async function initAjvValidators() {
  await addCommonSchema();
  const files = await glob(path.join(__dirname, '../configurations/**/*schema.json'));
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

export async function validateDestinationDefinitions(destDefConfig: any): Promise<boolean> {
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

  return true;
}

export async function validateSourceDefinitions(srcDefConfig: any): Promise<boolean> {
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

export async function init() {
  validators = {};
  await initAjvValidators();
}
