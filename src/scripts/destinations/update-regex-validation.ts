import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { Command } from 'commander';
import { removeDefaultSubRegex, hasDynamicConfigSupport, postProcessing } from './utils';

const program = new Command();

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

program.option('-d, --destination <string>', 'Destination to process').parse(process.argv);

interface ValidationTest {
  config: Record<string, any>;
  result: boolean;
  err?: string[];
}

interface SchemaJson {
  configSchema: {
    properties: Record<string, any>;
  };
}

function findPatternInSchema(
  properties: Record<string, any>,
  fieldPath: string[],
): string | undefined {
  if (fieldPath.length === 0) return undefined;

  const currentField = fieldPath[0];
  const property = properties[currentField];

  if (!property) return undefined;

  // Check current level for pattern
  if (property.pattern) {
    return property.pattern;
  }

  // If there are more fields in the path, check nested properties
  if (fieldPath.length > 1) {
    if (property.properties) {
      return findPatternInSchema(property.properties, fieldPath.slice(1));
    }
    if (property.items?.properties) {
      return findPatternInSchema(property.items.properties, fieldPath.slice(1));
    }
  }

  return undefined;
}

async function processValidationFile(validationPath: string, schemaJsonPath: string) {
  try {
    const validationContent = await readFile(validationPath, 'utf8');
    const schemaJsonContent = await readFile(schemaJsonPath, 'utf8');

    const validationTests: ValidationTest[] = JSON.parse(validationContent);
    const schemaJson: SchemaJson = JSON.parse(schemaJsonContent);

    const updatedTests = validationTests.map((test) => {
      if (!test.err) return test;

      const updatedErrors = test.err.map((error) => {
        const fieldMatch = error.match(/^([\d.A-Za-z]+) must match pattern/);
        if (!fieldMatch) return error;

        const fieldPath = fieldMatch[1].split('.');
        const pattern = findPatternInSchema(schemaJson.configSchema.properties, fieldPath);

        if (!pattern || !hasDynamicConfigSupport(pattern)) {
          return removeDefaultSubRegex(error);
        }
        return error;
      });

      return {
        ...test,
        err: updatedErrors,
      };
    });

    await writeFile(validationPath, JSON.stringify(updatedTests, null, 2), 'utf8');

    console.log(`Successfully processed ${validationPath}`);
  } catch (error) {
    console.error(`Error processing ${validationPath}:`, error);
  }
}

async function main() {
  const destinationsDir = path.join(__dirname, '../../../test/data/validation/destinations');
  const uiConfigDir = path.join(__dirname, '../../configurations/destinations');

  const files = fs.readdirSync(destinationsDir);
  const options = program.opts();

  await Promise.all(
    files
      .filter(
        (file) =>
          file.endsWith('.json') &&
          (file.replace('.json', '').includes(options.destination) || !options.destination),
      )
      .map(async (file) => {
        const destinationName = file.replace('.json', '');
        const validationPath = path.join(destinationsDir, file);
        const schemaJsonPath = path.join(uiConfigDir, destinationName, 'schema.json');

        if (fs.existsSync(schemaJsonPath)) {
          await processValidationFile(validationPath, schemaJsonPath);
        }
      }),
  );
  await postProcessing();
}

main().catch(console.error);
