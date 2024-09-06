import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

function readFile(filePath): string | undefined {
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

function readSchemaFile(filePath): string | undefined {
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

function writeFile(filePath, data) {
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
});
