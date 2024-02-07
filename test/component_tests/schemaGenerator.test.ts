import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

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

      const newSchemaData = readSchemaFile(path.resolve(__dirname, `./data/${expectedSchemaFile}`));

      expect(schema).toEqual(newSchemaData);
    });
  });
});
