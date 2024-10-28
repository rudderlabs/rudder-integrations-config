/* eslint-disable no-console */
import { compile } from 'json-schema-to-typescript';
import fs from 'fs';
import path from 'path';

// Set the base directory for destination schemas
const baseDir = './src/configurations/destinations';
const indexFilePath = path.join(baseDir, 'index.d.ts');

// Function to generate types for each destination schema
const generateTypes = async (destination) => {
    const dbConfigPath = path.join(baseDir, destination, 'db-config.json');
    const schemaPath = path.join(baseDir, destination, 'schema.json');
    const outputPath = path.join(baseDir, destination, 'schema.d.ts');

    if (fs.existsSync(schemaPath)) {
        try {
            const dbConfig = JSON.parse(fs.readFileSync(dbConfigPath, { encoding: 'utf-8' }));
            const schemaFileData = JSON.parse(fs.readFileSync(schemaPath, { encoding: 'utf-8' }));
            if (!schemaFileData.configSchema) {
                throw new Error(`No configSchema found for ${destination}`);
            }
            const schema = schemaFileData.configSchema;
            schema.title = dbConfig.name;
            const ts = await compile(schema);
            fs.writeFileSync(outputPath, ts);
            console.log(`Generated types for ${destination}`);
        } catch (error) {
            console.error(`Error generating types for ${destination}:`, error);
        }
    } else {
        console.log(`No schema.json found for ${destination}`);
    }
};

// Function to generate the index.d.ts file
const generateIndexFile = () => {
    let exportStatements = '';

    fs.readdirSync(baseDir).forEach((destination) => {
        const schemaFilePath = path.join(baseDir, destination, 'schema.d.ts');
        if (fs.existsSync(schemaFilePath)) {
            exportStatements += `export * from './${destination}/schema';\n`;
        }
    });

    fs.writeFileSync(indexFilePath, exportStatements);
    console.log('index.d.ts file generated successfully!');
};

// Read all destination directories and generate types
fs.readdirSync(baseDir).forEach((destination) => {
    generateTypes(destination);
});

// Generate the index.d.ts file after generating all types
generateIndexFile();
