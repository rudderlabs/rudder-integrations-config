/* eslint-disable no-lonely-if */
/* eslint-disable no-param-reassign */
import { promises as fs } from 'fs';
import { Command } from 'commander';
import path from 'path';
import { DYNAMIC_CONFIG_FIELDS } from './constants';
import {
  DynamicCustomFormField,
  Field,
  isOldStyleConfig,
  UIConfig,
  OldStyleUIConfig,
  NewStyleUIConfig,
} from './types';
import { removeDefaultSubRegex, postProcessing } from './utils';
import { processUIConfigTemplate } from './process-ui-config-template';

const program = new Command();

const DESTINATIONS_ROOT = './src/configurations/destinations';

const newUiConfigDestinations: string[] = [];

const isDynamicConfigSupportedField = (
  field: Field | DynamicCustomFormField,
  dynamicFields: string[],
): boolean => {
  const key = field.value || field.configKey || '';
  return dynamicFields.includes(key);
};

const processField = async (
  field: Field | DynamicCustomFormField,
  destination: string,
  dynamicFields: string[],
): Promise<void> => {
  // Check if this field's value is in dynamicFields
  if (isDynamicConfigSupportedField(field, dynamicFields)) {
    field.dynamicConfigSupported = true;
  } else {
    // Process regex if not a dynamic field
    if (field.regex) {
      field.regex = removeDefaultSubRegex(field.regex);
    }
  }

  // Recursively process nested fields in customFields
  if ('customFields' in field && Array.isArray(field.customFields)) {
    await Promise.all(
      field.customFields.map(async (customField: any) => {
        await processField(customField, destination, dynamicFields);
      }),
    );
  }

  // Recursively process nested fields in fields
  if ('fields' in field && Array.isArray(field.fields)) {
    await Promise.all(
      field.fields.map(async (subField) => {
        await processField(subField, destination, dynamicFields);
      }),
    );
  }
};

const processUIConfig = async (destination: string, configPath: string): Promise<void> => {
  try {
    // import d from '../../configurations/destinations/algolia/ui-config.json'
    const content = await import(configPath);
    const config: UIConfig = content.default;

    const dynamicFields = DYNAMIC_CONFIG_FIELDS[destination.toUpperCase()] || [];

    if (isOldStyleConfig(config.uiConfig as OldStyleUIConfig)) {
      // Process all sections
      await Promise.all(
        (config.uiConfig as OldStyleUIConfig).map(async (section) => {
          if (section.fields) {
            await Promise.all(
              section.fields.map((field: any) => processField(field, destination, dynamicFields)),
            );
          }
        }),
      );
    } else {
      // Process new style config using the template processor
      processUIConfigTemplate(config.uiConfig as NewStyleUIConfig, dynamicFields);
    }

    const modifiedConfigPath = path.join(DESTINATIONS_ROOT, destination, 'ui-config.json');
    // Write the modified config back to file
    await fs.writeFile(modifiedConfigPath, JSON.stringify(config, null, 2), 'utf8');
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
        const uiConfigPath = path.join(
          '../..',
          'configurations',
          'destinations',
          destination,
          'ui-config.json',
        );

        // Check if ui-config.json exists
        try {
          await processUIConfig(destination, uiConfigPath);
        } catch (error) {
          if (error instanceof Error && 'code' in error && error.code === 'ENOENT') {
            console.log(`⚠️ No ui-config.json found for ${destination}`);
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
    await postProcessing();
  } catch (error) {
    console.error('Fatal error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
};

main();
