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
  const createNewDestSchema = readSchemaFile(
    path.resolve(__dirname, './data/createNewDestSchema.json'),
  );

  it('should generate and save schema for the specified destination', () => {
    const destName = 'test_create_dest_ignore';
    const cmd = `npm run update:schema:destination "${destName}" -- -test`;

    execSync(cmd);

    const schemaFilePath = path.resolve(`src/configurations/destinations/${destName}/schema.json`);

    const schema = readSchemaFile(schemaFilePath);
    if (schema) {
      // delete the file
      fs.unlinkSync(schemaFilePath);
    }

    expect(schema).toEqual(createNewDestSchema);
  });
});
