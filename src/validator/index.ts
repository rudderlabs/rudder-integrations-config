import fs from 'fs';
import path from 'path';
import glob from 'glob';
import { promisify } from 'util';
import Ajv, { ValidateFunction } from 'ajv';

const globPromisified = promisify(glob);
const readFile = promisify(fs.readFile);

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
  const content = await readFile(file, { encoding: 'utf-8' });
  return JSON.parse(content);
}

async function initAjvValidators() {
  const files = await globPromisified(
    path.join(__dirname, '../configurations/**/schema.json'),
  );
  const filePromises = files.map(importJsonFromFile);
  const contents = await Promise.all(filePromises);

  files.forEach((file, i) => {
    const intgDir = path.dirname(file);
    const intgName = path.basename(intgDir);
    const intgType = path.basename(path.dirname(intgDir));
    validators[`${intgType}___${intgName}`] = ajv.compile(contents[i]['configSchema'] || {});
  });
}

export function validateConfig(
  definitionName: string,
  config: any,
  intgType: string,
  throwErrorOnMissingValidations: boolean = false,
) {
  if (!definitionName) {
    throw new Error('Missing definitionName');
  }

  const validationMethod = validators[`${intgType}___${definitionName}`];
  if (!validationMethod && throwErrorOnMissingValidations) {
    throw new Error(`No validation method found for definition ${definitionName}`);
  }

  if (validationMethod && !validationMethod(config)) {
    let errorMessages: string[] = [];
    if (validationMethod.errors?.length) {
      errorMessages = validationMethod.errors.map((e) => {
        const propertyName = e.instancePath.slice(1).replace(/\//g, '.');
        return `${propertyName} ${e.message}`;
      });
    }

    throw new Error(JSON.stringify(errorMessages));
  }
}

export function init() {
  validators = {};
  initAjvValidators();
}
