/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');
const { filterLanguages } = require('./common');

const destinationNameRegex = /^\w+$/;
// Path to the templates and generated files
const templatesDir = path.join(__dirname, '../templates');
const generatedDir = path.join(__dirname, '../generated');
const destinationsDir = path.join(__dirname, '../src/configurations/destinations');

// Function to read the template file and process it
function processTemplate(template, data) {
  // Create a function to evaluate the template with the data
  // eslint-disable-next-line no-new-func
  return new Function('destinations', `return \`${template}\`;`)(data);
}

function prepareDestinations(langCode) {
  return fs
    .readdirSync(destinationsDir)
    .map((destination) => {
      try {
        const destinationsFilePath = path.join(destinationsDir, destination, 'db-config.json');
        const destinationsContent = fs.readFileSync(destinationsFilePath, 'utf8');
        const destinationDef = JSON.parse(destinationsContent);
        if (!destinationDef.displayName || !destinationDef.name) {
          console.warn(`Skipping ${destination}: Missing displayName or name`);
          return null;
        }
        if (!destinationNameRegex.test(destinationDef.name)) {
          console.warn(`Skipping ${destination}: Invalid name`);
          return null;
        }
        return destinationDef;
      } catch (err) {
        console.error(`Error processing ${destination}:`, err.message);
        return null;
      }
    })
    .filter(Boolean)
    .filter((destination) => filterLanguages(destination, langCode))
    .map((destination) => ({
      name: destination.name,
      displayName: destination.displayName,
    }));
}

// Function to get the language code from the template file name
// Format: <template-name>.<lang-code>.template
function getLangCode(templateFileName) {
  const parts = templateFileName.split('.');
  if (parts.length === 3) {
    return parts[1];
  }
  throw new Error(`Invalid template file name: ${templateFileName}`);
}

// Function to read and process templates in the templates folder
function generateFiles() {
  // Ensure the 'generated' directory exists
  if (!fs.existsSync(generatedDir)) {
    fs.mkdirSync(generatedDir);
  }
  // Read all files in the templates directory
  fs.readdirSync(templatesDir)
    .filter((file) => file.endsWith('.template'))
    .forEach((file) => {
      try {
        const filePath = path.join(templatesDir, file);

        const destinations = prepareDestinations(getLangCode(file));

        // Read the content of the template file
        const templateContent = fs.readFileSync(filePath, 'utf8');

        // Process the template with the destinations data
        const output = processTemplate(templateContent, destinations);

        // Generate the output filename by removing the '.template' extension
        const outputFilePath = path.join(generatedDir, file.replace('.template', ''));

        // Write the generated content to the output file
        fs.writeFileSync(outputFilePath, output);
        console.log(`Generated: ${outputFilePath}`);
      } catch (err) {
        console.error(`Error processing ${file}:`, err.message);
      }
    });
}

// Generate the files
generateFiles();
