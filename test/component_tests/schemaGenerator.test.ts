import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

/**
 * Reads a file and returns its contents as a string.
 * Returns undefined if the file doesn't exist or cannot be read.
 *
 * @param filePath - Absolute path to the file to read
 * @returns File contents as string, or undefined if not found
 */
function readFile(filePath: string): string | undefined {
  let file;
  if (!fs.existsSync(filePath)) {
    return file;
  }

  try {
    file = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    /* empty */
  }

  return file;
}

/**
 * Reads and parses a JSON schema file.
 * Returns undefined if the file doesn't exist or cannot be parsed.
 *
 * @param filePath - Absolute path to the JSON schema file
 * @returns Parsed JSON schema object, or undefined if not found/invalid
 */
function readSchemaFile(filePath: string): any | undefined {
  let schema;
  if (!fs.existsSync(filePath)) {
    return schema;
  }

  try {
    schema = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e) {
    /* empty */
  }

  return schema;
}

/**
 * Writes data to a file at the specified path.
 *
 * @param filePath - Absolute path where the file should be written
 * @param data - Content to write to the file
 */
function writeFile(filePath: string, data: string | NodeJS.ArrayBufferView) {
  fs.writeFileSync(filePath, data);
}

describe('Schema Generator', () => {
  const configDir = 'test/component_tests/configurations';

  describe('should generate and save schema for the specified destination', () => {
    const testData = [
      {
        description: 'New UI',
        destName: 'create_new_schema_dest',
        expectedSchemaFile: 'createNewSchemaDest.json',
      },
      {
        description: 'Legacy UI',
        destName: 'create_new_schema_dest_legacy_ui',
        expectedSchemaFile: 'createNewSchemaDestLegacyUI.json',
      },
    ];

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    it.each(testData)('$description', ({ description, destName, expectedSchemaFile }) => {
      const cmd = `CONFIG_DIR=${configDir} npm run update:schema:destination "${destName}"`;

      execSync(cmd);

      const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);

      const schema = readSchemaFile(schemaFilePath);
      if (schema) {
        // delete the file
        fs.unlinkSync(schemaFilePath);
      }

      const expectedSchemaData = readSchemaFile(
        path.resolve(__dirname, `./data/${expectedSchemaFile}`),
      );

      expect(schema).toEqual(expectedSchemaData);
    });
  });

  describe('should not generate and save schema if update option is not provided for the specified destination', () => {
    const testData = [
      {
        description: 'New UI',
        destName: 'create_new_schema_dest',
      },
      {
        description: 'Legacy UI',
        destName: 'create_new_schema_dest_legacy_ui',
      },
    ];

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    it.each(testData)('$description', ({ description, destName }) => {
      const cmd = `CONFIG_DIR=${configDir} npm run check:schema:destination "${destName}"`;

      execSync(cmd);

      const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);

      const schema = readSchemaFile(schemaFilePath);
      expect(schema).toBeUndefined();
    });
  });

  describe('should update and save schema for the specified destination', () => {
    const testData = [
      {
        description: 'New UI',
        destName: 'update_schema_dest',
        expectedSchemaFile: 'updateSchemaDest.json',
      },
      {
        description: 'Legacy UI',
        destName: 'update_schema_dest_legacy_ui',
        expectedSchemaFile: 'updateSchemaDestLegacyUI.json',
      },
    ];

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    it.each(testData)('$description', ({ description, destName, expectedSchemaFile }) => {
      const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);
      const curSchema = readFile(schemaFilePath);

      const cmd = `CONFIG_DIR=${configDir} npm run update:schema:destination "${destName}"`;

      execSync(cmd);

      const schema = readSchemaFile(schemaFilePath);
      // Restore schema file
      if (curSchema) {
        writeFile(schemaFilePath, curSchema);
      }

      const expectedSchemaData = readSchemaFile(
        path.resolve(__dirname, `./data/${expectedSchemaFile}`),
      );

      expect(schema).toEqual(expectedSchemaData);
    });
  });

  describe('should not save the schema file if update option is not provided for the specified destination', () => {
    const testData = [
      {
        description: 'New UI',
        destName: 'update_schema_dest',
      },
      {
        description: 'Legacy UI',
        destName: 'update_schema_dest_legacy_ui',
      },
    ];

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    it.each(testData)('$description', ({ description, destName }) => {
      const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);
      const curSchema = readSchemaFile(schemaFilePath);

      const cmd = `CONFIG_DIR=${configDir} npm run check:schema:destination "${destName}"`;

      execSync(cmd);

      const schema = readSchemaFile(schemaFilePath);

      expect(schema).toEqual(curSchema);
    });
  });

  describe('should exclude ignored fields from diff', () => {
    const testData = [
      {
        description: 'Destination with ignored fields',
        destName: 'test_ignored_fields_dest',
      },
    ];

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    it.each(testData)(
      '$description - should not include ignored fields in diff',
      ({ description, destName }) => {
        const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);
        const curSchema = readSchemaFile(schemaFilePath);

        // Verify the current schema has the ignored fields
        expect(curSchema).toBeDefined();
        if (curSchema && 'configSchema' in curSchema) {
          const configSchema = (curSchema as any).configSchema;
          expect(configSchema.properties).toHaveProperty('oneTrustCookieCategories');
          expect(configSchema.properties).toHaveProperty('ketchConsentPurposes');
          expect(configSchema).toHaveProperty('additionalProperties');
        }

        // Run schema check - it should not detect differences in excluded fields
        const cmd = `CONFIG_DIR=${configDir} npm run check:schema:destination "${destName}"`;

        // This should run without errors even though consent fields differ
        expect(() => execSync(cmd, { stdio: 'pipe' })).not.toThrow();

        // Schema should remain unchanged
        const unchangedSchema = readSchemaFile(schemaFilePath);
        expect(unchangedSchema).toEqual(curSchema);
      },
    );
  });

  describe('should not remove any custom fields from schema (default behavior)', () => {
    const testData = [
      {
        description: 'New UI',
        destName: 'test_custom_fields_dest',
      },
    ];

    it.each(testData)(
      '$description - custom fields should not be removed from schema',
      ({ description, destName }) => {
        const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);
        const curSchema = readFile(schemaFilePath);

        const cmd = `CONFIG_DIR=${configDir} npm run update:schema:destination "${destName}"`;

        execSync(cmd);

        const updatedSchema = readSchemaFile(schemaFilePath);

        // Restore original schema
        if (curSchema) {
          writeFile(schemaFilePath, curSchema);
        }

        // Verify custom fields were not removed from schema
        expect(updatedSchema).toBeDefined();
        expect(updatedSchema).toHaveProperty('configSchema');
        expect(updatedSchema.configSchema.properties).toHaveProperty('customField');
      },
    );
  });

  describe('should delete any existing custom fields from schema when skip-deletions flag is not provided', () => {
    const testData = [
      {
        description: 'New UI',
        destName: 'test_custom_fields_dest',
      },
    ];

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    it.each(testData)(
      '$description - custom fields should be removed from schema',
      ({ description, destName }) => {
        const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);
        const curSchema = readFile(schemaFilePath);

        const cmd = `CONFIG_DIR=${configDir} python3 scripts/schemaGenerator.py destination -update -name "${destName}"`;

        execSync(cmd);

        const updatedSchema = readSchemaFile(schemaFilePath);

        // Restore original schema
        if (curSchema) {
          writeFile(schemaFilePath, curSchema);
        }

        // Verify custom fields were removed from schema
        expect(updatedSchema).toBeDefined();
        expect(updatedSchema).toHaveProperty('configSchema');
        expect(updatedSchema.configSchema.properties).not.toHaveProperty('customField');
      },
    );
  });
});
