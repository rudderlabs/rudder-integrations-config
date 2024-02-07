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

  it('should generate and save schema for the specified destination', () => {
    const newSchemaData = readSchemaFile(
      path.resolve(__dirname, './data/createNewSchemaDest.json'),
    );

    const destName = 'create_new_schema_dest';
    const cmd = `CONFIG_DIR=${configDir} npm run update:schema:destination "${destName}"`;

    execSync(cmd);

    const schemaFilePath = path.resolve(`${configDir}/destinations/${destName}/schema.json`);

    const schema = readSchemaFile(schemaFilePath);
    if (schema) {
      // delete the file
      fs.unlinkSync(schemaFilePath);
    }

    expect(schema).toEqual(newSchemaData);
  });
});
