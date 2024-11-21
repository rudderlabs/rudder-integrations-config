/* eslint-disable no-param-reassign */
import { promises as fs } from 'fs';
import { Command } from 'commander';
import path from 'path';
import { DYNAMIC_CONFIG_FIELDS } from './constants';
import { removeDefaultSubRegex, postProcessing } from './utils';

const program = new Command();

interface SchemaField {
  type: string;
  pattern?: string;
  properties?: Record<string, SchemaField>;
  items?: SchemaField;
  from?: SchemaField;
  to?: SchemaField;
  if?: {
    properties?: Record<string, SchemaField>;
    then?: {
      properties?: Record<string, SchemaField>;
    };
    else?: {
      properties?: Record<string, SchemaField>;
    };
  };
  then?: {
    properties?: Record<string, SchemaField>;
  };
  else?: {
    properties?: Record<string, SchemaField>;
  };
  [key: string]: unknown;
}

interface Schema {
  configSchema: {
    type: string;
    properties: Record<string, SchemaField>;
    [key: string]: unknown;
  };
}

const DESTINATIONS_ROOT = './src/configurations/destinations';

const processSchemaField = (
  field: SchemaField,
  fieldPath: string[],
  dynamicFields: string[],
): void => {
  // Get the field name from the path
  const fieldName = fieldPath[fieldPath.length - 1];
  const isFieldDynamic = dynamicFields.includes(fieldName);

  // Process pattern if present
  if (field.pattern && !isFieldDynamic) {
    field.pattern = removeDefaultSubRegex(field.pattern);
  }

  // Process mapping fields (from/to)
  if (field.from) {
    processSchemaField(field.from, [...fieldPath, 'from'], dynamicFields);
  }
  if (field.to) {
    processSchemaField(field.to, [...fieldPath, 'to'], dynamicFields);
  }

  // Process nested properties
  if (field.properties) {
    Object.entries(field.properties).forEach(([key, value]) => {
      processSchemaField(value, [...fieldPath, key], dynamicFields);
    });
  }

  // Process conditional properties
  if (field.if) {
    // Process if properties
    if (field.if.properties) {
      Object.entries(field.if.properties).forEach(([key, value]) => {
        processSchemaField(value, [...fieldPath, 'if', key], dynamicFields);
      });
    }
    // Process then properties
    if (field.if.then?.properties) {
      Object.entries(field.if.then.properties).forEach(([key, value]) => {
        processSchemaField(value, [...fieldPath, 'then', key], dynamicFields);
      });
    }
    // Process else properties
    if (field.if.else?.properties) {
      Object.entries(field.if.else.properties).forEach(([key, value]) => {
        processSchemaField(value, [...fieldPath, 'else', key], dynamicFields);
      });
    }
  }

  // Process direct then properties
  if (field.then?.properties) {
    Object.entries(field.then.properties).forEach(([key, value]) => {
      processSchemaField(value, [...fieldPath, 'then', key], dynamicFields);
    });
  }

  // Process direct else properties
  if (field.else?.properties) {
    Object.entries(field.else.properties).forEach(([key, value]) => {
      processSchemaField(value, [...fieldPath, 'else', key], dynamicFields);
    });
  }

  // Process array items
  if (field.items) {
    processSchemaField(field.items, [...fieldPath, 'items'], dynamicFields);
  }
};

const processSchema = async (destination: string, schemaPath: string): Promise<void> => {
  try {
    const content = await fs.readFile(schemaPath, 'utf8');
    const schema: Schema = JSON.parse(content);

    const dynamicFields = DYNAMIC_CONFIG_FIELDS[destination.toUpperCase()] || [];

    // Process all fields recursively
    Object.entries(schema.configSchema.properties).forEach(([key, value]) => {
      processSchemaField(value, [key], dynamicFields);
    });

    const modifiedSchemaPath = path.join(DESTINATIONS_ROOT, destination, 'schema.json');
    // Write the modified schema back to file
    await fs.writeFile(modifiedSchemaPath, JSON.stringify(schema, null, 2), 'utf8');
    console.log(`✅ Processed ${destination}`);
  } catch (error) {
    console.error(
      `❌ Error processing ${destination}:`,
      error instanceof Error ? error.message : String(error),
    );
  }
};

program.option('-d, --destination <string>', 'Destination to process').parse(process.argv);

const main = async (): Promise<void> => {
  try {
    const options = program.opts();
    // Read all destination directories
    const destinations = await fs.readdir(DESTINATIONS_ROOT);

    let destinationsToProcess: string[];
    if (options.destination) {
      if (options.destination.includes(',')) {
        destinationsToProcess = options.destination
          .split(',')
          .filter((dest: string) => destinations.includes(dest.trim()));
      } else {
        destinationsToProcess = [options.destination];
      }
    } else {
      destinationsToProcess = destinations;
    }

    // Process each destination
    await Promise.all(
      destinationsToProcess.map(async (destination) => {
        const schemaPath = path.join(DESTINATIONS_ROOT, destination, 'schema.json');

        try {
          await fs.access(schemaPath);
          await processSchema(destination, schemaPath);
        } catch (error) {
          if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
            console.log(`⚠️ No schema.json found for ${destination}`);
          } else {
            console.error(
              `❌ Error accessing ${destination}:`,
              error instanceof Error ? error.message : String(error),
            );
          }
        }
      }),
    );

    console.log('🎉 Processing complete!');

    // Run formatting commands
    await postProcessing();
  } catch (error) {
    console.error('Fatal error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
};

main();
